"""Build continuous triangular crown scarves for Ponytail and Space Buns."""
import importlib.util
import json
import math
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils.bvhtree import BVHTree

REV = Path(__file__).resolve().parents[1]
ROOT = REV.parent
OUT = REV / "assets"
sys.path.insert(0, str(ROOT / "271/tools"))
from build_bandanas import CAT, CENTER, envelope, hit, new_sprout, ordinary, sha, surface, texture

spec = importlib.util.spec_from_file_location("ties272", ROOT / "272/tools/build_bandanas.py")
ties = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ties)

N = 256
RADIUS = .384


def support(tree, rays):
    radii = np.empty(rays.shape[:2])
    for j,k in np.ndindex(radii.shape):
        d = rays[j,k]
        h = hit(tree,CENTER+d,-d)
        radii[j,k] = max(RADIUS,(h-CENTER)@d if h is not None else RADIUS)
    return envelope(radii,False)


def lower_wrap(tree, pony):
    theta = np.linspace(-np.pi,np.pi,N,endpoint=False) - (.25 if pony else 0)
    directions = np.column_stack((np.sin(theta),np.zeros(N),np.cos(theta)))
    rear = ((1-np.cos(theta))/2)**2
    low = 1.961 + .045*np.cos(theta) - .021*rear
    width = .061 - .019*rear
    v = np.linspace(0,1,23)
    heights = low[None,:] + width[None,:]*v[:,None]
    radii = np.empty_like(heights)
    for j,k in np.ndindex(heights.shape):
        base = CENTER.copy()
        base[1] = heights[j,k]
        d = directions[k]
        h = hit(tree,base+d,-d)
        skin = math.sqrt(RADIUS**2-(base[1]-CENTER[1])**2)
        radii[j,k] = max(skin,(h-base)@d if h is not None else skin)
    points = CENTER + directions[None,:,:]*(envelope(radii,True)+(.0026 if pony else .001))[:,:,None]
    points[:,:,1] = heights
    return points, theta


def crown(tree, ring, theta, pony):
    """Pull a broad front edge into a short, free triangle point."""
    indices = np.flatnonzero(np.abs(theta) < (1.13 if pony else 1.12))
    t = np.linspace(0,1,105)[:,None]
    start = ring[-1,indices]-CENTER
    start = start/np.linalg.norm(start,axis=1,keepdims=True)*RADIUS
    # Let the triangular point rest above the knot. The side corners
    # continue as the low ties, so the fabric has a clear way to close.
    tip_x, tip_z = (.091,-.169) if pony else (0.,-.215)
    x = start[None,:,0]*(1-t)**(1.10 if pony else 1.23) + t*tip_x
    z = start[None,:,2]*(1-t)+t*tip_z
    y = np.sqrt(np.maximum(.014**2,RADIUS**2-x*x-z*z))
    rays = np.stack((x,y,z),axis=-1)
    rays /= np.linalg.norm(rays,axis=-1,keepdims=True)
    points = CENTER+rays*(support(tree,rays)+(.0026 if pony else .001))[:,:,None]
    # Pin the front of the triangular panel to the same sewn fold.
    points += (ring[-1,indices]-points[0])[None,:,:]*np.clip(1-t/.085,0,1)[:,:,None]**2
    points[0] = ring[-1,indices]
    return points,indices


def assembled_mesh(ring, panel, front, material):
    rows = ring.shape[0]
    vertices = ring.reshape(-1,3).tolist()
    rings = [[j*N+k for k in range(N)] for j in range(rows)]
    faces,uvs = [],[]
    u_min,u_max = front[0],front[-1]

    def add(face,uv):
        verts, tex = [], []
        for i,p in zip(face,uv):
            if i not in verts:
                verts.append(i)
                tex.append(p)
        if len(verts)>=3:
            faces.append(verts)
            uvs.append(tex)

    for j in range(rows-1):
        for i in range(N):
            k=(i+1)%N
            u,w = (i-u_min)/(u_max-u_min),(i+1-u_min)/(u_max-u_min)
            a,b = .19*j/(rows-1),.19*(j+1)/(rows-1)
            add([rings[j][i],rings[j][k],rings[j+1][k],rings[j+1][i]],[(u,a),(w,a),(w,b),(u,b)])

    strip=[list(np.asarray(rings[-1])[front])]
    for row in panel[1:-1]:
        strip.append(list(range(len(vertices),len(vertices)+len(row))))
        vertices.extend(row.tolist())
    tip = len(vertices)
    vertices.append(panel[-1,len(front)//2].tolist())
    strip.append([tip]*len(front))
    for j in range(len(strip)-1):
        for k in range(len(front)-1):
            v,w=.19+.76*j/(len(strip)-1),.19+.76*(j+1)/(len(strip)-1)
            u,q=k/(len(front)-1),(k+1)/(len(front)-1)
            # Taper the texture with the actual fabric into the back fold.
            a=1-.86*j/(len(strip)-1)
            b=1-.86*(j+1)/(len(strip)-1)
            add([strip[j][k],strip[j][k+1],strip[j+1][k+1],strip[j+1][k]],
                [(.5+(u-.5)*a,v),(.5+(q-.5)*a,v),(.5+(q-.5)*b,w),(.5+(u-.5)*b,w)])

    mesh=bpy.data.meshes.new("One-piece triangular kerchief")
    mesh.from_pydata([(x,-z,y) for x,y,z in vertices],[],faces)
    mesh.update()
    ob=bpy.data.objects.new("Bandana / continuous triangular scarf",mesh)
    bpy.context.collection.objects.link(ob)
    uv=mesh.uv_layers.new(name="Unfolded scarf")
    for polygon,face_uv in zip(mesh.polygons,uvs):
        polygon.use_smooth=True
        for index,coord in zip(polygon.loop_indices,face_uv):
            uv.data[index].uv=coord
    mesh.materials.append(material)
    thickness=ob.modifiers.new("Cotton thickness","SOLIDIFY")
    thickness.thickness=.0024
    thickness.offset=-1

    # The cloth and its triangles in glTF coordinates for exact support checks.
    tri=[]
    for f in faces:
        tri.extend((f[0],f[i],f[i+1]) for i in range(1,len(f)-1))
    return BVHTree.FromPolygons(vertices,tri,all_triangles=True)


def fit(style):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    key = "Feminine-"+style
    source = CAT["builds"]["Feminine"]["hair"][style]["path"]
    hair_file = ordinary(source)
    pony = style == "ponytail"
    is_tail=lambda n:"rounded tail220" in n or "tie220" in n
    hair=surface(hair_file,lambda n:not pony or not is_tail(n))
    tail=surface(hair_file,is_tail) if pony else None
    ring,theta=lower_wrap(hair,pony)
    panel,front=crown(hair,ring,theta,pony)
    mat=texture("scarf-print.png")
    cloth=assembled_mesh(ring,panel,front,mat)
    overlaps=len(cloth.overlap(hair))
    tail_outer=len(cloth.overlap(tail)) if tail is not None else 0
    ties.knit_knot(hair,ring,ring[len(ring)//2,0],mat,True)
    target=OUT/(key+"-bandana.glb")
    bpy.ops.export_scene.gltf(filepath=str(target),export_format="GLB",export_apply=True,
                              export_materials="EXPORT",export_image_format="AUTO")
    wrap=surface(target,lambda n:"scarf" in n)
    tied=surface(target,lambda n:"fold" in n or "tail" in n)
    tail_pairs=len(surface(target).overlap(tail)) if tail is not None else 0
    joins=len(wrap.overlap(tied))
    scarf_hair_pairs=len(wrap.overlap(surface(hair_file)))
    assert overlaps == tail_outer == tail_pairs == scarf_hair_pairs == 0 and joins > 0, (
        key,overlaps,tail_outer,tail_pairs,scarf_hair_pairs,joins,
    )
    print("FIT273",key,"export-scarf/hair",scarf_hair_pairs,"export-tail",tail_pairs,"wrap/knot",joins,flush=True)
    sprout=OUT/(key+"-sprout.glb")
    shift=new_sprout(ordinary(CAT["sprouts"][key+"--headband"]["path"]),cloth,hair,sprout)
    return {
        "hair":source,"hair_sha256":sha(hair_file),
        "construction":"triangular crown scarf",
        "headgear":"./assets/"+target.name,"headgear_sha256":sha(target),
        "sprout":"./assets/"+sprout.name,"sprout_sha256":sha(sprout),
        "outer_wrap_hair_overlap_pairs":overlaps,"ponytail_overlap_pairs":tail_pairs,
        "wrap_tie_contact_pairs":joins,"sprout_height_adjustment":shift,
        "exported_scarf_hair_overlap_pairs":scarf_hair_pairs,
    }


if __name__=="__main__":
    baseline=json.loads((ROOT/"272/bandana-fits.json").read_text(encoding="utf8"))
    for item in baseline.values():
        for role in ("headgear","sprout"):
            item[role]="../272/"+item[role].removeprefix("./")
    for style in ("ponytail","space-buns"):
        baseline["Feminine-"+style]=fit(style)
    (REV/"bandana-fits.json").write_text(json.dumps(baseline,indent=2)+"\n",encoding="utf8",newline="\n")
