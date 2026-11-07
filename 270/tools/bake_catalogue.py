"""Materialize the full 263 catalogue at the 269 proportions as ordinary GLBs."""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

REV = Path(__file__).resolve().parents[1]
ROOT = REV.parent
SOURCE = ROOT / "263"
sys.path.insert(0, str(ROOT / "269/tools"))
from bake_assets import CENTER, HEAD, NEW_CENTER, SCALE, fit_vertices, normalized, quintic, read_glb, sha, vectors, write_glb

PASHMINA_LOW = 1.34
LONG = {"straight", "curls", "side-sweep"}
BRAIDS = {"twin-braids", "box-braids"}


def config(path):
    return json.loads(path.read_text(encoding="utf-8"))


def active_assets(catalogue):
    assets = {}

    def add(path, role):
        if not path:
            return
        if path in assets and assets[path] != role:
            raise ValueError(f"Ambiguous component {path}: {assets[path]}, {role}")
        assets[path] = role

    def add_hair(path, build, style, hat="none"):
        drape = build == "Feminine" and (style in BRAIDS or (style in LONG and hat == "pashmina"))
        loose = build == "Feminine" and style in LONG
        add(path, "braid" if drape else "loose" if loose else "rigid")

    for build, c in catalogue["builds"].items():
        for path in [c["base"], c.get("shirtlessBase"), *c["pantsBases"].values()]:
            add(path, "base")
        for role in ["eyes", "mouths", "lashes", "grooms"]:
            for entry in c.get(role, {}).values():
                add(entry.get("path"), "smile" if role == "mouths" else "rigid")
        add(c["hot"], "rigid")
        for path in c["rectangular"].values():
            add(path, "rigid")
        for style, entry in c["hair"].items():
            add_hair(entry["path"], build, style)
            for hat, item in catalogue["fits"][build + "-" + style].items():
                add_hair(item["hair"], build, style, hat)
                if hat != "pashmina":
                    band = build == "Masculine" and hat == "headband" and style in {"taper", "curly-top"}
                    add(item["headgear"], style + "-band" if band else "rigid")
        for group in catalogue["pashminaVariants"][build].values():
            for top, path in group.items():
                add(path, "buttonup-drape" if build == "Masculine" and top == "buttonup" else "pashmina")
    for entry in catalogue["glasses"].values():
        add(entry.get("path"), "rigid")
        add(entry.get("lenses"), "rigid")
    for path in catalogue["sprouts"].values():
        add(path["path"], "sprout")
    for group in catalogue["braidLengths"].values():
        for path in group.values():
            add(path, "braid")
    for source, variant in catalogue["ombre"].items():
        if source in assets:
            add(variant, assets[source])
    return assets


class OvalRadius:
    """Sample the smooth 266 radius fit. The dense grid makes bulk exports practical."""

    def __init__(self):
        g, b = read_glb(ROOT / "264/components/Feminine-base264.glb")
        head = next(node for node in g["nodes"] if node.get("name") == HEAD)
        p = g["meshes"][head["mesh"]]["primitives"][0]["attributes"]["POSITION"]
        offset = vectors(g, b, p) - CENTER
        r = np.linalg.norm(offset, axis=1)
        powers = [(x, y, z) for x in range(7) for y in range(7-x) for z in range(7-x-y)]

        def terms(points):
            x, y, z = points.T
            return np.column_stack([x**a * y**b * z**c for a, b, c in powers])

        coeff = np.linalg.lstsq(terms(offset / r[:, None]), r, rcond=1e-10)[0]
        azi = np.linspace(-np.pi, np.pi, 1025)
        ele = np.linspace(-np.pi/2, np.pi/2, 513)
        self.grid = np.empty((len(ele), len(azi)))
        for row, e in enumerate(ele):
            unit = np.column_stack((np.cos(e)*np.cos(azi), np.full_like(azi, np.sin(e)), np.cos(e)*np.sin(azi)))
            self.grid[row] = terms(unit) @ coeff

    def __call__(self, direction):
        x, y, z = direction.T
        a = (np.arctan2(z, x) / np.pi + 1) * 512
        e = (np.arcsin(np.clip(y, -1, 1)) / np.pi + 0.5) * 512
        ai = np.minimum(a.astype(np.int32), 1023)
        ei = np.minimum(e.astype(np.int32), 511)
        t, s = a-ai, e-ei
        g = self.grid
        return (g[ei, ai]*(1-t) + g[ei, ai+1]*t)*(1-s) + (g[ei+1, ai]*(1-t) + g[ei+1, ai+1]*t)*s


def to_sphere(p, radius, role):
    delta = p - CENTER
    length = np.linalg.norm(delta, axis=1)
    unit = delta / np.maximum(length, 1e-9)[:, None]
    sampled = radius(unit)
    t = np.clip((np.maximum(0, length - sampled) - 0.12) / 0.36, 0, 1)
    w = 1 - t*t*(3-2*t)
    if role in {"pashmina", "buttonup-drape"}:
        t = np.clip((p[:, 1] - 1.50) / 0.25, 0, 1)
        w *= t*t*(3-2*t)
    elif role == "braid":
        w *= quintic(p[:, 1], PASHMINA_LOW, 0.20)[0]
    out = p + unit * ((0.48 - sampled) * w)[:, None]
    if role in {"pashmina", "buttonup-drape"}:
        x, y, _ = out.T
        ease = np.exp(-((y-1.43)/0.075)**2 - (x/0.27)**4)
        out[:, 1] -= .025 * ease * quintic(p[:, 1], PASHMINA_LOW, 0.06)[0]
    return out


def warp_normals(warp, p, n):
    ref = np.zeros_like(n)
    ref[:, 0] = 1
    ref[np.abs(n[:, 0]) > 0.9] = [0, 1, 0]
    tangent = normalized(np.cross(n, ref))
    across = np.cross(n, tangent)
    step = 0.00015

    def direction(axis):
        return warp(p + step*axis) - warp(p - step*axis)

    return normalized(np.cross(direction(tangent), direction(across)))


def bandana_edge(p, role):
    x, y, z = p.T
    front = quintic(z, 0.14, 0.13)[0]
    upper = quintic(y, 1.956, 0.109)[0]
    width = 1 - quintic(np.abs(x), 0.19, 0.14)[0]
    lift, edge = (0.066, 0.061) if role == "taper-band" else (0.079, 0.076)
    angle = (lift + edge * upper) * front * width
    y, z = y - NEW_CENTER[1], z - NEW_CENTER[2]
    moved = p.copy()
    moved[:, 1] = NEW_CENTER[1] + y*np.cos(angle) + z*np.sin(angle)
    moved[:, 2] = NEW_CENTER[2] + z*np.cos(angle) - y*np.sin(angle)
    return moved


def deform(p, n, radius, role):
    if role == "base":
        radial = normalized(p - CENTER)
        return NEW_CENTER + 0.384 * radial, radial
    radial_fit = to_sphere(p, radius, role)
    normal = warp_normals(lambda points: to_sphere(points, radius, role), p, n)
    if role == "smile":
        radial_fit += normal * 0.0004 + normalized(radial_fit - CENTER) * 0.0003
    method = {"pashmina": "drape", "buttonup-drape": "buttonup-drape", "braid": "drape", "loose": "loose"}.get(role, "rigid")
    out, normal = fit_vertices(radial_fit, normal, method)
    if role in {"braid", "pashmina"}:
        fixed = p[:, 1] <= PASHMINA_LOW
        out[fixed], normal[fixed] = p[fixed], n[fixed]
    if role in {"taper-band", "curly-top-band"}:
        normal = warp_normals(lambda points: bandana_edge(points, role), out, normal)
        out = bandana_edge(out, role)
    return out, normal


def rotation_matrix(q):
    x, y, z, w = q
    return np.array([
        [1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
        [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
        [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)],
    ])


def node_transforms(gltf):
    def descend(index, rotation, offset):
        node = gltf["nodes"][index]
        assert "matrix" not in node and "scale" not in node
        offset = rotation @ node.get("translation", [0, 0, 0]) + offset
        rotation = rotation @ rotation_matrix(node.get("rotation", [0, 0, 0, 1]))
        yield node, rotation, offset
        for child in node.get("children", []):
            yield from descend(child, rotation, offset)

    for index in gltf["scenes"][gltf.get("scene", 0)]["nodes"]:
        yield from descend(index, np.eye(3), np.zeros(3))


def bake(source, dest, radius, role):
    gltf, binary = read_glb(source)
    modified = set()
    min_cloth = float("inf")
    for node, rot, offset in node_transforms(gltf):
        if "mesh" not in node or (role == "base" and node.get("name") != HEAD):
            continue
        for prim in gltf["meshes"][node["mesh"]]["primitives"]:
            p, n = (prim["attributes"][k] for k in ("POSITION", "NORMAL"))
            assert "TANGENT" not in prim["attributes"], source
            assert p not in modified and n not in modified, source
            pos, nor = vectors(gltf, binary, p), vectors(gltf, binary, n)
            new_pos, new_nor = deform(pos @ rot.T + offset, nor @ rot.T, radius, role)
            if role in {"pashmina", "buttonup-drape"}:
                min_cloth = min(min_cloth, float(np.linalg.norm(new_pos - NEW_CENTER, axis=1).min() - 0.384))
            pos[:], nor[:] = (new_pos - offset) @ rot, new_nor @ rot
            assert np.isfinite(pos).all() and np.isfinite(nor).all(), source
            assert np.max(abs(np.linalg.norm(nor, axis=1) - 1)) < 0.003, source
            gltf["accessors"][p].update(min=pos.min(axis=0).tolist(), max=pos.max(axis=0).tolist())
            modified.update((p, n))
    assert modified, source
    assert not any(i in modified for n in gltf["nodes"] if role == "base" and "mesh" in n and n.get("name") != HEAD
                   for p in gltf["meshes"][n["mesh"]]["primitives"] for i in p["attributes"].values())
    write_glb(dest, gltf, binary)
    return min_cloth if np.isfinite(min_cloth) else None


def prims(gltf):
    return [p for mesh in gltf["meshes"] for p in mesh["primitives"]]


def copy_color_fit(source, authored_peer, fitted_peer, dest):
    """Keep the color file's materials and alpha while using the chosen hairstyle pose."""
    source_doc, source_data = read_glb(source)
    authored_doc, authored_data = read_glb(authored_peer)
    peer_doc, peer_data = read_glb(fitted_peer)
    if len(prims(source_doc)) != len(prims(peer_doc)):
        raise ValueError(f"Color variant topology differs: {source}")
    for variant, authored, fitted in zip(prims(source_doc), prims(authored_doc), prims(peer_doc)):
        for semantic in ("POSITION", "NORMAL"):
            v = variant["attributes"][semantic]
            orig = vectors(authored_doc, authored_data, authored["attributes"][semantic])
            target = vectors(source_doc, source_data, v)
            assert np.array_equal(orig, target), (source, semantic)
            target[:] = vectors(peer_doc, peer_data, fitted["attributes"][semantic])
            if semantic == "POSITION":
                source_doc["accessors"][v].update(min=target.min(axis=0).tolist(), max=target.max(axis=0).tolist())
    write_glb(dest, source_doc, source_data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=REV / "generated")
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    catalogue = config(SOURCE / "catalogue263.json")
    selection = config(ROOT / "269/fixtures.json")
    radius = OvalRadius()
    methods = active_assets(catalogue)
    records = {}
    colors = {variant: original for original, variant in catalogue["ombre"].items() if original in methods}
    paths = sorted(methods.items(), key=lambda row: (row[0] in colors, row[0]))
    files = {}
    color_sources = {}
    for i, (key, role) in enumerate(paths, 1):
        source = (SOURCE / key).resolve()
        source_hash = sha(source)
        reused = selection["selected"].get(key)
        if reused:
            path = (ROOT / "269" / reused).resolve()
            route = "../269/" + path.relative_to(ROOT / "269").as_posix()
            clearance = None
        else:
            # Content-based names share identical assets used across multiple fits.
            stem = f"{source_hash[:24]}-{role}"
            if key in colors:
                peer = colors[key]
                # Two color assets with the same bytes may use different authored fits.
                peer_hash = records[peer]["output_sha256"]
                first = color_sources.setdefault(stem, peer_hash)
                if first != peer_hash:
                    stem += "-" + peer_hash[:12]
                path = out / (stem + ".glb")
                copy_color_fit(source, (SOURCE / peer).resolve(), files[peer], path)
                clearance = None
            else:
                path = out / (stem + ".glb")
                clearance = bake(source, path, radius, role)
            route = "./generated/" + path.name
        files[key] = path
        records[key] = {"path": route, "role": role, "source_sha256": source_hash,
                        "output_sha256": sha(path), "bytes": path.stat().st_size}
        if clearance is not None:
            records[key]["scarf_clearance"] = clearance
        if i % 50 == 0:
            print(f"{i}/{len(methods)} components", flush=True)
    info = {"source": "../263/catalogue263.json", "selection": selection["selection"], "components": records}
    (REV / "assets.json").write_text(json.dumps(info, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"Fitted {len(records)} paths; reused {sum(r['path'].startswith('../269/') for r in records.values())} from 269", flush=True)


if __name__ == "__main__":
    main()
