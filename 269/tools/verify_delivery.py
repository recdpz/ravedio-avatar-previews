
"""Verify 269 geometry protection and the paired reference renders."""
import json
import struct

import numpy as np

from bake_assets import CENTER, HEAD, NEW_CENTER, REV, ROOT, SCALE, read_glb, sha, vectors


def load_json(path):
    return json.loads(path.read_text(encoding="utf8"))


def check_assets():
    rows = []
    for row in load_json(REV / "verification/assets.json"):
        src = (REV / row["source"]).resolve()
        dst = REV / row["output"]
        assert sha(src) == row["source_sha256"] and sha(dst) == row["output_sha256"]
        a, a_binary = read_glb(src)
        b, b_binary = read_glb(dst)
        modified = set()
        minimum = None
        for node in b["nodes"]:
            if "mesh" not in node or node.get("name") not in row["nodes"]:
                continue
            for primitive in b["meshes"][node["mesh"]]["primitives"]:
                pos, norm = (primitive["attributes"][k] for k in ("POSITION", "NORMAL"))
                modified.update((pos, norm))
                p = vectors(b, b_binary, pos)
                n = vectors(b, b_binary, norm)
                assert np.isfinite(p).all() and np.isfinite(n).all()
                assert np.max(np.abs(np.linalg.norm(n, axis=1) - 1)) < 0.003
                assert np.array_equal(p.min(axis=0), b["accessors"][pos]["min"])
                assert np.array_equal(p.max(axis=0), b["accessors"][pos]["max"])
                a["accessors"][pos]["min"] = b["accessors"][pos]["min"]
                a["accessors"][pos]["max"] = b["accessors"][pos]["max"]
                old = vectors(a, a_binary, pos)
                if node.get("name") == HEAD:
                    assert np.max(abs(np.linalg.norm(p - NEW_CENTER, axis=1) - .384)) < 2e-7
                    assert abs(p[:, 1].min() - 1.4192) < 2e-5
                if row["method"] in {"rigid", "base"}:
                    expected = NEW_CENTER + SCALE * (old - CENTER)
                    assert np.max(abs(p - expected)) < 1.2e-7
                    assert np.array_equal(n, vectors(a, a_binary, norm))
                if row["method"] == "drape":
                    anchors = old[:, 1] <= 1.34
                    assert np.array_equal(p[anchors], old[anchors])
                    assert np.array_equal(n[anchors], vectors(a, a_binary, norm)[anchors])
                if row["method"] == "loose":
                    anchors = old[:, 1] <= 1.4
                    assert np.array_equal(p[anchors][:, [0, 2]], old[anchors][:, [0, 2]])
                if "pashmina" in dst.name and "headgear" in dst.name:
                    clearance = float(np.linalg.norm(p - NEW_CENTER, axis=1).min() - 0.384)
                    minimum = clearance if minimum is None else min(minimum, clearance)
                    assert clearance > 0
        assert a == b, dst
        # Check untouched buffer bytes, including topology, UVs, vertex alpha,
        # textures and every part of the base other than the head.
        views = {b["accessors"][i]["bufferView"] for i in modified}
        assert all(item["bufferView"] not in views for i, item in enumerate(b["accessors"]) if i not in modified)
        ranges = sorted((b["bufferViews"][v].get("byteOffset", 0), b["bufferViews"][v]["byteLength"]) for v in views)
        end = 0
        for offset, length in ranges:
            assert offset >= end and a_binary[end:offset] == b_binary[end:offset]
            end = offset + length
        assert a_binary[end:] == b_binary[end:]
        rows.append({"file": row["output"], "pashmina_vertex_clearance": minimum})
    return rows


def exr_depth(path, size):
    data = path.read_bytes()
    magic, version = struct.unpack_from("<II", data)
    assert magic == 20000630 and version == 2
    i, attrs = 8, {}
    while data[i] != 0:
        end = data.index(b"\0", i)
        type_end = data.index(b"\0", end+1)
        length, = struct.unpack_from("<I", data, type_end+1)
        start = type_end+5
        attrs[data[i:end]] = data[start:start+length]
        i = start+length
    assert attrs[b"compression"] == b"\0"
    assert attrs[b"channels"] == b"Depth.V\0" + struct.pack("<iB3xii", 2, 0, 1, 1) + b"\0"
    assert struct.unpack("<iiii", attrs[b"dataWindow"]) == (0, 0, size-1, size-1)
    values = np.empty((size, size), np.float32)
    visited = set()
    for off in struct.unpack_from(f"<{size}Q", data, i+1):
        y, length = struct.unpack_from("<iI", data, off)
        assert length == size * 4 and y not in visited and 0 <= y < size
        values[y] = np.frombuffer(data, dtype="<f4", count=size, offset=off+8)
        visited.add(y)
    assert not np.isnan(values).any()
    return values


def check_pairs():
    out = REV / "references"
    rows = []
    for path in sorted(out.glob("*-pairs.json")):
        record = load_json(path)
        assert sha(out / f"{record['build']}-269.blend") == record["scene_sha256"]
        for obj in record["components"].values():
            assert sha(ROOT / obj["file"]) == obj["sha256"]
        for pair in record["pairs"]:
            color, depth, size = out / pair["color"], out / pair["depth"], pair["size"]
            assert sha(color) == pair["color_sha256"] and sha(depth) == pair["depth_sha256"]
            assert struct.unpack_from(">II", color.read_bytes(), 16) == (size, size)
            values = exr_depth(depth, size)
            valid = (values > 0) & (values < 100)
            assert np.count_nonzero(valid) > size**2 * 0.10
            rows.append({"color": color.name, "depth": depth.name, "finite_depth_pixels": int(valid.sum())})
    assert len(rows) == 10
    return rows


if __name__ == "__main__":
    assets, pairs = check_assets(), check_pairs()
    print(f"Verified {len(assets)} GLBs and {len(pairs)} paired renders")
    print("Minimum pashmina clearance:", min(r["pashmina_vertex_clearance"] for r in assets if r["pashmina_vertex_clearance"] is not None))
    (REV / "verification" / "delivery.json").write_text(json.dumps({"assets": assets, "pairs": pairs}, indent=2) + "\n", encoding="utf8")
