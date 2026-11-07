"""Verify protected GLB data and equivalent color fits for the expanded catalogue."""
import json
from collections import Counter

import numpy as np

from bake_catalogue import (
    HEAD, NEW_CENTER, REV, SOURCE, active_assets, config, node_transforms,
    prims, read_glb, sha, vectors,
)


def verify_asset(original, fitted, role):
    src, src_bytes = read_glb(original)
    dst, dst_bytes = read_glb(fitted)
    edited = set()
    head_count = 0
    for node, rotation, offset in node_transforms(dst):
        if "mesh" not in node or (role == "base" and node.get("name") != HEAD):
            continue
        for p in dst["meshes"][node["mesh"]]["primitives"]:
            pos, normal = (p["attributes"][k] for k in ("POSITION", "NORMAL"))
            edited.update([pos, normal])
            dst_pos = vectors(dst, dst_bytes, pos)
            dst_nor = vectors(dst, dst_bytes, normal)
            assert np.isfinite(dst_pos).all()
            assert np.isfinite(dst_nor).all()
            assert np.max(abs(np.linalg.norm(dst_nor, axis=1) - 1)) < 0.003
            assert np.array_equal(dst_pos.min(axis=0), dst["accessors"][pos]["min"])
            assert np.array_equal(dst_pos.max(axis=0), dst["accessors"][pos]["max"])
            for key in ("min", "max"):
                src["accessors"][pos][key] = dst["accessors"][pos][key]
            if role == "base":
                head_count += 1
                world = dst_pos @ rotation.T + offset
                assert np.max(abs(np.linalg.norm(world - NEW_CENTER, axis=1) - 0.384)) < 2e-7
    if role == "base":
        assert head_count > 0
    assert src == dst, (original, fitted)
    views = {dst["accessors"][i]["bufferView"] for i in edited}
    for i, a in enumerate(dst["accessors"]):
        if i not in edited:
            assert a["bufferView"] not in views
    end = 0
    for start, length in sorted((dst["bufferViews"][v].get("byteOffset", 0), dst["bufferViews"][v]["byteLength"]) for v in views):
        assert start >= end and src_bytes[end:start] == dst_bytes[end:start], original
        end = start + length
    assert src_bytes[end:] == dst_bytes[end:], original


def main():
    c = config(SOURCE / "catalogue263.json")
    manifest = config(REV / "assets.json")
    records = manifest["components"]
    assert set(records) == set(active_assets(c))
    verified = set()
    for source, entry in records.items():
        original = (SOURCE / source).resolve()
        fitted = (REV / entry["path"]).resolve()
        assert fitted.stat().st_size == entry["bytes"]
        assert sha(original) == entry["source_sha256"]
        check_key = (entry["source_sha256"], entry["output_sha256"], entry["role"])
        if check_key not in verified:
            assert sha(fitted) == entry["output_sha256"]
            verify_asset(original, fitted, entry["role"])
            verified.add(check_key)
    colors = 0
    for a, b in c["ombre"].items():
        if a not in records:
            continue
        x, xb = read_glb(REV / records[a]["path"])
        y, yb = read_glb(REV / records[b]["path"])
        assert len(prims(x)) == len(prims(y))
        for p, q in zip(prims(x), prims(y)):
            for semantic in ("POSITION", "NORMAL"):
                v = vectors(x, xb, p["attributes"][semantic])
                w = vectors(y, yb, q["attributes"][semantic])
                assert np.array_equal(v, w), (a, b, semantic)
        colors += 1
    fresh = {x["path"]: x["bytes"] for x in records.values() if x["path"].startswith("./generated/")}
    scarf = [x["scarf_clearance"] for x in records.values() if "scarf_clearance" in x]
    assert min(scarf) > 0.018
    report = {
        "paths": len(records), "unique_verified_assets": len(verified),
        "reused_269_paths": sum(x["path"].startswith("../269/") for x in records.values()),
        "new_files": len(fresh), "generated_bytes": sum(fresh.values()),
        "ombre_matches": colors, "minimum_new_scarf_vertex_clearance": min(scarf),
        "counts_by_method": dict(Counter(x["role"] for x in records.values())),
    }
    (REV / "verification/assets.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
