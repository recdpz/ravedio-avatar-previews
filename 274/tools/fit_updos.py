"""Fit the existing triangular scarf to two updos using whole-hair placement."""
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
from build_bandanas import (
    CAT, CENTER, cloth_surface, female_wrap, mesh_grid, new_sprout, node_transforms,
    ordinary, read_glb, sha, surface, texture, triangles, vectors,
)
from bake_catalogue import write_glb

spec = importlib.util.spec_from_file_location("ties272", ROOT / "272/tools/build_bandanas.py")
ties = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ties)


def axis_rotation(axis, angle):
    c, s = math.cos(angle), math.sin(angle)
    if axis == "x":
        return np.array([[1,0,0],[0,c,-s],[0,s,c]])
    if axis == "y":
        return np.array([[c,0,s],[0,1,0],[-s,0,c]])
    return np.array([[c,-s,0],[s,c,0],[0,0,1]])


def bun_groups(points, indices):
    # One exported mesh contains the crown and individual bun coils.
    # Weld only for identification. The actual glTF topology remains intact.
    _, inv = np.unique(np.round(points,5), axis=0, return_inverse=True)
    parent = list(range(int(inv.max())+1))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for a,b,c in inv[indices]:
        r = find(a)
        parent[find(b)] = r
        parent[find(c)] = r
    groups = np.array([find(i) for i in inv])
    labels = np.zeros(len(points),dtype=np.int8)
    for group in np.unique(groups):
        m = groups == group
        q = points[m]
        if q[:,1].min() > 2.045 and q[:,2].max() < .015:
            if q[:,0].min() > .145:
                labels[m] = 1
            elif q[:,0].max() < -.145:
                labels[m] = -1
    return labels


def load_parts(path, style):
    g,b = read_glb(path)
    parts = []
    for node, rotation, offset in node_transforms(g):
        if "mesh" not in node:
            continue
        name = node.get("name","")
        for p in g["meshes"][node["mesh"]]["primitives"]:
            pos, normal = (p["attributes"][k] for k in ("POSITION","NORMAL"))
            points = vectors(g,b,pos)@rotation.T+offset
            inds = triangles(g,b,p["indices"]).astype(np.int32)
            if style == "space-buns":
                labels = bun_groups(points,inds)
            else:
                is_tail = "rounded tail220" in name or "tie220" in name
                labels = np.full(len(points),int(is_tail),dtype=np.int8)
            assert np.all(labels[inds] == labels[inds[:,[0]]]),name
            parts.append({
                "p":pos, "n":normal, "points":points, "inds":inds, "labels":labels,
                "rot":rotation, "offset":offset, "name":name,
            })
    assert {int(label) for p in parts for label in np.unique(p["labels"])} == (
        {-1,0,1} if style == "space-buns" else {0,1}
    )
    return g,b,parts


def group_geometry(parts, label):
    verts, tris = [], []
    for part in parts:
        mask = part["labels"] == label
        if not mask.any():
            continue
        idx = part["inds"][mask[part["inds"][:,0]]]
        lookup = np.cumsum(mask,dtype=np.int32)-1
        tris.extend((lookup[idx]+len(verts)).tolist())
        verts.extend(part["points"][mask].tolist())
    return np.array(verts),tris


def tree(points, inds):
    return BVHTree.FromPolygons(points.tolist(),inds,all_triangles=True)


def apply(points, matrix, offset):
    return CENTER + (points-CENTER)@matrix.T + offset


def candidate_groups(parts, scalp, scarf, style):
    labels = [1] if style == "ponytail" else [-1,1]
    chunks = {label:group_geometry(parts,label) for label in labels}
    candidates = []
    if style == "ponytail":
        for pitch in [-.10,-.16,-.22,-.28,-.34,-.40,-.46,-.52,-.58,-.64,-.70,-.76]:
            for yaw in [0,.10,.20,.30,.40,.52,.64,.76,.88]:
                for roll in [0,.09,.18,.27,.36]:
                    candidates.append((abs(pitch)+abs(yaw)*.83+roll,pitch,yaw,roll))
    else:
        for pitch in [-.06,-.10,-.15,-.20,-.25,-.30,-.36,-.42,-.49,-.56]:
            for yaw in [0,.06,.12,.18,.24,.31,.38]:
                for roll in [0,.045,.09,.135,.18,.225,.27,.315]:
                    candidates.append((abs(pitch)+abs(yaw)*.85+abs(roll)*1.12,pitch,yaw,roll))

    good = []
    rejected = [0, 0, 0]
    for score,pitch,yaw,roll in sorted(candidates):
        transforms,contacts = {},[]
        for label,(points,inds) in chunks.items():
            # In the bun fit both bunches rotate back together, with mirrored sides.
            r = axis_rotation("y",yaw*(label if style=="space-buns" else 1)) @ axis_rotation("x",pitch)
            r = axis_rotation("z",roll if style=="ponytail" else -roll*label)@r
            centroid = (points-CENTER).mean(axis=0)@r.T
            direction = centroid/np.linalg.norm(centroid)
            for inset in [0.,.004,.008,.012]:
                offset = -direction*inset
                moved = apply(points,r,offset)
                if moved[:,1].min() < 1.53:
                    rejected[0] += 1
                    continue
                posed = tree(moved,inds)
                if posed.overlap(scarf):
                    rejected[1] += 1
                    continue
                contact = len(posed.overlap(scalp))
                if contact < 3:
                    rejected[2] += 1
                if contact >= 3:
                    transforms[label] = (r,offset)
                    contacts.append(contact)
                    break
        if len(transforms)==len(labels):
            good.append((score,pitch,yaw,roll,transforms,contacts))
            if len(good)==4:
                break
    assert good, (style,rejected)
    return good


def write_pose(path, output, style, transforms):
    g,b,parts = load_parts(path,style)
    for part in parts:
        world = part["points"].copy()
        normals = vectors(g,b,part["n"])@part["rot"].T
        changed = part["labels"] != 0
        if not changed.any():
            continue
        for label,(matrix,offset) in transforms.items():
            selected = part["labels"] == label
            world[selected] = apply(world[selected],matrix,offset)
            normals[selected] = normals[selected]@matrix.T
        p,n = vectors(g,b,part["p"]),vectors(g,b,part["n"])
        p[changed] = (world[changed]-part["offset"])@part["rot"]
        n[changed] = normals[changed]@part["rot"]
        g["accessors"][part["p"]].update(min=p.min(axis=0).tolist(),max=p.max(axis=0).tolist())
    write_glb(output,g,b)


def fit(style):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    key = "Feminine-"+style
    base = CAT["builds"]["Feminine"]["hair"][style]["path"]
    original = ordinary(base)
    _,_,parts = load_parts(original,style)
    scalp = tree(*group_geometry(parts,0))
    points,uv,loop = female_wrap(scalp,"regular")
    if style == "space-buns":
        # Keep the same crown and rear drape. Ease the corners in just enough
        # to let the full-size buns sit clear of the cloth.
        points,uv = points[:,23:-23],uv[:,23:-23]
    direction = points-CENTER
    points += .0012*direction/np.linalg.norm(direction,axis=-1,keepdims=True)
    outer = cloth_surface(points,loop)
    assert not outer.overlap(scalp), key
    cloth_mat = texture("scarf-print.png")
    anchor = points[-1,points.shape[1]//2].copy()
    mesh_grid("Bandana / triangular crown scarf",points,uv,cloth_mat,loop=loop)
    ties.knit_knot(scalp,points,anchor,cloth_mat,False)
    cloth = OUT/(key+"-bandana.glb")
    bpy.ops.export_scene.gltf(filepath=str(cloth),export_format="GLB",export_apply=True,
                              export_materials="EXPORT",export_image_format="AUTO")
    full = surface(cloth)
    wrap = surface(cloth,lambda name:"scarf" in name)
    knot = surface(cloth,lambda name:"fold" in name or "tail" in name)
    joins = len(wrap.overlap(knot))
    assert joins > 0,key
    solutions = candidate_groups(parts,scalp,full,style)
    score,pitch,yaw,roll,pose,contacts = solutions[0]
    hairs,hashes = {},{}
    for color,source in [("default",base),("ombre",CAT["ombre"][base])]:
        result = OUT/(key+"-"+color+"-scarf-hair.glb")
        write_pose(ordinary(source),result,style,pose)
        _,_,fitted = load_parts_for_verify(result,parts)
        for label in pose:
            moved = tree(*group_geometry(fitted,label))
            assert not moved.overlap(full),(key,color,label)
            assert moved.overlap(scalp),(key,color,label,"lost attachment")
        hairs[color] = "./assets/"+result.name
        hashes[color] = sha(result)
    sprout = OUT/(key+"-sprout.glb")
    sprout_shift = new_sprout(ordinary(CAT["sprouts"][key+"--headband"]["path"]),outer,
                              surface(REV/hairs["default"]),sprout)
    print("FIT274",key,"pitch/yaw/roll",pitch,yaw,roll,"scalp contact",contacts,
          "other candidates",[(x[1],x[2],x[3]) for x in solutions[1:]],flush=True)
    return {
        "hair":base,"hair_sha256":sha(original),"construction":"triangular crown scarf",
        "headgear":"./assets/"+cloth.name,"headgear_sha256":sha(cloth),
        "sprout":"./assets/"+sprout.name,"sprout_sha256":sha(sprout),
        "fittedHair":hairs,"fittedHairSha256":hashes,
        "outer_wrap_hair_overlap_pairs":0,"ponytail_overlap_pairs":0,
        "wrap_tie_contact_pairs":joins,"sprout_height_adjustment":sprout_shift,
        "pose":{"pitch":pitch,"yaw":yaw,"outward_roll":roll,"scalp_contacts":contacts,
                "transforms":{str(k):{"matrix":m.tolist(),"offset":t.tolist()} for k,(m,t) in pose.items()}},
    }


def load_parts_for_verify(path, originals):
    g,b = read_glb(path)
    # Export retains indices and node coordinates, so use the original group labels.
    result = []
    for p in originals:
        points = vectors(g,b,p["p"])@p["rot"].T + p["offset"]
        result.append({**p,"points":points})
    return g,b,result


if __name__ == "__main__":
    baseline = json.loads((ROOT/"273/bandana-fits.json").read_text(encoding="utf8"))
    for style in ("ponytail","space-buns"):
        baseline["Feminine-"+style] = fit(style)
    (REV/"bandana-fits.json").write_text(json.dumps(baseline,indent=2)+"\n",encoding="utf8",newline="\n")
