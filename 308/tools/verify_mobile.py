"""Verify a revision 308 transfer archive with the Python standard library."""
from hashlib import file_digest, sha256
import json
from pathlib import Path, PurePosixPath
import struct
import sys
from zipfile import ZipFile


FIXTURES = {"r308-curls-pashmina", "r308-flow-cap", "r308-twin-jersey-pashmina",
            "r308-ponytail-beanie-jersey"}
FORBIDDEN_EXTENSIONS = {"KHR_draco_mesh_compression","EXT_meshopt_compression","KHR_mesh_quantization"}


def png_size(archive, name):
    with archive.open(name) as file:
        header = file.read(24)
    assert header[:8] == b"\x89PNG\r\n\x1a\n", name
    return struct.unpack_from(">II",header,16)


def verify_assets(archive, manifest):
    files, assets = manifest["files"], manifest["assets"]
    for digest, asset in assets.items():
        name = asset["file"]
        assert files[name] == asset["sha256"] == digest
        with archive.open(name) as file:
            magic, version, length = struct.unpack("<4sII", file.read(12))
            assert (magic,version,length) == (b"glTF",2,asset["bytes"]), name
            assert archive.getinfo(name).file_size == length
            size, tag = struct.unpack("<I4s",file.read(8))
            assert tag == b"JSON"
            gltf = json.loads(file.read(size))
        assert not FORBIDDEN_EXTENSIONS.intersection(gltf.get("extensionsUsed", []))
        assert all("uri" not in image and "bufferView" in image for image in gltf.get("images", []))
        assert all("uri" not in buffer for buffer in gltf["buffers"])


def verify_fixtures(archive, manifest):
    fixtures = manifest["fixtures"]
    stage = json.loads(archive.read("mobile-stage.json"))
    assert set(fixtures) == set(stage["assemblies"]) == FIXTURES
    assert stage["art_revision"] == manifest["revision"] and stage["mobile_base"] == manifest["mobile_base"]
    assert stage["palette"] in manifest["files"]
    pairs = 0
    for key, fixture in fixtures.items():
        assert fixture["scene"] in manifest["files"]
        entry = stage["assemblies"][key]
        assert entry["features"] == fixture["features"]
        assert entry["overrides"] == fixture["appearance_overrides"]
        assert entry["texture_overrides"] == fixture["texture_overrides"]
        assert entry["camera"] == fixture["references"][0]["camera"]
        assert [p["role"] for p in entry["parts"]] == list(fixture["components"])
        for part in entry["parts"]:
            asset = manifest["assets"][fixture["components"][part["role"]]["asset"]]
            level = {k:asset[k] for k in ("file","sha256","bytes","triangles")}
            assert part["levels"] == {"portrait":level, "detail":level}
        refs, diagnostics = fixture["references"], fixture["diagnostics"]
        assert {(r["skin"],r["size"]) for r in refs} == {(s,n) for s in range(4) for n in (48,64,120,512)}
        assert len(refs) == 16 and all(r["view"] == "chat" and r["angle"] == "front" for r in refs)
        assert all(r["camera"] == refs[0]["camera"] for r in refs)
        assert {r["angle"] for r in diagnostics if r["view"] == "face"} == {"rightprofile","rear"}
        assert {r["angle"] for r in diagnostics if r["view"] == "body"} == (
            {"front","threequarter","rear"} if fixture["features"]["top"] == "jersey" else set())
        for ref in refs + diagnostics:
            for kind in ("color","web_comparison"):
                assert png_size(archive,ref[kind]) == (ref["size"],ref["size"])
            with archive.open(ref["depth"]) as depth:
                assert struct.unpack("<I",depth.read(4))[0] == 20000630
            assert ref["alpha_threshold"] == .5
            pairs += 1
    assert "hairLengths" in fixtures["r308-twin-jersey-pashmina"]["components"]
    pony = fixtures["r308-ponytail-beanie-jersey"]
    assert "hairLengths" in pony["components"]
    assert pony["features"]["hairColor"] == "ombre" and pony["features"]["topColor"] == "white"
    bindings = pony["texture_overrides"]
    assert bindings["role"] == "top" and bindings["materials"]
    authored = manifest["assets"][pony["components"]["top"]["asset"]]["materials"]
    indices = {row["index"] for row in bindings["materials"]}
    assert len(indices) == len(bindings["materials"])
    assert all(0 <= i < len(authored) for i in indices)
    for row in bindings["materials"]:
        assert authored[row["index"]]["name"] == row["name"]
        if "base_color_textures" in row:
            assert row["base_color_textures"] in manifest["files"]
    assert {row["index"] for row in bindings["materials"] if "jersey atlas" in row["name"]}
    seed = stage["seed"]
    data = archive.read(seed["file"])
    assert sha256(data).hexdigest() == seed["sha256"]
    lookbook = json.loads(data)
    looks, messages = lookbook["appearances"], lookbook["messages"]
    assert len(looks) == seed["distinct_visual_keys"] == 16
    assert len(messages) == seed["rows"] == len({r["id"] for r in messages}) == 64
    assert {(r["assembly_id"],r["skin"]) for r in looks} == {(key,s) for key in FIXTURES for s in range(4)}
    assert {r["appearance"] for r in messages} == {r["id"] for r in looks}
    assert all(sum(m["appearance"] == r["id"] for m in messages) == 4 for r in looks)
    assert pairs == 78
    return f"{len(fixtures)} assemblies, {pairs} matched color/depth pairs, {len(looks)} distinct looks"


def verify_delta(archive, manifest):
    delta = json.loads(archive.read(manifest["delta"]))
    assert delta["schema"] == "ravedio-catalogue-delta-1"
    assert (delta["base_revision"],delta["revision"]) == (298,308)
    ids, roles = set(),set()
    assert delta["scanned_selections"] >= len(delta["entries"]) > 0
    for key, changes in delta["entries"].items():
        assert len(key.split("/")) == len(delta["selector_fields"])
        assert len({c["role"] for c in changes}) == len(changes)
        roles.update(c["role"] for c in changes)
    for change in [c for changes in delta["entries"].values() for c in changes] + list(delta["grooms"].values()):
        target = change["target"]
        if target:
            digest = target["asset"]
            assert digest != change["before_sha256"]
            assert digest in manifest["assets"]
            assert not target["source"].startswith("306/"), target
            ids.add(digest)
    assert {"hair","hairLengths","headgear","top","sprout"} <= roles
    assert ids == set(manifest["assets"])
    for finish in ("default","ombre"):
        row = delta["entries"][f"Feminine/box-braids/none/open/{finish}"]
        assert any(x["target"]["source"].startswith("304/") for x in row if x["role"]=="hair")
    return f"{len(delta['entries'])} changed selector rows, {len(delta['grooms'])} groom updates"


def verify(path):
    receipt = path.with_suffix(".zip.sha256")
    if receipt.exists():
        expected, name = receipt.read_text().split()
        with path.open("rb") as file:
            assert name == path.name and file_digest(file,"sha256").hexdigest() == expected
    with ZipFile(path) as archive:
        manifest = json.loads(archive.read("manifest.json"))
        assert manifest["schema"] == "ravedio-art-308-handoff-1" and manifest["revision"] == 308
        files = [f.filename for f in archive.infolist() if not f.is_dir()]
        assert len(files) == len(set(files))
        assert set(files) == {"manifest.json", *manifest["files"]}
        for name, digest in manifest["files"].items():
            p = PurePosixPath(name)
            assert not p.is_absolute() and ".." not in p.parts and "\\" not in name and ":" not in name
            with archive.open(name) as file:
                assert file_digest(file,"sha256").hexdigest() == digest, name
        verify_assets(archive, manifest)
        appearance = json.loads(archive.read("appearance.json"))
        dyes = appearance["feminine_jersey"]["dyes"]
        assert dyes["default"]["embedded"] and len(dyes) == 9
        for key,dye in dyes.items():
            if key != "default":
                assert png_size(archive,dye["atlas"]) == (2048,2048)
                png_size(archive,dye["pattern"])
        if manifest["package"] == "fixtures":
            details = verify_fixtures(archive,manifest)
        else:
            assert manifest["package"] == "catalogue-delta"
            details = verify_delta(archive,manifest)
        print(f"{path.name}: verified {len(files)} files, {len(manifest['assets'])} GLBs, {details}")


if __name__ == "__main__":
    for filename in sys.argv[1:]:
        verify(Path(filename))
