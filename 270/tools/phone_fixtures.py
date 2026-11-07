"""Package two expanded-catalogue looks for the existing iOS and Android labs."""
import json
import shutil
import struct
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bake_catalogue import REV, ROOT, SOURCE, config, sha

sys.path.insert(0, str(ROOT / "269/tools"))
from render_references import camera, configure, load_studio, skin_tone
from verify_delivery import exr_depth

LOOKS = {
    "Feminine": {
        "hair": "twin-braids", "headwear": "pashmina", "top": "sweatshirt",
        "bottom": "pants", "eyes": "hooded", "groom": "none", "glasses": "reading",
    },
    "Masculine": {
        "hair": "taper", "headwear": "headband", "top": "buttonup",
        "bottom": "pants", "eyes": "bean", "groom": "short", "glasses": "wayfarer",
    },
}


def selection_files(catalogue, manifest, build, s):
    c = catalogue["builds"][build]
    parts = {
        "base": c["pantsBases"]["clothed"],
        "top": c["tops"][s["top"]]["path"],
        "bottom": c["bottoms"][s["bottom"]]["path"],
        "eyes": c["eyes"][s["eyes"]]["path"],
        "mouth": c["mouths"]["line"]["path"],
        "groom": c["grooms"][s["groom"]]["path"],
        "glasses": catalogue["glasses"][s["glasses"]]["path"],
        "lenses": catalogue["glasses"][s["glasses"]]["lenses"],
        **catalogue["fits"][build + "-" + s["hair"]][s["headwear"]],
    }
    if build == "Feminine":
        parts["lashes"] = c["lashes"][s["eyes"]]["path"]
        parts["hairLengths"] = catalogue["braidLengths"]["pashmina"][s["top"]]
        family = catalogue["pashminaHairFamilies"][build][s["hair"]]
        parts["headgear"] = catalogue["pashminaVariants"][build][family][s["top"]]
    result = {}
    for slot, path in parts.items():
        if not path:
            continue
        if slot in {"top", "bottom"}:
            result[slot] = (SOURCE / path).resolve()
        else:
            asset = manifest["components"][path]
            file = (REV / asset["path"]).resolve()
            assert sha(file) == asset["output_sha256"]
            result[slot] = file
    return result


def pack(out):
    catalogue = config(SOURCE / "catalogue263.json")
    manifest = config(REV / "assets.json")
    recipes = {}
    for build, features in LOOKS.items():
        target = out / build
        components = target / "components"
        components.mkdir(parents=True)
        source = selection_files(catalogue, manifest, build, features)
        packed = {slot: Path(shutil.copyfile(path, components / f"{slot}.glb")) for slot, path in source.items()}
        scene, studio = load_studio(build, packed)
        scene.name = f"Ravedio 270 {build}"
        depth = configure(scene)
        depth.directory = "//"
        depth.file_name = "depth"
        scene.render.filepath = "//color.png"
        skin_tone(1)
        camera(scene, "front", 512)
        scene["avatar_revision"] = "270"
        bpy.ops.file.pack_all()
        scene_path = target / "reference.blend"
        bpy.ops.wm.save_as_mainfile(filepath=str(scene_path), compress=True)
        depth.directory = str(target)
        pairs = []
        for tone in [0, 3]:
            skin_tone(tone)
            for size in [48, 64, 512]:
                cam = camera(scene, "front", size)
                base = f"front-skin{tone}-{size}"
                depth.file_name = base + "-depth"
                color = target / (base + "-color.png")
                scene.render.filepath = str(color)
                bpy.ops.render.render(write_still=True)
                exr, = target.glob(base + "-depth*.exr")
                assert struct.unpack_from(">II", color.read_bytes(), 16) == (size, size)
                z = exr_depth(exr, size)
                assert ((z > 0) & (z < 100)).any()
                pairs.append({"size": size, "skin": tone, "camera": cam, "alpha_threshold": 0.5,
                              "color": color.name, "color_sha256": sha(color),
                              "depth": exr.name, "depth_sha256": sha(exr)})
        recipes[build] = {
            "features": features, "scene_sha256": sha(scene_path), "studio_source_sha256": sha(studio),
            "components": {slot: {"file": path.relative_to(target).as_posix(),
                                  "sha256": sha(path)} for slot, path in packed.items()},
            "color_management": {key: getattr(scene.view_settings, key)
                                 for key in ["view_transform", "look", "exposure", "gamma"]},
            "pairs": pairs,
        }
    receipt = {"revision": 270, "selection": manifest["selection"],
               "asset_manifest_sha256": sha(REV / "assets.json"), "looks": recipes}
    (out / "manifest.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf8")
    shutil.copyfile(REV / "PHONE-CHECK.md", out / "README.md")
    shutil.copyfile(ROOT / "264/palette.json", out / "palette.json")
    archive = Path(shutil.make_archive(str(out), "zip", root_dir=out))
    print("PACK270", archive, sha(archive), flush=True)


if __name__ == "__main__":
    if "--" not in sys.argv or len(sys.argv[sys.argv.index("--")+1:]) != 1:
        raise SystemExit("Pass an unused output directory after --")
    path = Path(sys.argv[-1]).resolve()
    path.mkdir(parents=True, exist_ok=False)
    pack(path)
