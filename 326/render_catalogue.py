"""Build the catalogue phone-review matrix from verified fitted source components."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "314/tools/handoff"))
from render import change_parts

# One appearance for each unoccluded haircut. Subsequent rows exercise fitted
# headwear against high-risk hair. Tops, bottoms, eye shapes and details vary
# across the same matrix so the native review stays quick to navigate.
# Build, hair, headwear, top, bottom, eyes, groom, glasses, lens, extra, skin, hair finish.
CASES = (
    ("F", "ponytail", "none", "jersey", "pants", "bean", "none", "none", "clear", "none", 0, "ombre"),
    ("M", "taper", "none", "tshirt", "pants", "original", "short", "none", "clear", "none", 3, "default"),
    ("F", "straight", "none", "open", "skirt", "tapered", "none", "rectangular", "clear", "none", 1, "default"),
    ("M", "buzz", "none", "tank", "shorts", "hooded", "stubble", "none", "clear", "hot", 2, "default"),
    ("F", "curls", "none", "tank", "shorts", "original", "none", "none", "clear", "none", 3, "default"),
    ("M", "curly-top", "none", "jersey", "shorts", "bean", "goatee", "wayfarer", "dark", "none", 0, "default"),
    ("F", "box-braids", "none", "triangle", "bikini", "hooded", "none", "none", "clear", "none", 2, "default"),
    ("M", "afro", "none", "shirtless", "shorts", "tapered", "none", "none", "clear", "none", 3, "default"),
    ("F", "space-buns", "none", "strappy", "shorts", "bean", "none", "heart", "dark", "none", 2, "default"),
    ("M", "flow", "none", "sweatshirt", "pants", "original", "long", "none", "clear", "none", 1, "default"),
    ("F", "side-sweep", "none", "sweatshirt", "pants", "tapered", "none", "reading", "clear", "none", 0, "default"),
    ("M", "locs", "none", "buttonup", "shorts", "hooded", "mustache", "wraparound", "dark", "none", 3, "ombre"),
    ("F", "twin-braids", "none", "tshirt", "skirt", "original", "none", "none", "clear", "sprout", 1, "default"),
    ("M", "middle-part", "none", "tshirt", "pants", "bean", "patch", "none", "clear", "none", 2, "default"),
    ("F", "bob", "none", "bandeau", "shorts", "hooded", "none", "cat-eye", "dark", "none", 3, "default"),
    ("M", "sidepart", "none", "buttonup", "pants", "tapered", "none", "kaleidoscope", "dark", "none", 1, "default"),
    ("F", "ponytail", "cap", "jersey", "pants", "bean", "none", "reading", "clear", "none", 2, "default"),
    ("M", "flow", "cap", "sweatshirt", "pants", "bean", "long", "none", "clear", "none", 3, "default"),
    ("F", "ponytail", "beanie", "jersey", "shorts", "original", "none", "none", "clear", "none", 1, "default"),
    ("M", "taper", "beanie", "sweatshirt", "pants", "bean", "short", "none", "clear", "none", 3, "default"),
    ("F", "ponytail", "headband", "open", "pants", "tapered", "none", "none", "clear", "none", 0, "default"),
    ("M", "afro", "cowboy", "buttonup", "shorts", "original", "none", "none", "clear", "none", 2, "default"),
    ("F", "space-buns", "headband", "tshirt", "pants", "bean", "none", "none", "clear", "none", 2, "default"),
    ("M", "curly-top", "bucket", "tshirt", "shorts", "hooded", "stubble", "none", "clear", "none", 1, "default"),
    ("F", "curls", "pashmina", "open", "pants", "bean", "none", "rectangular", "clear", "none", 3, "default"),
    ("F", "box-braids", "pashmina", "jersey", "skirt", "original", "none", "none", "clear", "none", 2, "default"),
    ("F", "bob", "ears", "tshirt", "shorts", "hooded", "none", "none", "clear", "none", 0, "default"),
    ("M", "middle-part", "headband", "jersey", "pants", "tapered", "none", "none", "clear", "none", 0, "default"),
)


def load(path):
    return json.loads(path.read_bytes())


def select(catalogue, row):
    key, hair, headwear, top, bottom, eye, groom, glasses, tint, extra, skin, finish = row
    build = {"F": "Feminine", "M": "Masculine"}[key]
    selector = f"{build}/{hair}/{headwear}/{top}/{finish}"
    fit = catalogue["fit_rows"][selector]
    independent = catalogue["independent_roles"][build]
    face = independent["faces"][eye]
    parts = {role: fit[role] for role in ("hair", "hairLengths", "top", "headgear")}
    parts.update(base=independent["bases"][bottom]["shirtless" if top == "shirtless" else "clothed"],
                 bottom=independent["bottoms"][bottom], eyes=face["eyes"], lashes=face["lashes"],
                 groom=independent["grooms"][groom],
                 mouth=catalogue["groom_mouths"].get(groom, face["mouth"]))
    if glasses != "none":
        lenses = independent["glasses"][glasses]
        parts.update(glasses=lenses["glasses"], lenses=lenses["lenses"][tint])
    if extra != "none":
        parts["extra"] = fit["sprout"] if extra == "sprout" else independent["hot"]
    identity = f"{key.lower()}-{hair}-{headwear}"
    names = catalogue["options"]
    label = names["builds"][build]["hair"][hair]
    if headwear != "none":
        label += " + " + names["headwear"][headwear]
    return dict(id=identity, label=label, build=build, skin=skin, eye=eye, groom=groom,
                hair_tone=0, top=top, top_tone=0, bottom=bottom, glasses=glasses, lens=tint,
                extra=extra, selector=selector, parts={role: digest for role, digest in parts.items() if digest})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ("work", "tools", "output"):
        parser.add_argument(key, type=Path)
    parser.add_argument("--only", nargs="+")
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    sys.path.insert(0, str(args.tools))
    from chat_portrait_blender import reduce_clear_lens_glare
    from render_chat_review_blender import recolor

    art = args.work / "native322"
    packed = args.work / "native321/handoff"
    catalogue = load(art / "catalogue.json")
    references = load(packed / "fixtures.json")["fixtures"]
    palette = load(art / "palette.json")
    out = args.output
    (out / "raw").mkdir(parents=True, exist_ok=True)
    rows = [select(catalogue, row) for row in CASES]
    assert len({row["id"] for row in rows}) == len(rows)
    (out / "looks.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf8")
    preferences = bpy.context.preferences.addons["cycles"].preferences
    preferences.compute_device_type = "CUDA"
    preferences.get_devices()
    for adapter in preferences.devices:
        adapter.use = adapter.type == "CUDA"
    device = "GPU" if any(adapter.use for adapter in preferences.devices) else "CPU"
    checked = set()
    for row in rows:
        if args.only and row["id"] not in args.only:
            continue
        fixture = "r321-ponytail-jersey" if row["build"] == "Feminine" else "r321-flow-long-beard"
        bpy.ops.wm.open_mainfile(filepath=str(packed / f"scenes/{fixture}.blend"))
        scene = bpy.context.scene
        old = {role: item["sha256"] for role, item in references[fixture]["parts"].items()}
        targets = {}
        for role, digest in row["parts"].items():
            path = art / catalogue["components"][digest]["file"]
            if digest not in checked:
                assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
                checked.add(digest)
            targets[role] = str(path)
        origins = {role: targets[role] if digest == row["parts"].get(role) else "packed" for role, digest in old.items()}
        change_parts(scene, origins, targets)
        recolor(scene, palette, row["skin"])
        if row["glasses"] != "none" and row["lens"] == "clear":
            reduce_clear_lens_glare(m for ob in scene.objects if ob.type == "MESH" and ob.get("component269") == "lenses"
                                   for m in ob.data.materials)
        for ob in scene.objects:
            if ob.type == "MESH" and ob.get("component269") == "top":
                ob.visible_glossy = False
        scene.render.use_compositing = False
        scene.render.film_transparent = True
        scene.render.resolution_x = scene.render.resolution_y = 384
        scene.render.resolution_percentage = 100
        scene.render.image_settings.file_format = "PNG"
        scene.render.image_settings.color_mode = "RGBA"
        scene.cycles.device = device
        scene.cycles.samples = 24
        scene.render.filepath = str(out / "raw" / (row["id"] + ".png"))
        bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
