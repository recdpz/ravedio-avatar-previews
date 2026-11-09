"""Refit the Ponytail to a right-side gather and soften the beanie fringe."""
from dataclasses import dataclass
import json
from hashlib import sha256
import importlib.util
import math
from pathlib import Path
import sys

import numpy as np

REV = Path(__file__).resolve().parents[1]
ROOT = REV.parent
spec = importlib.util.spec_from_file_location("pony311",ROOT/"311/tools/build.py")
previous = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous)
knit,updos = previous.knit,previous.updos
read,write = previous.read,previous.write
read_glb,write_glb,tree = previous.read_glb,previous.write_glb,previous.tree
from fit import accessor, geometry, warp_normals
from plaits import smooth_profile

CENTER = knit.CENTER
# X points to screen right when viewed from the front.
RIGHT = {"none":.082,"ears":.082,"beanie":.119,"cap":.060,"headband":.064,
         "bucket":.080,"cowboy":.080}


def smooth(low,high,value):
    return knit.old.smooth(low,high,value)


def angles(points):
    d = points-CENTER
    return np.arctan2(d[:,0],-d[:,2])


def spin(points,angle):
    d = points-CENTER
    c,s = np.cos(angle),np.sin(angle)
    return CENTER+np.column_stack((d[:,0]*c-d[:,2]*s,d[:,1],d[:,0]*s+d[:,2]*c))


def unit(d):
    return d/np.maximum(np.linalg.norm(d,axis=-1,keepdims=True),1e-9)


@dataclass
class Mesh:
    name: str
    bounds: dict
    pos: np.ndarray
    nor: np.ndarray
    rotation: np.ndarray
    offset: np.ndarray
    faces: np.ndarray

    @property
    def world(self):
        return self.pos@self.rotation.T+self.offset

    def update(self,points,normals):
        self.pos[:] = (points-self.offset)@self.rotation
        self.nor[:] = normals@self.rotation
        self.bounds.update(min=self.pos.min(0).tolist(),max=self.pos.max(0).tolist())


def joined(parts):
    points,faces = [],[]
    count = 0
    for mesh,vertices in parts:
        points.append(vertices)
        faces.append(mesh.faces+count)
        count += len(vertices)
    return tree(np.concatenate(points),np.concatenate(faces))


def is_tie(mesh):
    return any(part in mesh.name for part in ("tie220","ties226","low gathered elastic235"))


def is_tail(mesh):
    return any(part in mesh.name for part in ("rounded tail220","Hair / chestnut226","closed-hat low pony235"))


def crown_progress(crown):
    doc,data = crown
    node = next(n for n in doc["nodes"] if "mesh" in n and "roots220" in n["name"])
    attr = doc["meshes"][node["mesh"]]["primitives"][0]["attributes"]
    # Ombre uses its own color lookup. The authoring UVs remain in UV1.
    u = accessor(doc,data,attr.get("TEXCOORD_1",attr["TEXCOORD_0"]),2)[:,0].copy()
    assert len(np.unique(u))==85
    return u


def gather_motion(points,anchor,new_anchor,progress):
    a,b = unit(anchor-CENTER),unit(new_anchor-CENTER)
    bend = np.cross(a,b)
    if progress is None or np.linalg.norm(bend)<1e-9:
        return points.copy(),np.zeros(len(points))
    axis = unit(bend)
    angle = math.atan2(np.linalg.norm(bend),a@b)
    weight = smooth(.035,.96,progress)
    q = points-CENTER
    c,s = np.cos(angle*weight),np.sin(angle*weight)
    moved = q*c[:,None]+np.cross(axis,q)*s[:,None]+np.outer(q@axis,axis)*(1-c)[:,None]
    return CENTER+moved,weight


def root_cover(points,anchor,new_anchor,progress):
    """Carry the upper swept locks along their own length and seat their valleys."""
    turned,weight = gather_motion(points,anchor,new_anchor,progress)
    direction = unit(turned-CENTER)
    new_root = unit(new_anchor-CENTER)
    near = 1-smooth(.24,.48,np.linalg.norm(direction-new_root,axis=1))
    depth = np.linalg.norm(turned-CENTER,axis=1)
    lift = np.maximum(0.,.3882-depth)*near
    return turned+direction*lift[:,None],np.maximum(weight,smooth(0.,.004,lift))


def coverage(tree_,base,anchor):
    """Sample the gathered patch against the actual skin, looking down its normal."""
    n = unit(anchor-CENTER)
    x = unit(np.array([1.,0.,0.])-n*n[0])
    y = np.cross(n,x)
    misses,clearance = 0,float("inf")
    for radius in np.linspace(0,.078,11):
        for angle in np.linspace(0,2*np.pi,36,endpoint=False):
            direction = unit(n+radius/.384*(np.cos(angle)*x+np.sin(angle)*y))
            origin = CENTER+.73*direction
            hair = tree_.ray_cast(origin,-direction,.55)[-1]
            skin = base.ray_cast(origin,-direction,.55)[-1]
            assert skin is not None
            if hair is None:
                misses += 1
            else:
                gap = skin-hair
                clearance = min(clearance,gap)
                misses += int(gap<-.0003)
    return misses,round(clearance,6)


def gather_loop(vertices,faces):
    """Find the small open ring in the crown where the hair is gathered."""
    _,first,weld = np.unique(np.round(vertices,5),axis=0,return_index=True,return_inverse=True)
    indices = weld[faces]
    edges = np.concatenate([indices[:,[0,1]],indices[:,[1,2]],indices[:,[2,0]]])
    _,edge_map,counts = np.unique(np.sort(edges,axis=1),axis=0,return_inverse=True,return_counts=True)
    boundary = {int(a):int(b) for a,b in edges[counts[edge_map]==1]}
    loops = []
    while boundary:
        start = next(iter(boundary))
        loop,node = [start],boundary.pop(start)
        while node!=start and node in boundary:
            loop.append(node)
            node = boundary.pop(node)
        if node==start and len(loop)>8:
            loops.append(first[loop])
    return min(loops,key=lambda ids:np.linalg.norm(np.ptp(vertices[ids],axis=0)))


def add_float(doc,data,array,kind):
    values = np.asarray(array,dtype="<f4")
    if kind=="VEC3":
        return previous.append(doc,data,values,"<f4",kind,34962)
    view = len(doc["bufferViews"])
    doc["bufferViews"].append({"buffer":0,"byteOffset":len(data),"byteLength":values.nbytes,"target":34962})
    data.extend(values.tobytes())
    doc["accessors"].append({"bufferView":view,"componentType":5126,"count":len(values),"type":kind})
    return len(doc["accessors"])-1


def close_gather(crown,root,perimeter):
    """Close the inner hair ring using its own edge colors and normals."""
    doc,source_data = crown
    data = bytearray(source_data)
    node = next(n for n in doc["nodes"] if "mesh" in n and "roots220" in n["name"])
    primitives = doc["meshes"][node["mesh"]]["primitives"]
    source = primitives[0]
    border = root.world[perimeter]
    pole_direction = unit(border.mean(0)-CENTER)
    pole_radius = max(.3892,np.linalg.norm(border-CENTER,axis=1).mean())
    pole = CENTER+pole_direction*pole_radius
    steps = (0.,.29,.58,.82)
    n = len(border)
    rings = []
    for step in steps:
        direction = unit(border*(1-step)+pole*step-CENTER)
        radius = np.linalg.norm(border-CENTER,axis=1)*(1-step)+pole_radius*step
        rings.append(CENTER+direction*radius[:,None])
    points = np.vstack([*rings,pole])
    faces = []
    for row in range(len(steps)):
        for i in range(n):
            a,b = row*n+i,row*n+(i+1)%n
            if row==len(steps)-1:
                faces.append((b,a,len(points)-1))
            else:
                faces.extend([(b,a,a+n),(b,a+n,b+n)])
    faces = np.asarray(faces)
    a,b,c = points[faces[0]]
    if np.cross(b-a,c-a)@(a-CENTER)<0.:
        faces = faces[:,[0,2,1]]
    normal = previous.normals(points,faces)
    normal[:n] = root.nor[perimeter]@root.rotation.T
    attrs = {
        "POSITION":add_float(doc,data,(points-root.offset)@root.rotation,"VEC3"),
        "NORMAL":add_float(doc,data,normal@root.rotation,"VEC3"),
    }
    for name,index in source["attributes"].items():
        if name in attrs:
            continue
        kind = doc["accessors"][index]["type"]
        dims = int(kind[-1])
        assert doc["accessors"][index]["componentType"]==5126, (name,kind)
        edge = accessor(doc,data,index,dims)[perimeter].copy()
        mean = edge.mean(0)
        values = np.vstack([*(edge*(1-step)+mean*step for step in steps),mean])
        attrs[name] = add_float(doc,data,values,kind)
    primitives.append({"attributes":attrs,"material":source["material"],
                       "indices":previous.append(doc,data,faces.ravel(),"<u2","SCALAR",34963)})
    doc["buffers"][0]["byteLength"] = len(data)
    return points,faces,data


def rear_wrap(points,anchor,delta):
    theta = float(angles(anchor[None,:])[0])
    difference = np.arctan2(np.sin(angles(points)-theta),np.cos(angles(points)-theta))
    rear = 1-smooth(.72,2.17,np.abs(difference))
    return spin(points,delta*rear)


def turn_fringe(crown,uncovered,default_crown,hat):
    """Lead the strand down under the cuff, then release into its original curl."""
    src = [(p@r.T+o,n@r.T,uv) for p,n,uv,_,_,r,o in
           previous.front_parts(*read_glb(uncovered),"adjustable front")]
    original,original_normals,uvs = (np.concatenate(values) for values in zip(*src,strict=True))
    pos,nor,uv,faces,bounds,rot,offset = next(previous.front_parts(*crown,"front locks222"))
    existing = pos@rot.T+offset
    default_pos,_,default_uv,_,_,r,o = next(previous.front_parts(*read_glb(default_crown),"front locks222"))
    canonical = default_pos@r.T+o
    a,b = [np.lexsort((p[:,2],p[:,1],p[:,0])) for p in (canonical,existing)]
    assert np.allclose(canonical[a],existing[b],atol=2e-6)
    parameter = np.empty_like(uv)
    parameter[b] = default_uv[a]
    moved,shading = np.empty_like(existing),np.empty_like(existing)
    peaks = []
    for side in (-1,1):
        a,b = (np.flatnonzero(g[:,0]*side>0.) for g in (original,existing))
        a = a[np.lexsort((uvs[a,1],uvs[a,0]))]
        b = b[np.lexsort((parameter[b,1],parameter[b,0]))]
        assert np.array_equal(uvs[a],parameter[b])
        points = original[a]
        u = uvs[a,0]
        count = int(round(1/(np.unique(u)[1]-np.unique(u)[0])))
        rings = np.rint(u*count).astype(int)
        centers = np.array([points[rings==r].mean(0) for r in range(count+1)])
        x,y,z = centers.T
        theta = np.arctan2(x,z-CENTER[2])
        relative = y-knit.old.cap_ring(theta,0.)[:,1]
        _,penetration = previous.tuck_at_shell(points,hat)
        span = float(penetration.max())
        # Same displacement across each cross-section keeps the root rounded.
        knots = np.array([-.089,-.069,-.048,-.028,-.012,0.,.013,.028,.056,.070])
        weight = np.array([0.,.10,.41,.70,.90,1.06,.96,.70,.02,0.])
        grid = np.linspace(knots[0],knots[-1],360)
        guide = smooth_profile(knots,weight[:,None],grid,.005)[:,0]
        amount = np.interp(relative,grid,guide,left=0.,right=0.)*span
        amount = np.minimum(amount,np.maximum(0.,np.hypot(x,z-CENTER[2])-knit.head_radius(y)+.001))
        radial = np.column_stack((np.sin(theta),np.zeros(len(theta)),np.cos(theta)))
        shaped = points-(amount[:,None]*radial)[rings]
        shaped,_ = previous.tuck_at_shell(shaped,hat)
        moved[b],shading[b] = shaped,original_normals[a]
        peaks.append(float(amount.max()))
    affected = np.linalg.norm(moved-existing,axis=1)>1e-7
    # Match the sculpted strand shading at the lower, unaffected lengths.
    face_normals = previous.normals(moved,faces)
    shading[affected] = face_normals[affected]
    pos[:] = (moved-offset)@rot
    nor[:] = shading@rot
    bounds.update(min=pos.min(0).tolist(),max=pos.max(0).tolist())
    _,residual = previous.tuck_at_shell(moved,hat)
    assert residual.max()<.001, residual.max()
    return {"maxCuffSeat":max(peaks),"maxRemainingBreach":float(residual.max())}


def refit(key,parts,uncovered,default_crown,target_x,output_dir,forced_pose=None):
    head,finish = key.split("/")
    split = "hairLengths" in parts
    source = ROOT/parts["hair"]
    crown = read_glb(source)
    tail = read_glb(ROOT/parts["hairLengths"]) if split else crown
    root_parts = [m for m in map(lambda p:Mesh(*p),geometry(*crown)) if "roots220" in m.name]
    source_parts = [Mesh(*p) for p in geometry(*tail)]
    bundle = [(m,m.world) for m in source_parts if is_tail(m)]
    elastic = [(m,m.world) for m in source_parts if is_tie(m)]
    assert len(root_parts)==1 and len(elastic)==1 and bundle,key
    root = root_parts[0]
    roots = root.world
    progress = crown_progress(crown) if head in {"none","ears","cap"} else None
    anchor = elastic[0][1].mean(0)
    theta = float(angles(anchor[None,:])[0])
    radius = np.linalg.norm((anchor-CENTER)[[0,2]])
    desired = math.asin(target_x/radius)-theta
    n = max(1,int(math.ceil(abs(desired)/.055)))
    angles_to_try = np.linspace(desired,0,n+1)
    pitches = (0.,-.032,-.064,-.096,-.128,-.16,-.192) if head=="bucket" else (0.,)
    poses = [forced_pose] if forced_pose is not None else [
        (yaw,pitch) for pitch in pitches for yaw in angles_to_try
    ]
    hat = updos.surface(ROOT/parts["headgear"]) if "headgear" in parts else None
    drape = read_glb(ROOT/parts["headgear"]) if head=="headband" else None
    cloth_parts = [Mesh(*m) for m in geometry(*drape)] if drape else []
    baseline = joined(bundle+elastic)
    before_hat = len(baseline.overlap(hat)) if hat else 0
    root_tree = joined([(root,roots)])
    before_join = len(joined(bundle).overlap(root_tree))
    options = []
    for delta,pitch in poses:
        rotation = updos.axis_rotation("x",pitch)
        def carry(points):
            return spin(CENTER+(points-CENTER)@rotation.T,delta)

        mapped = carry(anchor[None,:])[0]
        new_root,normal_weight = root_cover(roots,anchor,mapped,progress)
        crown_tree = joined([(root,new_root)])
        carried = [(m,carry(p)) for m,p in bundle]
        carried_tie = [(m,carry(p)) for m,p in elastic]
        tail_tree = joined(carried+carried_tie)
        fitted_cloth = (joined([(m,rear_wrap(m.world,anchor,delta)) for m in cloth_parts])
                        if drape else hat)
        hat_hits = len(tail_tree.overlap(fitted_cloth)) if fitted_cloth else 0
        if hat_hits>before_hat:
            continue
        join = len(joined(carried).overlap(crown_tree))
        if join<max(1,min(12,before_join)):
            continue
        # As in 311, elastic is seated on the bundle and clear of the hat.
        if fitted_cloth and joined(carried_tie).overlap(fitted_cloth):
            continue
        candidate = (delta,pitch,hat_hits,join,new_root,normal_weight,crown_tree,carried,carried_tie)
        options.append(candidate)
        if not hat_hits and abs(delta-desired)<.055:
            break
    if not options:
        raise ValueError("No clear Ponytail route for "+key)
    delta,pitch,hat_hits,join,new_root,normal_weight,crown_tree,carried,carried_tie = min(
        options,key=lambda result:(result[2],abs(result[0]-desired),abs(result[1])))
    rotation = updos.axis_rotation("x",pitch)
    mapped = spin(CENTER+(anchor[None,:]-CENTER)@rotation.T,delta)[0]
    base = updos.surface(ROOT/parts["base"],lambda n:"soft oval head" in n)
    assert base is not None
    before = coverage(root_tree,base,anchor)
    old_normals = root.nor@root.rotation.T
    normals = previous.normals(new_root,root.faces)
    root.update(new_root,unit(old_normals+(normals-old_normals)*normal_weight[:,None]))
    for mesh,p in carried+carried_tie:
        normal = spin(CENTER+mesh.nor@mesh.rotation.T@rotation.T,delta)-CENTER
        mesh.update(p,normal)
    after = coverage(crown_tree,base,mapped)
    if head in {"none","ears"}:
        perimeter = gather_loop(roots,root.faces)
        points,faces,data = close_gather(crown,root,perimeter)
        crown = crown[0],data
        capped = tree(np.vstack((root.world,points)),np.vstack((root.faces,faces+len(roots))))
        after = coverage(capped,base,mapped)
        assert after[0]==0, (key,after)
    result = {"yawDegrees":round(math.degrees(delta),3),"pitchDegrees":round(math.degrees(pitch),3),"fromX":round(float(anchor[0]),5),
              "toX":round(float(mapped[0]),5),"oldHatContacts":before_hat,"hatContacts":hat_hits,
              "bundleToCrownContacts":join,"rootCoverageBefore":before,"rootCoverageAfter":after}
    if drape and finish=="default":
        for m in cloth_parts:
            points = m.world
            warp = lambda p:rear_wrap(p,anchor,delta)
            m.update(warp(points),warp_normals(warp,points,m.nor@m.rotation.T))
        write_glb(output_dir/"ponytail-bandana.glb",*drape)
    if split:
        result["fringe"] = turn_fringe(crown,uncovered,default_crown,hat)
        output = output_dir/f"ponytail-beanie-fringe-{finish}.glb"
        write_glb(output,*crown)
        tail_name = f"ponytail-beanie-{finish}.glb"
        write_glb(output_dir/tail_name,*tail)
        return output.name,tail_name,result,(float(delta),float(pitch))
    if head=="cap":
        # The compressed radial roots in the cap window catch a pin-point
        # reflection beside the elastic. Give this covered crown softer sheen.
        doc,_ = crown
        node = next(n for n in doc["nodes"] if "mesh" in n and "roots220" in n["name"])
        primitive = doc["meshes"][node["mesh"]]["primitives"][0]
        material = doc["materials"][primitive["material"]]
        material["pbrMetallicRoughness"]["roughnessFactor"] = .38
        material["extensions"]["KHR_materials_clearcoat"]["clearcoatFactor"] = .22
    output = output_dir/f"ponytail-{head}-{finish}.glb"
    write_glb(output,*crown)
    return output.name,None,result,(float(delta),float(pitch))


def main(rows, *, revision=REV, targets=RIGHT):
    output_dir = revision/"assets"
    art,hair_fits = (json.loads((ROOT/"311"/file).read_text().replace('"./assets/','"../311/assets/'))
                    for file in ("art.json","hair-fits.json"))
    fits = hair_fits["Feminine"]["ponytail"]["fits"]
    receipt = {}
    for head,target_x in targets.items():
        delta = None
        for finish in ("default","ombre"):
            key = head+"/"+finish
            source = ROOT/rows["none/default"]["hair"]
            reference = ROOT/rows["beanie/default"]["hair"]
            hair,tail,receipt[key],delta = refit(key,rows[key],source,reference,target_x,output_dir,delta)
            fits[head][finish] = "./assets/"+hair
            if tail:
                art["beanie"]["Feminine"]["ponytail"]["tail"][finish] = "./assets/"+tail
            print(key,receipt[key],flush=True)
    bandanas = json.loads((ROOT/"303/bandana-fits.json").read_text().replace('"./assets/','"../303/assets/'))
    bandana = bandanas["Feminine-ponytail"]
    bandana["headgear"] = "./assets/ponytail-bandana.glb"
    bandana["headgear_sha256"] = sha256((output_dir/"ponytail-bandana.glb").read_bytes()).hexdigest()
    bandana["fittedHair"] = {color:fits["headband"][color] for color in ("default","ombre")}
    bandana["fittedHairSha256"] = {color:sha256((revision/path).read_bytes()).hexdigest()
                                 for color,path in bandana["fittedHair"].items()}
    old_hat = updos.surface(ROOT/rows["headband/default"]["headgear"])
    new_hat = updos.surface(output_dir/"ponytail-bandana.glb")
    clip = output_dir/"ponytail-bandana-sprout.glb"
    knit.seat_sprout(revision/bandana["sprout"],clip,old_hat,new_hat)
    bandana["sprout"] = "./assets/"+clip.name
    bandana["sprout_sha256"] = sha256(clip.read_bytes()).hexdigest()
    write(revision/"art.json",art)
    write(revision/"hair-fits.json",hair_fits)
    write(revision/"bandana-fits.json",bandanas)
    write(revision/"verification/fit.json",{"fits":receipt,"assets":{
        p.name:sha256(p.read_bytes()).hexdigest() for p in sorted(output_dir.glob("*.glb"))}})


if __name__=="__main__":
    main(read(Path(sys.argv[-1])))
