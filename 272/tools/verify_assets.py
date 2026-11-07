"""Check the exported bandana inputs and the retained hairstyle provenance."""
import json
import struct
import sys
from pathlib import Path

REV = Path(__file__).resolve().parents[1]
ROOT = REV.parent
sys.path.insert(0, str(ROOT / "270/tools"))
from bake_catalogue import read_glb, sha

original = json.loads((ROOT / "263/catalogue263.json").read_text(encoding="utf8"))
catalogue = json.loads((ROOT / "270/assets.json").read_text(encoding="utf8"))
fits = json.loads((REV / "bandana-fits.json").read_text(encoding="utf8"))
assert len(fits) == 16
checked = {}
for build, entries in original["builds"].items():
    for style, hair in entries["hair"].items():
        key = build + "-" + style
        row = fits[key]
        assert row["hair"] == hair["path"]
        ref = catalogue["components"][row["hair"]]
        assert sha(ROOT / "270" / ref["path"]) == ref["output_sha256"] == row["hair_sha256"]
        for slot in ("headgear","sprout"):
            assert sha(REV / row[slot]) == row[slot+"_sha256"]
        gltf, blob = read_glb(REV / row["headgear"])
        assert len(gltf["images"]) == 1
        image = gltf["images"][0]
        assert image["mimeType"] == "image/png"
        view = gltf["bufferViews"][image["bufferView"]]
        offset = view.get("byteOffset",0)
        assert blob[offset:offset+8] == b"\x89PNG\r\n\x1a\n"
        size = struct.unpack_from(">II",blob,offset+16)
        assert size == ((1024,1024) if row["construction"] == "triangular crown scarf" else (4096,256))
        assert "KHR_draco_mesh_compression" not in gltf.get("extensionsUsed",[])
        assert row["outer_wrap_hair_overlap_pairs"] == row["ponytail_overlap_pairs"] == 0
        assert row["wrap_tie_contact_pairs"] > 0
        checked[key] = {
            "print_dimensions":size, "wrap_tie_contact_pairs":row["wrap_tie_contact_pairs"],
            "outer_cloth_clear":True,"exact_bare_hair":True, "construction":row["construction"],
        }
(REV / "verification/assets.json").write_text(json.dumps(checked,indent=2)+"\n",encoding="utf8",newline="\n")
print("Verified cloth, Sprout and original hair for all",len(checked),"looks")
