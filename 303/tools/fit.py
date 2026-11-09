"""Continue the bandana crown directly into the folds gathered beneath the ponytail."""
import importlib.util
import json
from pathlib import Path

import bpy
import numpy as np

REV = Path(__file__).resolve().parents[1]
ROOT = REV.parent
ASSETS = REV / "assets"
spec = importlib.util.spec_from_file_location("bandana302", ROOT / "302/tools/fit.py")
previous = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous)
updos = previous.updos


def panel(fabric, uv, scalp, tail, elastic, anchor, material):
    """Append both gathered ends to the same vertices as the crown hem."""
    rows, cols = fabric.shape[:2]
    uv = uv.copy()
    uv[:,:,1] -= .075*previous.ease((uv[:,:,1]-.76)/.23)
    vertices = list(fabric.reshape(-1, 3))
    texcoords = list(uv.reshape(-1, 2))
    faces = [
        (r*cols+c, r*cols+c+1, (r+1)*cols+c+1, (r+1)*cols+c)
        for r in range(rows-1) for c in range(cols-1)
    ]
    rim = ([(0,c) for c in range(cols-1)] +
           [(r,cols-1) for r in range(rows-1)] +
           [(rows-1,c) for c in range(cols-1,0,-1)] +
           [(r,0) for r in range(rows-1,0,-1)])
    rim_points = np.array([fabric[r,c] for r,c in rim])-updos.CENTER
    relative = elastic-updos.CENTER
    back = np.arctan2(relative[0],relative[2])
    az = np.arctan2(rim_points[:,0],rim_points[:,2])
    angles = (az-back+np.pi)%(2*np.pi)-np.pi
    for side in (-1,1):
        # The broad section of each rear hem narrows into the knot.
        # The ribbon starts on this actual edge, sharing vertices and UVs.
        indices = np.flatnonzero(np.abs(angles+side*.37)<.167)
        assert len(indices)>10 and np.all(np.diff(indices)==1), indices
        edge = [rim[i] for i in indices]
        points = np.array([fabric[r,c] for r,c in edge])
        rays = previous.unit(points-updos.CENTER)
        polar = np.arccos(rays[:,1])
        longitude = np.arctan2(rays[:,0],rays[:,2])
        outward = np.stack((np.sin(longitude)*np.cos(polar),-np.sin(polar),
                            np.cos(longitude)*np.cos(polar)),axis=-1)
        start_uv = np.array([uv[r,c] for r,c in edge])
        span = points[-1]-points[0]
        finish = anchor + np.array([side*.016,.008,-.009])
        toward = finish-points.mean(axis=0)
        across = previous.unit(np.array([toward[1],-toward[0],0.]))
        if across@span < 0:
            across = -across
        s = np.linspace(-1,1,len(edge))[None,:]
        t = np.linspace(0,1,40)[:,None]
        end = finish+s.T*across*.012
        band = previous.curve([
            points,
            points+outward*.046,
            end+np.array([side*.038,.034,.001]),
            end,
        ],t[:,:,None])
        # Rounded gathers run with the cloth and soften as they enter the knot.
        band[:,:,2] -= (.0045*(1-s*s)+.0027*np.cos(2.2*np.pi*s))*np.sin(np.pi*t)**1.4
        band = previous.drape_over_scalp(band,scalp,tail,.0065)
        band[0] = points
        band_uv = np.broadcast_to(start_uv,(*band.shape[:2],2)).copy()
        band_uv[:,:,1] += .084*t
        active = [r*cols+c for r,c in edge]
        for ring, mapped in zip(band[1:],band_uv[1:],strict=True):
            next_ring = list(range(len(vertices),len(vertices)+len(edge)))
            vertices.extend(ring)
            texcoords.extend(mapped)
            for a,b,c,d in zip(active[:-1],active[1:],next_ring[:-1],next_ring[1:],strict=True):
                faces.append((b,a,c,d))
            active = next_ring

    # Give the continuous textile one thickness and a continuous smoothed normal
    # field through the crown and both gathers.
    p,q,r = (vertices[i] for i in faces[(rows//2)*(cols-1)+cols//2][:3])
    if np.cross(q-p,r-p)@(p-updos.CENTER)<0:
        faces = [tuple(reversed(face)) for face in faces]
    mesh = bpy.data.meshes.new("Ponytail bandana fabric")
    mesh.from_pydata([(float(x),float(-z),float(y)) for x,y,z in vertices],[],faces)
    mesh.update()
    cloth = bpy.data.objects.new("Bandana / continuous crown and gathers",mesh)
    bpy.context.collection.objects.link(cloth)
    layer = mesh.uv_layers.new(name="Cotton print")
    for poly in mesh.polygons:
        poly.use_smooth = True
        for loop in poly.loop_indices:
            layer.data[loop].uv = texcoords[mesh.loops[loop].vertex_index]
    mesh.materials.append(material)
    solid = cloth.modifiers.new("Fabric thickness","SOLIDIFY")
    solid.thickness = .0018
    solid.offset = -1


def knot_and_ends(scalp, tail, anchor, material):
    t,s = np.meshgrid(np.linspace(0,1,37),np.linspace(-1,1,19),indexing="ij")
    for side in (-1,1):
        center = previous.curve([
            anchor+np.array([side*.020,-.007,-.008]),
            anchor+np.array([side*(.026 if side==1 else .014),-.024,-.012]),
            anchor+np.array([side*(.063 if side==1 else .012),-(.060 if side==1 else .041),-.008]),
            anchor+np.array([side*(.079 if side==1 else .018),-.070-.018*side,.007]),
        ],t[:,:,None])
        width = .010+(.012 if side==1 else .005)*np.sin(np.pi*t*.85)**.75
        center[:,:,0] += s*width
        center[:,:,1] += side*.011*s*t**3
        center[:,:,2] -= .008*np.sin(np.pi*t*.94)*(1-s*s)
        if side<0:
            center[:,:,2] = anchor[2]-.008-.004*(1-s*s)*np.sin(np.pi*t)
        else:
            center = previous.drape_over_scalp(center,scalp,tail,.007)
        updos.mesh_grid(f"Bandana / hanging end {side}",center,
                        np.stack((.68+.22*t,(s+1)*.5),axis=-1),material,thickness=.0019)

    y,x = np.meshgrid(np.linspace(-1,1,19),np.linspace(-1,1,25),indexing="ij")
    knot = anchor+np.stack((
        .048*x*(1-.19*y*y)+.008*y,
        .024*y*(1-.22*x*x)+.004*x,
        -.004-.027*(1-x*x)*(1-y*y)+.007*np.exp(-((x-.24*y)/.17)**2)*(1-y*y),
    ),axis=-1)
    knot = previous.drape_over_scalp(knot,scalp,tail,.008)
    uv = np.stack((.49+.080*(x+1)*.5,(y+1)*.5),axis=-1)
    updos.mesh_grid("Bandana / under-tail knot",knot,uv,material,thickness=.004)


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    ASSETS.mkdir(exist_ok=True)
    base = ROOT/"302"
    archived = json.loads((base/"bandana-fits.json").read_text(encoding="utf8").replace('"./assets/','"../302/assets/'))
    fit = archived["Feminine-ponytail"]
    hair = {name:(REV/uri).resolve() for name,uri in fit["fittedHair"].items()}
    _,_,parts = updos.load_parts(hair["default"],"ponytail")
    scalp = updos.tree(*updos.group_geometry(parts,0))
    tail = updos.tree(*updos.group_geometry(parts,1))
    elastic = next(p["points"].mean(axis=0) for p in parts if "tie220" in p["name"])
    fabric,uv,_ = previous.crown(scalp,tail,elastic)
    anchor = elastic + np.array([.071,-.161,0.])
    anchor[2] = -.413
    material = updos.texture("scarf-print.png")
    panel(fabric,uv,scalp,tail,elastic,anchor,material)
    knot_and_ends(scalp,tail,anchor,material)
    target = ASSETS/"ponytail-bandana.glb"
    bpy.ops.export_scene.gltf(filepath=str(target),export_format="GLB",export_apply=True,
                              export_materials="EXPORT",export_image_format="AUTO")

    shell = updos.surface(target)
    crown = updos.surface(target,lambda n:"continuous" in n)
    knot = updos.surface(target,lambda n:"under-tail knot" in n)
    report = {"knot":anchor.tolist(),"scalp_intersections":len(shell.overlap(scalp)),
              "crown_to_knot_contacts":len(crown.overlap(knot)),"tail_intersections":{},"ends":{}}
    for color,path in hair.items():
        _,_,fitted = updos.load_parts(path,"ponytail")
        report["tail_intersections"][color] = len(shell.overlap(updos.tree(*updos.group_geometry(fitted,1))))
    for side in (-1,1):
        end = updos.surface(target,lambda n:n.endswith("hanging end "+str(side)))
        report["ends"][str(side)] = len(end.overlap(knot))
    assert report["scalp_intersections"] == 0 and not any(report["tail_intersections"].values()), report
    assert report["crown_to_knot_contacts"] and all(report["ends"].values()), report
    print(json.dumps(report),flush=True)
    (ASSETS/"geometry.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf8")
    fit["headgear"] = "./assets/"+target.name
    fit["headgear_sha256"] = updos.sha(target)
    (REV/"bandana-fits.json").write_text(json.dumps(archived,indent=2)+"\n",encoding="utf8")


if __name__=="__main__":
    main()
