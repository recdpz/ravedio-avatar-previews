"""Fit the lower fall of long hair to the pashmina opening."""
import hashlib
import json
from itertools import product
import shutil
import sys
from pathlib import Path

import numpy as np
from mathutils.bvhtree import BVHTree

REV = Path(__file__).resolve().parents[1]
ROOT = REV.parent
sys.path.insert(0, str(ROOT / "297/tools"))
from sculpt import (CENTER, accessor, centerline, deform, ease, islands, local_path,
                    node_transforms, read_glb, surface, triangles, turn_along_path, unit, write_glb)
from drape import warp_normals

FIT_STYLES = ("curls", "straight", "box-braids", "bob")
COLLAR_SHA = "c1fb925b46d44243aba671716733f223de6ac57ad59c9dd22c0897f2ede09d20"
SOURCE_SHA = "ed29f0b6f9a304f337860b72f4086d755283c12c3d79e3cf9f5f14d6c6c72935"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inherit(name):
    data = (ROOT / "298" / name).read_text(encoding="utf8")
    return json.loads(data.replace('"./assets/', '"../298/assets/'))


def dump(name, data):
    (REV / name).write_text(json.dumps(data, indent=2) + "\n", encoding="utf8", newline="\n")


def fall(path, style):
    x, y, z = path.T
    at_cheek = np.argmin(abs(y - 1.65))
    side = np.sign(x[at_cheek])
    front = z[at_cheek] > (.057 if style == "curls" else .046)
    rear = 1 - ease((z[at_cheek] + .23) / .16)
    radial = unit(np.column_stack((x, np.zeros(len(y)), z - CENTER[2])))
    if front:
        lead = ease((1.802 - y) / .31)
        drop = ease((1.560 - y) / .23)
        direction = np.array([-.055 * side, 0., .139])
        movement = lead[:, None] * direction
        movement[:, 0] += .012 * side * drop
        movement[:, 2] -= .010 * drop
    else:
        lower = ease((1.675 - y) / .33)
        shoulder = ease((1.425 - y) / .145)
        inset = (.058 - .028 * rear) * lower * (1 - .18 * shoulder)
        movement = -radial * inset[:, None]
        movement[:, 2] -= .042 * (1-rear) * lower
        movement[:, 1] = (.043 + .022 * rear) * lower
    return path + movement, side, front


def tree(points, faces):
    return BVHTree.FromPolygons(points.tolist(), faces.tolist(), all_triangles=True)


def section_pose(section, ring, tangent, path):
    fitted_tangent = unit(np.gradient(path, axis=0))[ring]
    return path[ring] + turn_along_path(section, tangent, fitted_tangent), fitted_tangent


def seat(path, section, ring, tangent, faces, style, cloth, support):
    proposed, side, front = fall(path, style)
    # The cheek pieces go in front of the edge. The other pieces turn
    # back under it, where a small lift can clear the shoulder.
    weight = ease((1.655 - path[:, 1]) / .285)
    if front:
        choices = product((0., .014, .028), (0., .024, .048, .072), (0., .024))
    else:
        choices = product((0., .024, .048, .072), (0., -.028, -.056, -.080), (0., .023, .046, .069, .088))
    faces = faces[np.min(path[:, 1][ring[faces]], axis=1) < 1.71]
    if not len(faces):
        return proposed
    best, fit = None, proposed
    for inset, advance, lift in choices:
        shift = np.array([-side*inset, lift, advance])
        candidate = proposed + weight[:, None] * shift
        points, _ = section_pose(section, ring, tangent, candidate)
        lock = tree(points, faces)
        fabric = sum(len(lock.overlap(part)) for part in cloth)
        body = sum(len(lock.overlap(part)) for part in support)
        # Avoid shoulder penetration and prefer the smallest change among
        # routes that clear the fitted opening. Keep its high roots anchored.
        score = (fabric + body * 2, float(shift @ shift))
        if best is None or score < best:
            best, fit = score, candidate
        if score == (0, 0.):
            break
    return fit


def fit_locks(source, target, style, cloth, support):
    doc, binary = read_glb(source)
    changed = 0
    for node, rotation, offset in node_transforms(doc):
        if "mesh" not in node:
            continue
        mesh = doc["meshes"][node["mesh"]]
        if "side sweep" not in mesh["name"]:
            continue
        for primitive in mesh["primitives"]:
            a = primitive["attributes"]
            pos = accessor(doc, binary, a["POSITION"], 3)
            nor = accessor(doc, binary, a["NORMAL"], 3)
            uv = accessor(doc, binary, a["TEXCOORD_0"], 2)
            faces = triangles(doc, binary, primitive["indices"])
            points, normals = pos @ rotation.T + offset, nor @ rotation.T
            labels = islands(points, faces)
            for label in np.unique(labels):
                mask = labels == label
                _, ring, path = centerline(points[mask], uv[mask])
                section = points[mask] - path[ring]
                tangent = unit(np.gradient(path, axis=0))[ring]
                selected = faces[labels[faces[:,0]] == label]
                local_faces = np.searchsorted(np.flatnonzero(mask), selected)
                target_path = seat(path, section, ring, tangent, local_faces, style, cloth, support)
                moved = np.linalg.norm(target_path - path, axis=1) > 1e-7
                if not moved.any():
                    continue
                p, fitted_tangent = section_pose(section, ring, tangent, target_path)
                n = unit(turn_along_path(normals[mask], tangent, fitted_tangent))
                ids = np.flatnonzero(mask)[moved[ring]]
                pos[ids] = (p[moved[ring]] - offset) @ rotation
                nor[ids] = n[moved[ring]] @ rotation
                changed += len(ids)
            doc["accessors"][a["POSITION"]].update(min=pos.min(axis=0).tolist(), max=pos.max(axis=0).tolist())
    assert changed, style
    write_glb(target, doc, binary)

def geometry(doc, binary):
    for node, rotation, offset in node_transforms(doc):
        if "mesh" not in node:
            continue
        mesh = doc["meshes"][node["mesh"]]
        for p in mesh["primitives"]:
            a = p["attributes"]
            pos = accessor(doc, binary, a["POSITION"], 3)
            nor = accessor(doc, binary, a["NORMAL"], 3)
            yield (mesh["name"], doc["accessors"][a["POSITION"]], pos, nor, rotation, offset,
                   triangles(doc, binary, p["indices"]))


def local_faces(labels, label, faces):
    selected = faces[labels[faces[:,0]] == label]
    return np.searchsorted(np.flatnonzero(labels == label), selected)


def amount(height, style):
    if style == "bob":
        return ease((1.817 - height) / .287)
    return ease((1.755 - height) / .313)


def hem_amount(height):
    # Add a little room specifically as the braid rounds the scarf edge,
    # and let it fall back to the prior path where it rests over the shirt.
    return np.exp(-((height - 1.417) / .104)**2)


def route_patch(part, points, groups, shifts, style):
    _, bounds, pos, nor, rotation, offset, _ = part
    for label, (delta, hem) in shifts.items():
        if not (np.any(delta) or np.any(hem)):
            continue
        group = groups == label

        def warp(p):
            y = p[:,1]
            return p + amount(y, style)[:,None]*delta + hem_amount(y)[:,None]*hem

        pos[group] = (warp(points[group]) - offset) @ rotation
        nor[group] = warp_normals(warp, points[group], nor[group] @ rotation.T) @ rotation
    bounds.update(min=pos.min(axis=0).tolist(), max=pos.max(axis=0).tolist())


def patch_shift(points, faces, anchor, style, cloth, support):
    relevant = np.min(points[faces,1], axis=1) < (1.72 if style == "bob" else 1.58)
    faces = faces[relevant]
    delta, hem = np.zeros(3), np.zeros(3)
    if not len(faces):
        return delta, hem
    side = np.sign(anchor[0])
    front = anchor[2] > (.007 if style == "box-braids" else .034)
    weight = amount(points[:,1], style)[:,None]

    def count(p):
        lock = tree(p, faces)
        contacts = sum(len(lock.overlap(part)) for part in cloth)
        body = sum(len(lock.overlap(part)) for part in support)
        return contacts + body*2

    if style == "bob":
        choices = product((0., .017, .031, .045), (0., .024, .048, .072, .092) if front else (0., -.024), (0., .016))
    elif front:
        choices = product((0., .022, .045, .065), (0., .046, .080, .115, .145), (0., .021))
    else:
        choices = product((0., .017, .035, .057), (0., -.028, -.052, -.078, .027), (0., .026, .051))
    best = None
    for inset, advance, lift in choices:
        candidate = np.array([-side*inset, lift, advance])
        score = (count(points + weight*candidate), float(candidate @ candidate))
        if best is None or score < best:
            best, delta = score, candidate
        if score == (0, 0.):
            break
    if style == "box-braids" and best[0]:
        path = points + weight*delta
        low = hem_amount(points[:,1])[:,None]
        best = (best[0], 0.)
        across_values = (0., -.022, -.045, .022, .046, .068)
        forward_values = (0., .026, .055, .084, .111, .139)
        for across, forward, up in product(across_values, forward_values, (0., .021, -.021, -.042)):
            candidate = np.array([across*side, up, forward if front else -forward])
            score = (count(path + low*candidate), float(candidate @ candidate))
            if score < best:
                best, hem = score, candidate
    return delta, hem

def fit_braids(source, target, cloth, support):
    doc, binary = read_glb(source)
    braid, cuff = geometry(doc, binary)
    points, tips = (p[2] @ p[4].T + p[5] for p in (braid,cuff))
    cuff_ids = islands(tips, cuff[-1])
    labels = np.unique(cuff_ids)
    anchors = np.array([tips[cuff_ids == label].mean(axis=0) for label in labels])
    ply_ids = islands(points, braid[-1])
    groups = np.empty(len(points), dtype=int)
    matches = np.zeros(len(labels), dtype=int)
    for ply in np.unique(ply_ids):
        mask = ply_ids == ply
        values = points[mask]
        tip = values[values[:,1] < values[:,1].min() + .050].mean(axis=0)
        distance = np.linalg.norm((anchors-tip)*[1,.4,1], axis=1)
        choice = distance.argmin()
        groups[mask] = labels[choice]
        matches[choice] += 1
    assert np.all(matches == 4)
    shifts = {label: patch_shift(points[groups == label], local_faces(groups,label,braid[-1]),
                                 anchor, "box-braids", cloth, support)
              for label, anchor in zip(labels, anchors)}
    route_patch(braid, points, groups, shifts, "box-braids")
    route_patch(cuff, tips, cuff_ids, shifts, "box-braids")
    write_glb(target, doc, binary)


def fit_bob(source, target, cloth, support):
    doc, binary = read_glb(source)
    for part in geometry(doc, binary):
        name, _, pos, _, rotation, offset, faces = part
        if "side sweep" not in name:
            continue
        points = pos @ rotation.T + offset
        groups = islands(points, faces)
        shifts = {}
        for label in np.unique(groups):
            lock = points[groups == label]
            tip = lock[lock[:,1] < lock[:,1].min()+.060].mean(axis=0)
            shifts[label] = patch_shift(lock, local_faces(groups,label,faces), tip, "bob", cloth, support)
        route_patch(part, points, groups, shifts, "bob")
    write_glb(target, doc, binary)

def twin_fall(points):
    x, y, _ = points.T
    # The two large plaits need to round the opening sooner than the
    # loose locks. They turn back toward their existing chest contact.
    approach = ease((1.815 - y) / .330)
    settle = ease((y - 1.155) / .218)
    drift = approach * settle
    out = points.copy()
    out[:,0] -= .028 * drift * np.sign(x)
    chest = ease((1.41 - y) / .245)
    opening = .030 * np.exp(-((y - 1.535) / .107)**2)
    out[:,2] += .126 * drift + .062 * chest + opening
    return out


def fit_twins(full_baseline):
    full = json.loads(full_baseline.read_text(encoding="utf8"))["rows"]
    lengths = {}
    for row in full:
        if row["hair"] != "twin-braids":
            continue
        top, color = row["top"], row["hairColor"]
        source = local_path(row["parts"]["hairLengths"])
        target = REV / "assets" / f"twin-braids-{top}-{color}.glb"
        deform(source, target, twin_fall)
        lengths.setdefault(top, {})[color] = "./assets/" + target.name
    assert len(lengths) == 8
    return lengths

def build(fitted, baseline, full_baseline):
    hair = inherit("hair-fits.json")
    scarves = inherit("pashmina-fits.json")
    collar_source = ROOT / "298/assets/scarf-curls-open.glb"
    assert sha(collar_source) == SOURCE_SHA
    assert sha(fitted) == COLLAR_SHA
    target = REV / "assets/scarf-curls-open.glb"
    shutil.copyfile(fitted, target)
    scarves["Feminine"]["curls"]["open"] = "./assets/" + target.name
    rows = json.loads(baseline.read_text(encoding="utf8"))["rows"]
    assert all(row["top"] == "open" for row in rows)
    controls = {row["hair"]:row["parts"] for row in rows if row["hairColor"] == "default"}
    support = [
        surface(local_path(controls["curls"]["base"]), lambda name: name.startswith("Skin / rounded torso")),
        surface(local_path(controls["curls"]["top"]), lambda name: "sleeve" not in name.lower()),
    ]
    support = [part for part in support if part is not None]
    for style in FIT_STYLES:
        cloth = [surface(REV / scarf) for scarf in sorted(set(scarves["Feminine"][style].values()))]
        color_fits = hair["Feminine"][style]["fits"]["pashmina"]
        for color, name in color_fits.items():
            source = (REV / name).resolve()
            target = REV / "assets" / f"{style}-pashmina-{color}.glb"
            if style == "box-braids":
                fit_braids(source, target, cloth, support)
            elif style == "bob":
                fit_bob(source, target, cloth, support)
            else:
                fit_locks(source, target, style, cloth, support)
            color_fits[color] = "./assets/" + target.name
        print(style, flush=True)
    hair["Feminine"]["twin-braids"]["fits"]["pashmina"]["lengths"] = fit_twins(full_baseline)
    dump("hair-fits.json", hair)
    dump("pashmina-fits.json", scarves)


if __name__ == "__main__":
    build(*map(Path, sys.argv[-3:]))
