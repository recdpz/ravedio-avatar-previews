"""Build smooth, fitted bandanas around the undeformed 270 hairstyles."""
import json
import math
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

REV = Path(__file__).resolve().parents[1]
ROOT = REV.parent
OUT = REV / "assets"
sys.path.insert(0, str(ROOT / "270/tools"))
from bake_catalogue import NEW_CENTER as CENTER, node_transforms, read_glb, sha, vectors

CAT = json.loads((ROOT / "263/catalogue263.json").read_text(encoding="utf8"))
FIT = json.loads((ROOT / "270/assets.json").read_text(encoding="utf8"))
UP = np.array([0., 1., 0.])
FRONT = np.array([0., 0., 1.])


def unit(p):
    return p / np.linalg.norm(p, axis=-1, keepdims=True)


def ease(t):
    t = np.clip(t, 0, 1)
    return t*t*(3 - 2*t)


def ordinary(path):
    return (ROOT / "270" / FIT["components"][path]["path"]).resolve()


def triangles(gltf, binary, idx):
    acc = gltf["accessors"][idx]
    buf = gltf["bufferViews"][acc["bufferView"]]
    start = acc.get("byteOffset", 0) + buf.get("byteOffset", 0)
    return np.frombuffer(binary, dtype={5121:"u1",5123:"<u2",5125:"<u4"}[acc["componentType"]],
                         count=acc["count"], offset=start).reshape(-1, 3)


def surface(path, include=lambda _: True):
    g, b = read_glb(path)
    verts, faces = [], []
    for node, rot, offset in node_transforms(g):
        if "mesh" not in node or not include(node.get("name", "")):
            continue
        for p in g["meshes"][node["mesh"]]["primitives"]:
            world = vectors(g, b, p["attributes"]["POSITION"]) @ rot.T + offset
            faces.extend((triangles(g,b,p["indices"]).astype(np.int32) + len(verts)).tolist())
            verts.extend(world.tolist())
    return BVHTree.FromPolygons(verts, faces, all_triangles=True) if faces else None


def hit(tree, origin, direction):
    p, *_ = tree.ray_cast(Vector(origin), Vector(direction), 2.)
    return np.array(p) if p is not None else None


def envelope(values, loop):
    """A smoothed support surface that clears the high points of adjacent locks."""
    angular = np.pad(values, ((0,0),(3,3)), mode="wrap" if loop else "edge")
    roof = np.maximum.reduce([angular[:,i:i+values.shape[1]] - abs(3-i)*.00065
                              for i in range(7)])
    vertical = np.pad(roof, ((2,2),(0,0)), mode="edge")
    roof = np.maximum.reduce([vertical[i:i+values.shape[0]] - abs(2-i)*.00085
                              for i in range(5)])
    smooth = roof
    for axis in [0,1,1]:
        work = np.swapaxes(smooth, axis, 1)
        padded = np.pad(work, ((0,0),(2,2)), mode="wrap" if axis == 1 and loop else "edge")
        smooth = np.swapaxes(sum(w*padded[:,i:i+work.shape[1]]
                                 for i,w in enumerate([1/16,4/16,6/16,4/16,1/16])),axis,1)
    return np.maximum(values + .0057, smooth + .0066)

def male_wrap(tree, style):
    n, m = 224, 27
    u, v = np.linspace(-np.pi,np.pi,n,endpoint=False), np.linspace(0,1,m)
    direction = np.stack((np.sin(u),np.zeros(n),np.cos(u)),axis=-1)
    front_height = {"buzz":1.976,"taper":2.052,"curly-top":2.039,"afro":2.011}.get(style,2.003)
    rear = ((1-np.cos(u))/2)**2
    middle = front_height - .094*rear + .004*np.sin(u+.3) + .002*np.sin(3*u+.8)
    width = .089 - .024*rear**6 + .004*np.cos(u*2+.9)
    height = middle[None,:] + (v[:,None]-.5)*width[None,:]
    support = np.empty_like(height)
    for j,k in np.ndindex(height.shape):
        d = direction[k]
        center = CENTER.copy()
        center[1] = height[j,k]
        h = hit(tree,center+d,-d)
        r = math.sqrt(.384**2-(center[1]-CENTER[1])**2)
        support[j,k] = max(r,(h-center)@d if h is not None else r)
    radius = envelope(support,True)
    if style == "afro":
        radius += .0036
    elif style == "sidepart":
        radius += .0014
    radius += .0011*np.sin(u*5+.7)[None,:] + .0021*np.sin(v[:,None]*np.pi*1.4)**2
    points = CENTER + direction[None,:,:]*radius[:,:,None]
    points[:,:,1] = height
    uv = np.stack(np.meshgrid(np.arange(n)/n,v),axis=-1)
    return points,uv,True


def female_wrap(tree, style, pony=None):
    s = np.linspace(-1,1,145)
    v = np.linspace(0,1,97)

    def directions(u):
        az = u * (1.16 if style == "space-buns" else 1.51)
        polar = .74 + .40*np.abs(u)**1.35
        front = np.stack((np.sin(polar)*np.sin(az),np.cos(polar),np.sin(polar)*np.cos(az)),axis=-1)
        if style == "box-braids":
            front[:,:,1] += .045 * np.abs(u)**1.2
            front = unit(front)
        rear_x = .42 if pony is not None else 0
        rear = unit(np.stack((rear_x+.055*u,np.full_like(u,.31),np.full_like(u,-.95)),axis=-1))
        start = .045*ease((np.abs(u)-.84)/.16)
        t = start + (1-start)*v[:,None]
        mix = (1-t[:,:,None])*front + t[:,:,None]*rear
        if pony is not None:
            mix[:,:,0] += .16 * (1-ease((t-.73)/.24)) * ease((t-.25)/.32)
        d = unit(mix)
        if style == "space-buns":
            # Keep the crown scarf between the two buns. The front corners
            # remain broad until the fabric reaches the bun attachments.
            x = d[:,:,0]
            taper = ease((.39-d[:,:,2])/.30)
            narrowed = (1-taper)*x + taper*.31*np.tanh(x/.46)
            d[:,:,1:] *= np.sqrt((1-narrowed*narrowed)/(1-x*x))[:,:,None]
            d[:,:,0] = narrowed
        return d

    u = np.broadcast_to(s,(len(v),len(s))).copy()
    if pony is not None:
        # Leave a sewn edge beside the tie, based on the actual ponytail
        # footprint. Cutting the scarf beside the tie avoids a hole in the crown.
        lower = np.full(len(v),-1.)
        initial = directions(u)
        for j,k in np.ndindex(u.shape):
            d = initial[j,k]
            if hit(pony,CENTER+1.04*d,-d) is not None:
                lower[j] = max(lower[j],min(.94,u[j,k]+.095))
        p = np.pad(lower,(7,7),mode="edge")
        guard = np.maximum.reduce([p[i:i+len(v)] - abs(i-7)*.036 for i in range(15)])
        smooth = np.convolve(np.pad(guard,(5,5),mode="edge"),np.ones(11)/11,mode="valid")
        left = np.maximum(guard,smooth)
        u = left[:,None] + (1-left[:,None])*(s[None,:]+1)*.5

    d = directions(u)
    radius = np.empty(d.shape[:2])
    for j,k in np.ndindex(radius.shape):
        ray = d[j,k]
        h = hit(tree,CENTER+ray,-ray)
        radius[j,k] = max(.384,(h-CENTER)@ray if h is not None else .384)
    support = envelope(radius,False)
    support += .0017*np.sin(np.pi*v[:,None])*np.sin(u*6.0+v[:,None]*2)
    points = CENTER + d*support[:,:,None]
    uv = np.stack(((u*(1-.92*v[:,None])+1)*.5,np.broadcast_to(v[:,None],radius.shape)),axis=-1)
    return points,uv,False

def texture(name):
    mat=bpy.data.materials.new("Headwear / bandana cotton271")
    mat.use_nodes=True
    shader=mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Roughness"].default_value=.91
    shader.inputs["Specular IOR Level"].default_value=.17
    node=mat.node_tree.nodes.new("ShaderNodeTexImage")
    node.image=bpy.data.images.load(str(OUT/name), check_existing=True)
    mat.node_tree.links.new(node.outputs["Color"],shader.inputs["Base Color"])
    return mat


def mesh_grid(name, points, uv, mat, loop=False, thickness=.0027):
    rows, cols, _ = points.shape
    verts=[(float(x),float(-z),float(y)) for x,y,z in points.reshape(-1,3)]
    faces, tex = [], []
    for j in range(rows-1):
        for i in range(cols if loop else cols-1):
            k=(i+1)%cols
            faces.append((j*cols+i,j*cols+k,(j+1)*cols+k,(j+1)*cols+i))
            a,b,c,d=uv[j,i],uv[j,k].copy(),uv[j+1,k].copy(),uv[j+1,i]
            if k == 0:
                b[0]=c[0]=1
            tex.append([a,b,c,d])
    # Orient toward the outside of the head (coordinate conversion preserves handedness).
    probe = ((rows-1)//2)*(cols if loop else cols-1)+cols//2-1
    f=faces[probe]
    p,q,r=points.reshape(-1,3)[list(f[:3])]
    if np.cross(q-p,r-p) @ (p-CENTER) < 0:
        faces=[tuple(reversed(f)) for f in faces]
        tex=[list(reversed(u)) for u in tex]
    data=bpy.data.meshes.new(name)
    data.from_pydata(verts,[],faces)
    data.update()
    obj=bpy.data.objects.new(name,data)
    bpy.context.collection.objects.link(obj)
    layer=data.uv_layers.new(name="Cotton print")
    for poly,uvs in zip(data.polygons,tex):
        poly.use_smooth=True
        for index,value in zip(poly.loop_indices,uvs):
            layer.data[index].uv=value
    data.materials.append(mat)
    mod=obj.modifiers.new("Fabric thickness","SOLIDIFY")
    mod.thickness=thickness
    mod.offset=-1
    return obj


def pull_behind(tree, p, offset):
    # Keep cloth following the back of the hairstyle with a small fabric clearance.
    anchor = np.array([p[0],p[1],-.95])
    h=hit(tree,anchor,FRONT)
    out=p.copy()
    if h is not None:
        out[2]=min(out[2],h[2]-offset)
    return out


def ties(tree, anchor, mat, feminine):
    """Gather the wrap into a compact knot with two draped, supported tails."""
    n,w=30,11
    ts=np.linspace(0,1,n)
    ss=np.linspace(-1,1,w)
    for side in [-1,1]:
        # Each gather begins slightly inside the wrap and emerges from its rear seam.
        centers=[]
        for t in ts:
            p=anchor+np.array([side*((.023 if feminine else .034)*(1-t)-.013*t),
                               .004 + .005*np.sin(np.pi*t) - .014*t,
                               .003 - .020*t])
            centers.append(p)
        centers=np.array(centers)
        p=centers[:,None,:]+np.array([0,1,0])[None,None,:]*ss[None,:,None]*(.018-.009*ts[:,None,None])
        p[:,:,2] -= .004*(1-ss[None,:]**2)*np.sin(np.pi*ts[:,None])
        for j,k in np.ndindex(p.shape[:2]):
            p[j,k]=pull_behind(tree,p[j,k],.003)
        u,v=np.meshgrid((ss+1)*.5,ts)
        uv=np.stack((.34+.066*v,u),axis=-1)
        mesh_grid("Bandana / woven gather "+str(side),p,uv,mat,thickness=.0029)

        centers=[]
        for t in ts:
            length=.085 if side<0 else .107
            p=anchor+np.array([side*(.010+.037*t+.007*np.sin(np.pi*t)),
                               -.011-length*t+.011*np.sin(np.pi*t),
                               -.019-.021*t-.006*np.sin(np.pi*t)])
            centers.append(pull_behind(tree,p,.005+.006*t))
        centers=np.array(centers)
        widths=.015+.006*np.sin(np.pi*ts)-.004*ts
        p=centers[:,None,:]+np.array([1.,-.25*side,0.])[None,None,:]*ss[None,:,None]*widths[:,None,None]
        p[:,:,2]-=.003*np.cos(ss[None,:]*np.pi*.8)*np.sin(np.pi*ts[:,None])
        for j,k in np.ndindex(p.shape[:2]):
            p[j,k]=pull_behind(tree,p[j,k],.004)
        u,v=np.meshgrid((ss+1)*.5,ts)
        uv=np.stack((.44+.14*v,u),axis=-1)
        mesh_grid("Bandana / falling tie "+str(side),p,uv,mat,thickness=.0026)

    # A short cross-fold seals the transition without a detached decorative bow.
    s=np.linspace(-1,1,19)
    t=np.linspace(-1,1,9)
    x,y=np.meshgrid(s,t)
    p=anchor+np.stack((.022*x,.014*y-.012,
        -.022-.006*np.maximum(0,1-x*x)*np.maximum(0,1-y*y)),axis=-1)
    uv=np.stack(((x+1)*.05+.36,(y+1)*.46),axis=-1)
    mesh_grid("Bandana / knot cross-fold",p,uv,mat,thickness=.0032)


def cloth_surface(points, loop):
    rows, cols, _ = points.shape
    verts=points.reshape(-1,3).tolist()
    tris=[]
    for j in range(rows-1):
        for i in range(cols if loop else cols-1):
            k=(i+1)%cols
            a,b,c,d=j*cols+i,j*cols+k,(j+1)*cols+k,(j+1)*cols+i
            tris.extend([(a,b,c),(a,c,d)])
    return BVHTree.FromPolygons(verts,tris,all_triangles=True)


def new_sprout(path, cloth, hair, dest):
    g,b=read_glb(path)
    clip=[]
    for node,rotation,offset in node_transforms(g):
        if "mesh" not in node or "clip" not in node.get("name","").lower():
            continue
        for p in g["meshes"][node["mesh"]]["primitives"]:
            clip.extend(vectors(g,b,p["attributes"]["POSITION"]) @ rotation.T+offset)
    assert clip,path
    clip=np.array(clip)
    low=clip[clip[:,1]<=clip[:,1].min()+.006]
    reference=low.mean(axis=0)
    heights=[]
    for bvh in [cloth,hair]:
        h=hit(bvh,[reference[0],3.,reference[2]],-UP)
        if h is not None:
            heights.append(h[1])
    assert heights,path
    dy=float(max(heights)-reference[1]-.0025)
    for index in g["scenes"][g.get("scene",0)]["nodes"]:
        node=g["nodes"][index]
        t=node.get("translation",[0,0,0])
        node["translation"]=[t[0],t[1]+dy,t[2]]
    from bake_catalogue import write_glb
    write_glb(dest,g,b)
    return dy


def generate(build,style):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    key=build+"-"+style
    hair=CAT["builds"][build]["hair"][style]["path"]
    file=ordinary(hair)
    all_hair=surface(file)
    pony = None
    if build=="Feminine":
        crown=all_hair
        if style=="ponytail":
            is_tail = lambda n: "rounded tail220" in n or "tie220" in n
            crown = surface(file,lambda n: not is_tail(n))
            pony = surface(file,is_tail)
        points,uv,loop=female_wrap(crown,style,pony)
        anchor=points[-1,points.shape[1]//2].copy()
        mat=texture("scarf-print.png")
    else:
        points,uv,loop=male_wrap(all_hair,style)
        anchor=points[points.shape[0]//2,0].copy()
        mat=texture("bandana-print.png")
    mesh_grid("Bandana / folded crown scarf" if build=="Feminine" else "Bandana / folded forehead wrap",
              points,uv,mat,loop=loop)
    ties(all_hair,anchor,mat,build=="Feminine")
    shell=cloth_surface(points,loop)
    dest=OUT/(key+"-bandana.glb")
    bpy.ops.export_scene.gltf(filepath=str(dest),export_format="GLB",export_apply=True,
                              export_materials="EXPORT",export_image_format="AUTO")
    sprout=OUT/(key+"-sprout.glb")
    sprout_shift=new_sprout(ordinary(CAT["sprouts"][key+"--headband"]["path"]),shell,all_hair,sprout)
    overlaps=len(shell.overlap(all_hair))
    exported_shell=surface(dest,lambda n: "wrap" in n or "scarf" in n)
    exported_ties=surface(dest,lambda n: "gather" in n or "tie" in n or "cross-fold" in n)
    joins=len(exported_shell.overlap(exported_ties))
    assert joins > 0 and overlaps == 0, (key, joins, overlaps)
    tail_overlaps=0
    if pony is not None:
        tail_overlaps=len(surface(dest).overlap(pony))
        assert tail_overlaps == 0, key
    print(key,"cloth/hair triangle candidates",overlaps,"ponytail candidates",tail_overlaps,"sprout shift",round(sprout_shift,4),flush=True)
    return {
        "hair":hair,"hair_sha256":sha(file),
        "headgear":"./assets/"+dest.name,"headgear_sha256":sha(dest),
        "sprout":"./assets/"+sprout.name,"sprout_sha256":sha(sprout),
        "outer_wrap_hair_overlap_pairs":overlaps,"ponytail_overlap_pairs":tail_overlaps,
        "wrap_tie_contact_pairs":joins,
        "sprout_height_adjustment":sprout_shift,
    }


if __name__=="__main__":
    fits={}
    for build,c in CAT["builds"].items():
        for style in c["hair"]:
            fits[build+"-"+style]=generate(build,style)
    (REV/"bandana-fits.json").write_text(json.dumps(fits,indent=2)+"\n",encoding="utf8",newline="\n")
