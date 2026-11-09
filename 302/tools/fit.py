"""Fit the triangular scarf over the ponytail attachment with an under-tail knot."""
import importlib.util
import json
from pathlib import Path
import sys

import bpy
import numpy as np

REV = Path(__file__).resolve().parents[1]
ROOT = REV.parent
ASSETS = REV / "assets"

spec = importlib.util.spec_from_file_location("updos274", ROOT / "274/tools/fit_updos.py")
updos = importlib.util.module_from_spec(spec)
spec.loader.exec_module(updos)
from build_bandanas import ease, envelope, hit, unit

PITCH = -.48
YAW = -.10
FRONT = np.array([0., 0., 1.])


def curve(points, t):
    a, b, c, d = np.asarray(points)
    return (1-t)**3*a + 3*(1-t)**2*t*b + 3*(1-t)*t**2*c + t**3*d


def direction(azimuth, polar):
    return np.stack((np.sin(polar)*np.sin(azimuth),np.cos(polar),np.sin(polar)*np.cos(azimuth)),axis=-1)


def supported_radius(scalp, ray):
    p = hit(scalp, updos.CENTER+ray, -ray)
    return max(.384, (p-updos.CENTER)@ray if p is not None else .384)


def soften(field, passes):
    weights = np.array([1,4,6,4,1])/16
    for _ in range(passes):
        for axis in (0,1):
            field = np.apply_along_axis(
                lambda row: np.convolve(np.pad(row,2,mode="edge"),weights,mode="valid"),
                axis,field)
    return field


def crown(scalp, tail, elastic):
    """Keep the triangular outline and shape an open edge over the ponytail root."""
    archive, _, _ = updos.female_wrap(scalp, "regular")
    boundary = np.vstack((archive[0],archive[1:,-1],archive[-1,-2::-1],archive[-2:0:-1,0]))-updos.CENTER
    angles = np.arctan2(boundary[:,0],boundary[:,2])
    polar = np.arctan2(np.hypot(boundary[:,0],boundary[:,2]),boundary[:,1])
    center = elastic-updos.CENTER
    back = np.arctan2(center[0],center[2])
    relative = np.linspace(-np.pi,np.pi,361,endpoint=False)
    absolute = back+relative
    original = np.interp(absolute,angles,polar,period=2*np.pi)
    blend = 1-ease((np.abs(relative)-.48)/.34)
    rounded = 1.18-.15*np.exp(-.5*(relative/.17)**2)
    edge = original*(1-blend)+rounded*blend

    # Use the fitted root to set the opening. Spread the margin out through
    # both corners so the cloth takes one rounded turn into the returning ends.
    safe = edge.copy()
    for i,angle in enumerate(absolute):
        if abs(relative[i])>.65:
            continue
        for pitch in np.arange(.62,edge[i],.006):
            ray = direction(angle,pitch)
            p = updos.CENTER+ray*(supported_radius(scalp,ray)+.009)
            nearest, _, _, _ = tail.find_nearest(p,.012)
            if nearest is not None:
                safe[i]=pitch-.014
                break
    i = np.arange(len(relative))
    distance = np.abs(i[:,None]-i[None,:])
    distance = np.minimum(distance,len(i)-distance)
    safe = np.min(safe[None,:]+.022*distance,axis=1)
    kernel = np.array([1,4,6,4,1])/16
    rim = safe
    for _ in range(4):
        rim = np.convolve(np.pad(rim,2,mode="wrap"),kernel,mode="valid")
    safe = np.where(np.abs(relative)<.65,np.minimum(safe,rim),rim)

    def seam(az):
        return np.interp(az,absolute,safe,period=2*np.pi)

    # A disk with one vertex at the center keeps each radial path monotone.
    # The square grid maps smoothly onto it and supplies continuous cloth UVs.
    y,x = np.meshgrid(np.linspace(-1,1,101),np.linspace(-1,1,133),indexing="ij")
    dx,dz = x*np.sqrt(1-y*y/2),y*np.sqrt(1-x*x/2)
    az = np.arctan2(dx,dz)
    radius = np.hypot(dx,dz)
    rays = direction(az,radius*seam(az))
    support = np.empty(az.shape)
    for j,k in np.ndindex(az.shape):
        support[j,k] = supported_radius(scalp,rays[j,k])
    drape = soften(envelope(support,False),5)+.0065+.0010*np.sin(np.pi*radius)**2*np.sin(az*6)
    result = updos.CENTER+rays*drape[:,:,None]
    uv = np.stack((.50+.49*dx,.50-.49*dz),axis=-1)

    starts = {}
    for side in (-1,1):
        turn = back-side*.40
        outer = updos.CENTER+direction(turn,seam(turn))*.40
        distances = np.linalg.norm(result-outer,axis=-1)
        boundary_mask = np.zeros(distances.shape,dtype=bool)
        boundary_mask[[1,-2],:] = True
        boundary_mask[:,[1,-2]] = True
        j,k = np.unravel_index(np.argmin(np.where(boundary_mask,distances,np.inf)),az.shape)
        starts[side] = result[j,k]
    return result, uv, starts

def drape_over_scalp(points, scalp, tail, clearance):
    out = points.copy()
    for j,k in np.ndindex(points.shape[:2]):
        x,y,z = points[j,k]
        p = hit(scalp, np.array([x,y,-.95]), FRONT)
        if p is not None:
            back = p[2] - clearance
            cloth = min(z, back)
            hair = hit(tail, np.array([x,y,.95]), -FRONT)
            if hair is not None and hair[2] + .008 < back:
                cloth = max(cloth, hair[2] + .008)
            out[j,k,2] = cloth
    out[:,:,2] = soften(out[:,:,2],2)
    return out


def tie(scalp, tail, starts, anchor, material):
    along, across = np.meshgrid(np.linspace(0,1,37),np.linspace(-1,1,19),indexing="ij")
    t,s = along,across
    for side in (-1,1):
        start = starts[side].copy()
        start[2] += .001
        end = anchor + np.array([side*.011, .001, -.013])
        control = [
            start,
            start+np.array([side*.001,-.040,-.017]),
            end+np.array([side*.055,-.009,-.010]),
            end,
        ]
        center = curve(control,t[:,:,None])
        fold = center.copy()
        fold[:,:,1] += s*(.016*(1-t)+.009*t)
        fold[:,:,2] -= (.005+.004*t)*(1-s*s)*np.sin(np.pi*t)
        fold = drape_over_scalp(fold, scalp, tail, .006)
        uv = np.stack((.58 + .080*t,(s+1)*.5),axis=-1)
        updos.mesh_grid(f"Bandana / returning fold {side}",fold,uv,material,thickness=.0016)

        center = curve([
            anchor + np.array([side*.013,-.005,-.012]),
            anchor + np.array([side*.025,-.023,-.012]),
            anchor + np.array([side*.072,-.068,-.008]),
            anchor + np.array([side*(.090 if side==1 else .068),-.105-.018*side,-.003]),
        ],t[:,:,None])
        width = .010+.012*np.sin(np.pi*t*.85)**.75
        tails = center.copy()
        tails[:,:,0] += s*width
        tails[:,:,1] += side*.011*s*t**3
        tails[:,:,2] -= .008*np.sin(np.pi*t*.94)*(1-s*s)
        tails = drape_over_scalp(tails,scalp,tail,.007)
        uv = np.stack((.68 + .22*t,(s+1)*.5),axis=-1)
        updos.mesh_grid(f"Bandana / hanging end {side}",tails,uv,material,thickness=.0019)

    y,x = np.meshgrid(np.linspace(-1,1,19),np.linspace(-1,1,25),indexing="ij")
    knots = anchor + np.stack((
        .033*x*(1-.17*y*y)+.006*y,
        .016*y*(1-.22*x*x),
        -.005-.010*(1-x*x)*(1-y*y),
    ),axis=-1)
    knots = drape_over_scalp(knots,scalp,tail,.008)
    uv = np.stack((.49+.075*(x+1)*.5,(y+1)*.5),axis=-1)
    updos.mesh_grid("Bandana / under-tail knot",knots,uv,material,thickness=.004)


def bake(output, pitch, yaw):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    output.mkdir(parents=True, exist_ok=True)
    source = updos.CAT["builds"]["Feminine"]["hair"]["ponytail"]["path"]
    base = updos.ordinary(source)
    materials = json.loads((ROOT/"301/material-assets.json").read_text())["components"]
    source_key = "../" + base.relative_to(ROOT.resolve()).as_posix()
    brown = (ROOT/"301"/materials[source_key]).resolve()
    ombre = updos.ordinary(updos.CAT["ombre"][source])
    _,_,parts = updos.load_parts(brown,"ponytail")
    scalp = updos.tree(*updos.group_geometry(parts,0))
    transform = updos.axis_rotation("y",yaw)@updos.axis_rotation("x",pitch)
    shift = np.zeros(3)
    pose = {1:(transform,shift)}
    elastic = next(p["points"] for p in parts if "tie220" in p["name"])
    elastic = updos.apply(elastic,transform,shift).mean(axis=0)
    tail, indices = updos.group_geometry(parts,1)
    fitted_tail = updos.tree(updos.apply(tail,transform,shift),indices)

    fabric, uv, starts = crown(scalp,fitted_tail,elastic)
    material = updos.texture("scarf-print.png")
    updos.mesh_grid("Bandana / triangular scarf over ponytail",fabric,uv,material,thickness=.0018)
    knot_anchor = np.array([elastic[0]+.007,elastic[1]-.079,-.382])
    tie(scalp,fitted_tail,starts,knot_anchor,material)
    scarf = output/"ponytail-bandana.glb"
    bpy.ops.export_scene.gltf(filepath=str(scarf),export_format="GLB",export_apply=True,
                              export_materials="EXPORT",export_image_format="AUTO")
    hairs = {}
    for color,original in (("default",brown),("ombre",ombre)):
        target=output/f"ponytail-{color}.glb"
        updos.write_pose(original,target,"ponytail",pose)
        hairs[color] = target

    full = updos.surface(scarf)
    scarf_shell = updos.surface(scarf,lambda n: "triangular" in n)
    overlaps = {}
    for fragment in ("triangular","returning fold","hanging end","under-tail knot"):
        piece = updos.surface(scarf,lambda n:fragment in n)
        overlaps[fragment] = {"scalp":len(piece.overlap(scalp)),"tail":len(piece.overlap(fitted_tail))}
    attachment = len(fitted_tail.overlap(scalp))
    assert attachment and all(not any(contact.values()) for contact in overlaps.values()), overlaps
    for color, path in hairs.items():
        _, _, exported = updos.load_parts(path,"ponytail")
        exported_tail = updos.tree(*updos.group_geometry(exported,1))
        assert exported_tail.overlap(scalp) and not exported_tail.overlap(full), color
        for original_part, exported_part in zip(parts,exported,strict=True):
            if not original_part["labels"].any():
                assert np.array_equal(original_part["points"],exported_part["points"]), color
    print("Ponytail contacts",attachment,"cloth contacts",overlaps,flush=True)
    joins = {}
    for side in (-1,1):
        fold = updos.surface(scarf,lambda n:n.endswith("returning fold "+str(side)))
        end = updos.surface(scarf,lambda n:n.endswith("hanging end "+str(side)))
        knot = updos.surface(scarf,lambda n:"under-tail knot" in n)
        joins[str(side)] = {"scarf_to_fold":len(scarf_shell.overlap(fold)),
            "fold_to_knot":len(fold.overlap(knot)), "knot_to_end":len(knot.overlap(end))}
    assert all(all(contacts.values()) for contacts in joins.values()), joins
    print("Fabric joins",joins,flush=True)
    sprout = output/"ponytail-sprout.glb"
    shift = updos.new_sprout(updos.ordinary(updos.CAT["sprouts"]["Feminine-ponytail--headband"]["path"]),
                           scarf_shell,updos.surface(hairs["default"]),sprout)

    fit = {
        "hair": source, "construction": "triangular crown scarf",
        "headgear": "./assets/"+scarf.name,
        "headgear_sha256":updos.sha(scarf),
        "sprout": "./assets/"+sprout.name,
        "sprout_sha256":updos.sha(sprout),
        "fittedHair": {key:"./assets/"+file.name for key,file in hairs.items()},
        "fittedHairSha256": {key:updos.sha(file) for key,file in hairs.items()},
    }
    report = {"pitch":pitch,"yaw":yaw,"elastic":elastic.tolist(),"knot":knot_anchor.tolist(),
              "scalp_attachment":attachment,"cloth_contacts":overlaps,
              "total_tail_contacts":len(full.overlap(fitted_tail)),"fabric_joins":joins,"sprout_shift":shift}
    (output/"fit.json").write_text(json.dumps(fit,indent=2)+"\n",encoding="utf8")
    (output/"geometry.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf8")


def preview(output, pitch, yaw):
    bake(output,pitch,yaw)
    previous = (ROOT/"274/bandana-fits.json").read_text(encoding="utf8")
    fits = json.loads(previous.replace('"./assets/', '"../274/assets/'))
    fits["Feminine-ponytail"] = json.loads((output/"fit.json").read_text(encoding="utf8"))
    (REV/"bandana-fits.json").write_text(json.dumps(fits,indent=2)+"\n",encoding="utf8")


if __name__ == "__main__":
    preview(ASSETS,PITCH,YAW)
