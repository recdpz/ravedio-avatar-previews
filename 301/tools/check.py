"""Verify revision 301 resolves every color-only replacement and reuses the exact mesh data."""
import hashlib
import json
import sys
from pathlib import Path

from bake import REVISION, asset_path, read_glb


def verify(before_path, after_path, preview_origin):
    read = lambda path: json.loads(path.read_text(encoding="utf-8-sig"))
    before, after = read(before_path), read(after_path)
    manifest = read(REVISION / "material-assets.json")["components"]
    assert len(before) == len(after) and before
    check = set()
    selections = 0
    for previous, current in zip(before, after, strict=True):
        assert previous["build"] == current["build"] and previous["features"] == current["features"]
        assert previous["components"].keys() == current["components"].keys()
        for role, uri in previous["components"].items():
            source = asset_path(uri, preview_origin + "/300/")
            original = "../" + source.relative_to(REVISION.parent).as_posix()
            eligible = role in {"hair", "hairLengths", "groom"} and previous["features"]["hairColor"] == "default"
            mapped = manifest.get(original) if eligible else None
            actual = asset_path(current["components"][role], preview_origin + "/301/")
            expected = (REVISION / mapped.removeprefix("./")) if mapped else source
            assert actual == expected, (role, actual, expected)
            if mapped:
                check.add((source, actual))
        selections += 1

    assert len(check) == len(manifest)
    for source, target in check:
        original, binary = read_glb(source)
        revised, result = read_glb(target)
        assert hashlib.sha256(binary).digest() == hashlib.sha256(result).digest(), target
        source_materials, target_materials = original.pop("materials"), revised.pop("materials")
        assert original == revised, target
        for old, new in zip(source_materials, target_materials, strict=True):
            if old == new:
                continue
            old_factor = old["pbrMetallicRoughness"].pop("baseColorFactor", [1, 1, 1, 1])
            new_factor = new["pbrMetallicRoughness"].pop("baseColorFactor")
            assert old_factor[3] == new_factor[3], target
            old.get("extras", {}).pop("hairBase252", None)
            new.get("extras", {}).pop("hairBase252", None)
            assert old == new, target
    print(f"Verified {selections} selections and {len(check)} color-only GLBs with identical binary chunks")


if __name__ == "__main__":
    verify(Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3] if len(sys.argv) > 3 else "http://127.0.0.1:9251")
