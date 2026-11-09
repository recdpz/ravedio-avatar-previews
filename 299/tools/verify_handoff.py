"""Verify the packaged baseline pairs and the supplemental portrait recipe."""
import importlib.util
import hashlib
import json
import struct
import sys
import zipfile
from pathlib import Path

def verify(path):
    with zipfile.ZipFile(path) as archive:
        manifest = json.loads(archive.read("manifest.json"))
        refs = json.loads(archive.read("portrait-20.json"))
        source = json.loads(archive.read("source-art.json"))
        assert refs["revision"] == source["revision"] == manifest["revision"] == 299
        assert refs["display_background"] == "#ffffff"
        expected = {entry["id"] for entry in manifest["fixtures"].values()}
        assert set(refs["fixtures"]) == expected
        assert {entry["fixture"] for entry in source["assemblies"].values()} == expected
        files = manifest["files"]
        assert set(source["assemblies"]["r298-curls-pashmina"]["changed"]) == {"hair","headgear"}
        assert not source["assemblies"]["r298-flow-cap"]["changed"]
        for part in source["assemblies"]["r298-curls-pashmina"]["changed"].values():
            assert part["after"] == files[part["file"]] and part["before"] != part["after"]
        count = 0
        for fixture, rows in refs["fixtures"].items():
            portraits = [r for r in rows if r["yaw"] == -20]
            assert {(r["size"],r["skin"]) for r in portraits} == {
                *((512,i) for i in range(4)), *((size,tone) for size in (40,64) for tone in (0,3)),
            }
            assert all(r["ortho_scale"] == 1.10 and abs(r["target"][2] - 1.78) < 1e-6 for r in portraits)
            angles = [r["yaw"] for r in rows if r["yaw"] != -20]
            assert angles == ([0,-90,90,180] if fixture == "r299-curls-pashmina" else [])
            for row in rows:
                width, height = struct.unpack(">II", archive.read(row["color"])[16:24])
                assert width == height == row["size"] and row["alpha_threshold"] == .5
                assert archive.read(row["depth"])[:4] == b"\x76\x2f\x31\x01"
                assert row["color"] in files and row["depth"] in files
                count += 1
        assert count == 20
    spec = importlib.util.spec_from_file_location("verify_archive", Path(__file__).resolve().parents[2] / "295/tools/verify_archive.py")
    verifier = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(verifier)
    verifier.verify(path, 299)
    with path.open("rb") as handle:
        digest = hashlib.file_digest(handle,"sha256").hexdigest()
    assert path.with_suffix(".zip.sha256").read_text(encoding="ascii").split()[0] == digest
    print(f"Verified {count} additional matched portrait and fit pairs, archive SHA-256 {digest}")

if __name__ == "__main__":
    verify(Path(sys.argv[1]))
