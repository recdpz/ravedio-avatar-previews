"""Verify the portable native asset package with the Python standard library."""
import hashlib
import json
import struct
import sys
import zipfile
from pathlib import Path


def verify(path):
    with zipfile.ZipFile(path) as archive:
        manifest = json.loads(archive.read("manifest.json"))
        assert manifest["schema"] == "ravedio-native-art-fixtures-1"
        assert manifest["revision"] == 295
        hashes = manifest["files"]
        files = [entry.filename for entry in archive.infolist() if not entry.is_dir()]
        assert len(set(files)) == len(files)
        assert set(files) == {"manifest.json", *hashes}
        for name, digest in hashes.items():
            with archive.open(name) as data:
                assert hashlib.file_digest(data, "sha256").hexdigest() == digest, name
        assert set(manifest["fixtures"]) == {"Feminine", "Masculine"}
        pairs = 0
        for build, fixture in manifest["fixtures"].items():
            assert fixture["scene"] in hashes
            components = fixture["components"]
            assert {"hair", "headgear", "glasses", "lenses"} <= components.keys()
            for slot, asset in components.items():
                name = asset["file"]
                assert hashes[name] == asset["sha256"], slot
                with archive.open(name) as data:
                    magic, version, size = struct.unpack("<4sII", data.read(12))
                    assert magic == b"glTF" and version == 2 and size == asset["bytes"], name
            refs = fixture["references"]
            assert {(r["skin"], r["size"]) for r in refs} == {(s, n) for s in (0, 3) for n in (48, 64, 120, 512)}
            assert len(refs) == 8
            cameras = [r["camera"] for r in refs]
            assert all(c == cameras[0] for c in cameras)
            diagnostics = fixture["diagnostics"]
            assert len(diagnostics) == 2
            assert {r["angle"] for r in diagnostics} == {"rightprofile", "rear"}
            assert all(r["size"] == 512 and r["skin"] == 1 for r in diagnostics)
            for ref in refs + diagnostics:
                size = ref["size"]
                for key in ("color", "web_comparison"):
                    with archive.open(ref[key]) as data:
                        header = data.read(24)
                        assert header[:8] == b"\x89PNG\r\n\x1a\n"
                        assert struct.unpack_from(">II", header, 16) == (size, size), ref[key]
                with archive.open(ref["depth"]) as data:
                    assert struct.unpack("<I", data.read(4))[0] == 20000630, ref["depth"]
                pairs += 1
        print(f"Verified {len(hashes)} package files and {pairs} matched color/depth pairs")


if __name__ == "__main__":
    verify(Path(sys.argv[1]))