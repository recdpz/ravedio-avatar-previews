"""Bake the selected 268 proportions to ordinary, independently fitted GLBs."""
import hashlib
import json
import struct
from pathlib import Path

import numpy as np

REV = Path(__file__).resolve().parents[1]
ROOT = REV.parent
REFERENCE = ROOT / "266"
CENTER = np.array([0.0, 1.88, -0.015])
SCALE = 0.8
LIFT = -8
DY = 0.96 * LIFT / 100
NEW_CENTER = CENTER + [0, DY, 0]
HEAD = "Skin / soft oval head"


def read_glb(path):
    raw = path.read_bytes()
    length, kind = struct.unpack_from("<II", raw, 12)
    assert kind == 0x4E4F534A
    size, kind = struct.unpack_from("<II", raw, 20 + length)
    assert kind == 0x004E4942 and len(raw) == 28 + length + size
    return json.loads(raw[20:20 + length]), bytearray(raw[28 + length:])


def write_glb(path, gltf, binary):
    js = json.dumps(gltf, ensure_ascii=False, separators=(",", ":")).encode()
    js += b" " * (-len(js) % 4)
    assert len(binary) % 4 == 0
    path.write_bytes(
        struct.pack("<IIIII", 0x46546C67, 2, 28 + len(js) + len(binary), len(js), 0x4E4F534A)
        + js + struct.pack("<II", len(binary), 0x004E4942) + binary
    )


def vectors(gltf, binary, index):
    accessor = gltf["accessors"][index]
    view = gltf["bufferViews"][accessor["bufferView"]]
    assert accessor["componentType"] == 5126 and accessor["type"] == "VEC3"
    return np.ndarray(
        (accessor["count"], 3), dtype="<f4", buffer=binary,
        offset=view.get("byteOffset", 0) + accessor.get("byteOffset", 0),
        strides=(view.get("byteStride", 12), 4),
    )


def quintic(y, lower, width):
    t = np.clip((y - lower) / width, 0, 1)
    weight = t**3 * (10 - 15*t + 6*t*t)
    derivative = 30 * t*t * (1-t)**2 / width
    return weight, derivative


def normalized(normal):
    return normal / np.linalg.norm(normal, axis=1, keepdims=True)


def fit_vertices(positions, normals, method):
    points = positions.astype(np.float64)
    if method == "rigid":
        return NEW_CENTER + SCALE * (points - CENTER), normals
    if method in {"drape", "buttonup-drape"}:
        w, dw = quintic(points[:, 1], 1.34, 0.38)
        motion = (SCALE - 1) * (points - CENTER) + [0, DY, 0]
        fitted = points + w[:, None] * motion
        k = 1 + w * (SCALE - 1)
        new_normal = normals / k[:, None]
        new_normal[:, 1] -= dw * (motion * normals).sum(axis=1) / (k * (k + dw * motion[:, 1]))
        new_normal = normalized(new_normal)
        new_normal[w == 0] = normals[w == 0]
        if method == "buttonup-drape":
            return settle_buttonup_scarf(fitted, new_normal)
        return fitted, new_normal
    assert method == "loose"
    w, dw = quintic(points[:, 1], 1.4, 0.3)
    k = 1 + w * (SCALE - 1)
    relative = points - CENTER
    fitted = NEW_CENTER + relative * np.column_stack((k, np.full_like(k, SCALE), k))
    new_normal = normals / k[:, None]
    horizontal = relative[:, 0] * normals[:, 0] + relative[:, 2] * normals[:, 2]
    new_normal[:, 1] = normals[:, 1] / SCALE - (SCALE - 1) * dw * horizontal / (k * SCALE)
    return fitted, normalized(new_normal)



def settle_buttonup_scarf(points, normals):
    """Lay the two front panels over the shirt with a broad fold, including fringe."""
    def depth(p):
        x, y, z = p.T
        front, _ = quintic(z, 0.015, 0.065)
        neckline, _ = quintic(y, 1.398, 0.052)
        panel = 0.006 + 0.011 * np.exp(-((y - 1.244) / 0.078)**2)
        crossing = 0.049 * np.exp(-((y - 1.359) / 0.042)**2 - ((np.abs(x) - 0.091) / 0.109)**2)
        return (panel + crossing) * front * (1 - neckline)

    motion = depth(points)
    gradient = np.column_stack([
        (depth(points + delta) - depth(points - delta)) / 0.00002
        for delta in np.eye(3) * 0.00001
    ])
    assert np.min(1 + gradient[:, 2]) > 0
    fitted = points.copy()
    fitted[:, 2] += motion
    changed_normals = normalized(normals - gradient * (normals[:, 2] / (1 + gradient[:, 2]))[:, None])
    changed_normals[motion == 0] = normals[motion == 0]
    return fitted, changed_normals


def roles_and_methods(fixtures):
    methods = {}

    def include(path, method):
        if not path or path not in fixtures["sphere"]:
            return
        if path in methods and methods[path] != method:
            raise ValueError(f"Incompatible fits for {path}: {methods[path]}, {method}")
        methods[path] = method

    for build, entries in fixtures["builds"].items():
        include(entries["base"], "base")
        include(entries["pantsBase"], "base")
        for key in ("eyes", "grooms", "mouths"):
            for item in entries[key].values():
                include(item.get("path"), "rigid")
        for path in entries["lashes"].values():
            include(path, "rigid")
        for style, entry in entries["hair"].items():
            long = build == "Feminine" and style in {"straight", "curls"}
            include(entry["path"], "loose" if long else "rigid")
            fits = entries["fits"][style]
            include(fits["cap"]["hair"], "loose" if long else "rigid")
            include(fits["cap"]["headgear"], "rigid")
            include(fits["pashmina"]["hair"], "drape" if long else "rigid")
            for top, cloth in entries["pashmina"][style].items():
                method = "buttonup-drape" if build == "Masculine" and top == "buttonup" else "drape"
                include(cloth, method)
        for glasses in entries["glasses"].values():
            for role in ("glasses", "lenses"):
                include(glasses.get(role), "rigid")
    return methods


def bake(source, target, method):
    gltf, binary = read_glb(source)
    updated = {}
    changed = []
    for node in gltf["nodes"]:
        if "mesh" not in node or (method == "base" and node.get("name") != HEAD):
            continue
        assert not {"matrix", "translation", "rotation", "scale"}.intersection(node), node
        changed.append(node.get("name"))
        for primitive in gltf["meshes"][node["mesh"]]["primitives"]:
            attrs = primitive["attributes"]
            p, n = attrs["POSITION"], attrs["NORMAL"]
            if p in updated:
                assert updated[p] == n
                continue
            assert n not in updated.values(), (source, n)
            assert "TANGENT" not in attrs or method in {"rigid", "base"}, source
            positions, normals = vectors(gltf, binary, p), vectors(gltf, binary, n)
            new_p, new_n = fit_vertices(positions, normals, "rigid" if method == "base" else method)
            positions[:] = new_p
            normals[:] = new_n
            bounds = gltf["accessors"][p]
            bounds.update(min=positions.min(axis=0).tolist(), max=positions.max(axis=0).tolist())
            updated[p] = n
    assert updated, source
    if method == "base":
        for node in gltf["nodes"]:
            if "mesh" in node and node.get("name") != HEAD:
                for primitive in gltf["meshes"][node["mesh"]]["primitives"]:
                    assert not set(primitive["attributes"].values()).intersection(set(updated) | set(updated.values()))
    write_glb(target, gltf, binary)
    return changed


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    fixtures = json.loads((REFERENCE / "fixtures.json").read_text(encoding="utf8"))
    methods = roles_and_methods(fixtures)
    output = {}
    assets = []
    for key, method in sorted(methods.items()):
        source = REFERENCE / fixtures["sphere"][key]
        target = REV / "assets" / source.name
        changed = bake(source, target, method)
        output[key] = "./assets/" + target.name
        assets.append({
            "key": key, "source": "../266/" + source.relative_to(REFERENCE).as_posix(),
            "output": output[key], "method": method, "nodes": changed,
            "source_sha256": sha(source), "output_sha256": sha(target),
            "bytes": target.stat().st_size,
        })
    selection = {"headScale": SCALE, "heightPercent": LIFT, "worldLift": DY,
                 "sourceCenter": CENTER.tolist(), "center": NEW_CENTER.tolist(), "radius": 0.48*SCALE}
    data = {"builds": fixtures["builds"], "original": fixtures["sphere"], "selected": output,
            "selection": selection}
    (REV / "fixtures.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf8")
    (REV / "verification" / "assets.json").write_text(json.dumps(assets, indent=2) + "\n", encoding="utf8")
    print(f"Baked {len(assets)} fitted components ({sum(x['bytes'] for x in assets)/1e6:.1f} MB)")


if __name__ == "__main__":
    main()
