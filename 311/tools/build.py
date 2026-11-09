"""Restore the exposed Ponytail fringe and seat the tie around the gathered bundle."""
from hashlib import sha256
import json
from pathlib import Path
import sys

from mathutils import Vector
from mathutils.geometry import convex_hull_2d
import numpy as np

REV = Path(__file__).resolve().parents[1]
ROOT = REV.parent
OUT = REV/"assets"
sys.path.insert(0,str(ROOT/"310/tools"))
import knit
from fit import accessor, triangles, tree

from tailor import compact

updos = knit.updos
read_glb, write_glb = updos.read_glb, updos.write_glb
ANGLES = np.linspace(0.,2*np.pi,72,endpoint=False)
DIRECTIONS = np.column_stack((np.cos(ANGLES),np.sin(ANGLES)))


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(path,data):
    path.write_text(json.dumps(data,indent=2)+"\n",encoding="utf8",newline="\n")


def front_parts(doc,data,match):
    for node,rot,shift in updos.node_transforms(doc):
        if "mesh" not in node or match not in node["name"]:
            continue
        for primitive in doc["meshes"][node["mesh"]]["primitives"]:
            attr = primitive["attributes"]
            pos = updos.vectors(doc,data,attr["POSITION"])
            normal = updos.vectors(doc,data,attr["NORMAL"])
            uv = accessor(doc,data,attr["TEXCOORD_0"],2)
            face = triangles(doc,data,primitive["indices"])
            yield pos,normal,uv,face,doc["accessors"][attr["POSITION"]],rot,shift


def tuck_at_shell(points,hat):
    """Remove actual shell breakthroughs. Points below the cuff keep their shape."""
    x,y,z = points.T
    theta = np.arctan2(x,z-knit.CENTER[2])
    hem = knit.old.cap_ring(theta,0.)[:,1]
    pressure = np.zeros(len(points))
    for i in np.flatnonzero(y>hem+.0006):
        a = theta[i]
        outward = np.array([np.sin(a),0.,np.cos(a)])
        origin = np.array([0.,y[i],knit.CENTER[2]])+.62*outward
        hit = hat.ray_cast(origin,-outward,.62)[0]
        if hit is not None and (np.asarray(hit)-origin)@outward>-.58:
            pressure[i] = max(0.,float((points[i]-np.asarray(hit))@outward)+.0015)
    adjusted = points.copy()
    adjusted[:,0] -= pressure*np.sin(theta)
    adjusted[:,2] -= pressure*np.cos(theta)
    return adjusted,pressure


def original_fringe(hair_fits,rows):
    pony = read(ROOT/"309/sources.json")["ponytail"]
    fits = hair_fits["Feminine"]["ponytail"]["fits"]["beanie"]
    result = {}
    for finish in ("default","ombre"):
        covered,bare = (ROOT/pony[finish][key] for key in ("covered","bare"))
        hat = updos.surface(ROOT/rows["beanie/"+finish]["headgear"])
        doc,data = read_glb(covered)
        original = [(pos@rot.T+shift,normal@rot.T,uv)
                    for pos,normal,uv,_,_,rot,shift in front_parts(*read_glb(bare),"adjustable front")]
        base,normals_bare,coords = [np.concatenate(values) for values in zip(*original,strict=True)]
        pos,nor,uv,face,bounds,rot,shift = next(front_parts(doc,data,"front locks222"))
        prior = pos@rot.T+shift
        points,original_normals = np.empty_like(prior),np.empty_like(prior)
        for side in (-1,1):
            left,right = [np.flatnonzero(q[:,0]*side>0.) for q in (base,prior)]
            src = left[np.lexsort((coords[left,1],coords[left,0]))]
            dst = right[np.lexsort((uv[right,1],uv[right,0]))]
            assert np.array_equal(coords[src],uv[dst]),finish
            points[dst],original_normals[dst] = base[src],normals_bare[src]
        adjusted,press = tuck_at_shell(points,hat)
        touched = press>1e-8
        if touched.any():
            adjacent = np.zeros(len(adjusted),dtype=bool)
            adjacent[face[touched[face].any(1)]] = True
            actual = normals(adjusted,face)
            original_normals[adjacent] = actual[adjacent]
        pos[:] = (adjusted-shift)@rot
        nor[:] = original_normals@rot
        bounds.update(min=pos.min(0).tolist(),max=pos.max(0).tolist())
        target = OUT/f"ponytail-beanie-fringe-{finish}.glb"
        write_glb(target,doc,data)
        fits[finish] = "./assets/"+target.name
        _,residual = tuck_at_shell(adjusted,hat)
        assert residual.max()<.001, (finish,residual.max())
        result[finish] = {"bareFringe":pony[finish]["bare"],"vertices":len(press),
                          "verticesTuckedAtShell":int(touched.sum()),"maxInwardShift":float(press.max())}
        print("fringe",finish,result[finish],flush=True)
    return result


def normalize(v):
    return v/np.linalg.norm(v)


def rounded_bundle(doc,data,read_path=True):
    rails, all_triangles = [],[]
    tie = None
    for node,rot,shift in updos.node_transforms(doc):
        if "mesh" not in node:
            continue
        name = node["name"]
        for primitive in doc["meshes"][node["mesh"]]["primitives"]:
            attr = primitive["attributes"]
            pos = updos.vectors(doc,data,attr["POSITION"])@rot.T+shift
            if "tie220" in name:
                tie = node,primitive,pos.mean(0),rot,shift
            if "rounded tail220" not in name:
                continue
            if not read_path:
                rails.append(pos)
                continue
            uv = accessor(doc,data,attr["TEXCOORD_0"],2)
            ring = np.rint(uv[:,0]*96).astype(int)
            assert np.allclose(uv[:,0],ring/96,atol=1e-6)
            rails.append(np.stack([pos[ring==r].mean(0) for r in range(97)]))
            indices = triangles(doc,data,primitive["indices"])
            all_triangles.append(pos[indices[ring[indices].max(axis=1)<=26]])
    assert tie and len(rails)==5
    return (np.mean(rails,axis=0),np.concatenate(all_triangles),tie) if read_path else (rails,tie)


def cross(a,b):
    return a[...,0]*b[...,1]-a[...,1]*b[...,0]


def section_radius(tail,axial):
    """Trace the gathered section, then ease around the outside of its locks."""
    points = []
    for i,j in [(0,1),(1,2),(2,0)]:
        a,b = tail[:,i],tail[:,j]
        cut = (a[:,2]>=axial)!=(b[:,2]>=axial)
        a,b = a[cut],b[cut]
        u = (axial-a[:,2])/(b[:,2]-a[:,2])
        points.extend(a[:,:2]+(b[:,:2]-a[:,:2])*u[:,None])
    if len(points)<5:
        raise ValueError("Tie plane misses the gathered hair")
    hull = np.array(points)[convex_hull_2d([Vector(v) for v in points])]
    edges = np.roll(hull,-1,axis=0)-hull
    d = DIRECTIONS[:,None,:]
    div = cross(d,edges)
    with np.errstate(divide="ignore",invalid="ignore"):
        radius = cross(hull,edges)/div
        edge_t = cross(hull,d)/div
    hits = np.max(np.where((edge_t>=-1e-8)&(edge_t<=1+1e-8)&(radius>0)&np.isfinite(radius),
                          radius,0),axis=1)
    if hits.min()<.007:
        raise ValueError("Tie plane is too close to the hair root")
    smooth = sum(np.roll(hits,i)*weight for i,weight in [(-2,1),(-1,2),(0,3),(1,2),(2,1)])/9
    return np.maximum(smooth,hits-.0005)


def elastic(rail,faces,index,halfwidth):
    origin = rail[index]
    axis = normalize(rail[index+2]-rail[index-2])
    across = normalize(np.array([1.,0.,0.])-axis*axis[0])
    frame = np.column_stack((across,np.cross(axis,across),axis))
    tail = (faces-origin)@frame
    vertices = []
    profile = np.linspace(0,2*np.pi,12,endpoint=False)
    for angle in profile:
        z = halfwidth*np.sign(np.sin(angle))*abs(np.sin(angle))**.63
        r = section_radius(tail,z) + .0013 + .0041*np.sign(np.cos(angle))*abs(np.cos(angle))**.65
        vertices.extend(origin+np.column_stack((r[:,None]*DIRECTIONS,np.full(len(r),z)))@frame.T)
    indices = []
    n = len(ANGLES)
    for row in range(len(profile)):
        next_row = (row+1)%len(profile)
        for i in range(n):
            j = (i+1)%n
            a,b,c,d = row*n+i,row*n+j,next_row*n+j,next_row*n+i
            indices.extend([(a,b,c),(a,c,d)])
    return np.array(vertices),np.array(indices),origin,axis


def normals(points,faces):
    a,b,c = points[faces].transpose(1,0,2)
    result = np.zeros_like(points)
    direction = np.cross(b-a,c-a)
    for ids in faces.T:
        np.add.at(result,ids,direction)
    return result/np.maximum(np.linalg.norm(result,axis=1,keepdims=True),1e-12)


def append(doc,data,array,dtype,kind,target):
    values = np.asarray(array,dtype=dtype)
    payload = values.tobytes()
    view = len(doc["bufferViews"])
    doc["bufferViews"].append({"buffer":0,"byteOffset":len(data),"byteLength":len(payload),"target":target})
    data.extend(payload)
    data.extend(b"\0"*((-len(data))%4))
    spec = {"bufferView":view,"componentType":5126 if kind=="VEC3" else 5123,
            "count":len(values),"type":kind}
    if kind=="VEC3":
        spec.update(min=values.min(0).tolist(),max=values.max(0).tolist())
    doc["accessors"].append(spec)
    return len(doc["accessors"])-1


def retie(source,target,headgear,scalp,default):
    doc,data = read_glb(source)
    if source==default:
        rail,tail,tie = rounded_bundle(doc,data)
    else:
        base = read_glb(default)
        rail,tail,_ = rounded_bundle(*base)
        a,_ = rounded_bundle(*base,read_path=False)
        b,tie = rounded_bundle(doc,data,read_path=False)
        for old,new in zip(a,b,strict=True):
            old,new = [pts[np.lexsort((pts[:,2],pts[:,1],pts[:,0]))] for pts in (old,new)]
            assert np.allclose(old,new,atol=2e-6), source
    _,primitive,old_center,rot,shift = tie
    cloth = updos.surface(headgear) if headgear else None
    cap = updos.surface(scalp,lambda n:"roots220" in n)
    old_nearest = int(np.argmin(np.linalg.norm(rail-old_center,axis=1)))
    # Choose the first fully gathered section outside the scalp. Wear the
    # elastic around the departure tangent, with a little space below hats.
    trials = [(i,w) for w in (.0105,.009,.0075)
              for i in range(max(4,old_nearest),max(16,old_nearest+10))]
    for i,w in trials:
        try:
            points,faces,center,axis = elastic(rail,tail,i,w)
        except ValueError:
            continue
        band = tree(points,faces)
        if cloth is not None and band.overlap(cloth):
            continue
        if cap is not None and band.overlap(cap):
            continue
        break
    else:
        raise ValueError("No clear gathered elastic fit for "+source.name)
    attachment = updos.surface(source,lambda n:"rounded tail220" in n)
    contact = len(band.overlap(attachment))
    assert contact, source
    n = normals(points,faces)
    local = (points-shift)@rot
    primitive["attributes"] = {
        "POSITION":append(doc,data,local,"<f4","VEC3",34962),
        "NORMAL":append(doc,data,n@rot,"<f4","VEC3",34962),
    }
    primitive["indices"] = append(doc,data,faces.ravel(),"<u2","SCALAR",34963)
    material = doc["materials"][primitive["material"]]
    pbr = material["pbrMetallicRoughness"]
    pbr.update(baseColorFactor=[.033,.024,.021,1.],roughnessFactor=.62,metallicFactor=0.)
    spec = material.get("extensions",{}).get("KHR_materials_specular")
    if spec is not None:
        spec["specularFactor"] = .31
    doc.setdefault("images",[])
    data = compact(doc,data)
    if not doc["images"]:
        del doc["images"]
    write_glb(target,doc,data)
    return {"section":i/96,"width":2*w,"center":center.tolist(),"axis":axis.tolist(),"bundleContacts":contact}


def main(rows):
    art,hair_fits = (json.loads((ROOT/"310"/file).read_text().replace('"./assets/','"../310/assets/'))
                     for file in ("art.json","hair-fits.json"))
    record = {"fringe":original_fringe(hair_fits,rows),"ties":{}}
    fits = hair_fits["Feminine"]["ponytail"]["fits"]
    for head in ("beanie","none","cap","headband","ears"):
        default = rows[head+"/default"]
        geometry_source = ROOT/default.get("hairLengths",default["hair"])
        for finish in ("default","ombre"):
            parts = rows[head+"/"+finish]
            source = ROOT/parts.get("hairLengths",parts["hair"])
            hat = ROOT/parts["headgear"] if "headgear" in parts else None
            scalp = REV/fits["beanie"][finish] if head=="beanie" else source
            name = f"ponytail-{head}-{finish}.glb"
            info = retie(source,OUT/name,hat,scalp,geometry_source)
            record["ties"][head+"/"+finish] = info
            if head=="beanie":
                art["beanie"]["Feminine"]["ponytail"]["tail"][finish] = "./assets/"+name
            else:
                fits[head][finish] = "./assets/"+name
            print(head,finish,info,flush=True)
    record["assets"] = {path.name:sha256(path.read_bytes()).hexdigest() for path in sorted(OUT.glob("*.glb"))}
    write(REV/"art.json",art)
    write(REV/"hair-fits.json",hair_fits)
    write(REV/"verification/fit.json",record)


if __name__=="__main__":
    main(read(Path(sys.argv[-1])))
