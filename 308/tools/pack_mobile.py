"""Package revision 308 test fixtures and a content-deduplicated art delta."""
import json
import math
from pathlib import Path
import re
import shutil
import struct
import sys
from urllib.parse import unquote, urljoin, urlparse
import zipfile

import bpy
from mathutils import Vector

REV = Path(__file__).resolve().parents[1]
ROOT = REV.parent
sys.path.insert(0, str(ROOT / "295/tools"))
from pack_native import (apply_materials, asset_metrics, camera, configure, diagnostic_camera,
                         exr_depth, load_studio, material_overrides, sha, srgb, studio_info)

SOURCE_COMMIT = "7298fc4"
MOBILE_BASE = "d3066eec374cfa05fdba235adf66eca02332b5ed"
SIZES = (48, 64, 120, 512)
PALETTE = json.loads((ROOT / "235/face-palette209.json").read_text(encoding="utf8"))


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf8", newline="\n")


def source(uri, revision=308):
    if not uri:
        return None
    url = urljoin(f"http://preview/{revision}/", uri)
    path = ROOT / unquote(urlparse(url).path).lstrip("/")
    assert path.is_relative_to(ROOT) and ".." not in path.relative_to(ROOT).parts, uri
    assert path.is_file(), path
    return path


def add_asset(path, out, assets, digests):
    if path not in digests:
        digests[path] = sha(path)
    digest = digests[path]
    if digest not in assets:
        file = f"components/{digest}.glb"
        target = out / file
        target.parent.mkdir(exist_ok=True)
        shutil.copyfile(path, target)
        assets[digest] = {"file": file, "sha256": digest, **asset_metrics(target)}
    return {"asset": digest, "source": path.relative_to(ROOT).as_posix()}


def wardrobe(out, matrix):
    """Record the authored color bindings and supply the feminine jersey dyes."""
    variant = json.loads((REV / "wardrobe.json").read_text(encoding="utf8"))["Feminine"]["jersey"]
    jersey = {"default": {"embedded": True}}
    for color, uri in variant["atlases"].items():
        images = {}
        for kind, path in (("atlas", source(uri)),
                           ("pattern", ROOT / "213/colors" / f"jersey-{color}-pattern.png")):
            rel = f"textures/feminine-jersey-{color}-{kind}.png"
            target = out / rel
            target.parent.mkdir(exist_ok=True)
            shutil.copyfile(path, target)
            images[kind] = rel
        jersey[color] = images
    values = {
        "colors": matrix["colors"],
        "color_aliases": matrix["aliases"],
        "baked_hair_finishes": ["default", "ombre"],
        "original_brown_linear": [.160, .059, .030],
        "groom_tint_multiplier": .82,
        "feminine_jersey": {
            "dyes": jersey,
            "texture_bindings": {
                "atlas": "top material name containing 'jersey atlas'",
                "pattern": "other textured top materials containing 'Top / jersey' or 'jersey binding'",
                "sampler": "sRGB, repeating UVs, glTF V orientation",
            },
            "solid_fabric": "Apply selected top color to untextured 'Top /' fabric and preserve button finish.",
        },
        "hoodie_cavity_tint_multiplier": .48,
        "hoodie_facing_tint_multiplier": .78,
        "cap_and_scarf_fits": "Use resolved hair, lengths and headgear as independent roles.",
    }
    write_json(out / "appearance.json", values)
    write_json(out / "palette.json", PALETTE)
    return values


def provenance(matrix):
    urls = [*matrix["sourceURLs"], "/270/viewer.js", "/263/catalogue263.json", "/235/face-palette209.json"]
    return {path.relative_to(ROOT).as_posix(): sha(path) for path in map(source, urls)}


def bake_skin(index):
    for material in bpy.data.materials:
        if not material.use_nodes:
            continue
        bsdf = next((n for n in material.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
        if bsdf is None:
            continue
        for prefix, key in (("Skin","skin"), ("Face / ink209","ink"),
                            ("Face / lip209","lip"), ("Groom / stubble209","stubble")):
            if material.name.startswith(prefix):
                bsdf.inputs["Base Color"].default_value = (*PALETTE[key][index], 1)
                break
        if material.name.startswith("Chest / shade191"):
            ratio = float(material.name.split()[3])
            bsdf.inputs["Base Color"].default_value = (*(v*ratio for v in PALETTE["skin"][index]), 1)


def material_slots(overrides, authored):
    """Use authored GLB material indices for native overrides, including duplicate names."""
    names = {m["name"] for m in authored}
    maps = {}
    for binding, values in overrides.items():
        for name, value in values.items():
            source_name = name if name in names else re.sub(r"\.\d{3}$", "", name)
            assert source_name in names, name
            target = maps.setdefault(source_name, {})
            assert binding not in target or target[binding] == value
            target[binding] = value
    return {"role":"top","materials":[{"index":i,"name":mat["name"],**maps[mat["name"]]}
            for i,mat in enumerate(authored) if mat["name"] in maps]}


def bake_appearance(scene, row, out, appearance, top_materials):
    features = row["features"]
    overrides = material_overrides(row["build"]) if "lenses" in row["parts"] else {}
    if overrides:
        clear = features["lensTint"] == "clear"
        values = "DCE9EB" if clear else "1C2029"
        overrides["lenses"]["base_color_linear"] = [srgb(int(values[i:i+2],16)) for i in (0,2,4)]
        apply_materials(scene, overrides)
        for obj in scene.objects:
            if obj.type == "MESH" and obj.get("component269") == "lenses":
                for mat in obj.data.materials:
                    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
                    bsdf.inputs["Base Color"].default_value = (*overrides["lenses"]["base_color_linear"], 1)

    color = features["topColor"]
    if features["top"] != "jersey" or color == "default":
        return overrides, {}
    assert row["build"] == "Feminine"
    palette = {key: rgb for key, _, rgb in appearance["colors"]["top"]}
    rgb = palette[color].lstrip("#")
    linear = [srgb(int(rgb[i:i+2],16)) for i in (0,2,4)]
    dye = appearance["feminine_jersey"]["dyes"][color]
    applied = {"base_color_textures": {}, "solid_base_color_linear": {}}
    materials = {m for o in scene.objects if o.type == "MESH" and o.get("component269") == "top"
                 for m in o.data.materials}
    for material in sorted(materials, key=lambda m: m.name):
        nodes = material.node_tree.nodes
        bsdf = next(n for n in nodes if n.type == "BSDF_PRINCIPLED")
        image = next((node for node in nodes if node.type == "TEX_IMAGE"), None)
        name = material.name
        if image and ("Top / jersey" in name or "jersey binding" in name):
            kind = "atlas" if "jersey atlas" in name else "pattern"
            image.image = bpy.data.images.load(str(out / dye[kind]), check_existing=True)
            applied["base_color_textures"][name] = dye[kind]
        elif "Top /" in name:
            bsdf.inputs["Base Color"].default_value = (*linear, 1)
            applied["solid_base_color_linear"][name] = linear
    assert len(applied["base_color_textures"]) >= 2
    return overrides, material_slots(applied, top_materials)


def body_camera(scene, angle):
    target = Vector((0., 0., 1.28))
    yaw = {"front":0., "threequarter":-.464, "rear":math.pi}[angle]
    scene.camera.data.ortho_scale = 2.7
    scene.camera.location = target + Vector((8*math.sin(yaw), -8*math.cos(yaw), 0.))
    scene.camera.rotation_euler = (target - scene.camera.location).to_track_quat("-Z", "Y").to_euler()
    bpy.context.view_layer.update()
    return {"matrix_world": [list(row) for row in scene.camera.matrix_world],
            "ortho_scale": 2.7, "target": list(target),
            "clip_start": scene.camera.data.clip_start, "clip_end": scene.camera.data.clip_end}


def render_fixture(fixture_id, row, out, browser, assets, digests, appearance):
    target = out / "references" / fixture_id
    target.mkdir(parents=True)
    components = {role: add_asset(source(uri), out, assets, digests) for role, uri in row["parts"].items()}
    packed = {role: out / assets[part["asset"]]["file"] for role, part in components.items()}
    scene, studio = load_studio(row["build"], packed)
    scene.name = fixture_id
    scene["avatar_revision"] = "308"
    top_materials = assets[components["top"]["asset"]]["materials"]
    overrides, textures = bake_appearance(scene, row, out, appearance, top_materials)
    depth = configure(scene)
    bake_skin(0)
    camera(scene, "front", 512)
    depth.directory = "//"
    depth.file_name = "depth"
    scene.render.filepath = "//color.png"
    reference = target / "reference.blend"
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(reference), compress=True)
    info = studio_info(scene)
    depth.directory = str(target)

    def render(angle, skin, size, mode):
        bake_skin(skin)
        if mode == "body":
            camera_data = body_camera(scene, angle)
        elif mode == "face":
            camera_data = diagnostic_camera(scene, angle)
        else:
            camera_data = camera(scene, "front", size)
        scene.render.resolution_x = scene.render.resolution_y = size
        key = f"{'body-' if mode == 'body' else ''}{angle}-skin{skin}-{size}"
        depth.file_name = key + "-depth"
        color = target / (key + "-color.png")
        scene.render.filepath = str(color)
        bpy.ops.render.render(write_still=True)
        exr, = target.glob(key + "-depth*.exr")
        assert struct.unpack_from(">II", color.read_bytes(), 16) == (size, size)
        values = exr_depth(exr, size)
        assert ((values > 0) & (values < 100)).sum() > size**2 * .08
        web = target / (key + "-web.png")
        shutil.copyfile(browser / f"{fixture_id}-{key}-web.png", web)
        return {"angle": angle, "view": mode, "skin": skin, "size": size, "camera": camera_data,
                "alpha_threshold": .5, **{role: path.relative_to(out).as_posix()
                 for role, path in (("color", color), ("depth", exr), ("web_comparison", web))}}

    refs = [render("front", skin, size, "chat") for skin in range(4) for size in SIZES]
    diagnostics = [render(angle, 1, 512, "face") for angle in ("rightprofile", "rear")]
    if row["features"]["top"] == "jersey":
        diagnostics += [render(angle, 1, 768, "body") for angle in ("front","threequarter","rear")]
    print(f"{fixture_id}: {len(refs) + len(diagnostics)} color/depth pairs", flush=True)
    return {"id": fixture_id, "build": row["build"], "features": row["features"], "components": components,
            "scene": reference.relative_to(out).as_posix(), "scene_skin": 0, "studio": info,
            "studio_source_sha256": sha(studio), "appearance_overrides": overrides,
            "texture_overrides": textures, "references": refs, "diagnostics": diagnostics}


def write_stage(out, fixtures, assets):
    assemblies, looks = {}, []
    for key, fixture in fixtures.items():
        parts = []
        for role, part in fixture["components"].items():
            asset = assets[part["asset"]]
            level = {k:asset[k] for k in ("file","sha256","bytes","triangles")}
            parts.append({"id": f"{key}-{role}", "role": role,
                          "levels": {"portrait": level, "detail": level}})
        assemblies[key] = {"build":fixture["build"], "parts":parts, "features":fixture["features"],
                           "overrides":fixture["appearance_overrides"],
                           "texture_overrides":fixture["texture_overrides"],
                           "camera":fixture["references"][0]["camera"]}
        for skin in range(4):
            looks.append({"id": f"{key}-skin{skin}", "assembly_id":key, "build":fixture["build"],
                          "skin":skin, "eye":fixture["features"]["eyes"], "top":fixture["features"]["top"],
                          "groom":fixture["features"]["groom"], "hair_finish":fixture["features"]["hairColor"],
                          "top_color":fixture["features"]["topColor"]})
    messages = []
    for body in ("Where should we meet?", "I’m near the entrance.", "See you there.", "On my way."):
        for look in looks:
            index = len(messages)
            messages.append({"id": f"r308-row-{index:02d}", "sender": f"r308-sender-{index:02d}",
                             "display_name": f"{look['assembly_id'][5:]} {look['skin'] + 1}",
                             "appearance": look["id"], "body":body,"arrival_ms":0})
    seed = out / "fixtures/r308-visual.json"
    write_json(seed, {"name":"r308-visual","appearances":looks,"messages":messages})
    write_json(out / "mobile-stage.json", {
        "schema":"ravedio-art-lab-stage-1","art_revision":308,"mobile_base":MOBILE_BASE,
        "assemblies":assemblies,"palette":"palette.json",
        "seed":{"file":seed.relative_to(out).as_posix(),"name":"r308-visual","sha256":sha(seed),
                "rows":len(messages),"distinct_visual_keys":len(looks)},
        "portrait_framing":{"orthographic_span":1.35,"target_y":1.90},"chat_sizes_px":[48,64],
    })


def pack(out, kind, matrix, assets, data):
    shutil.copyfile(REV / "NATIVE-HANDOFF.md", out / "README.md")
    shutil.copyfile(REV / "tools/verify_mobile.py", out / "verify_mobile.py")
    files = {p.relative_to(out).as_posix():sha(p) for p in sorted(out.rglob("*")) if p.is_file() and p != out / "manifest.json"}
    write_json(out / "manifest.json", {
        "schema":"ravedio-art-308-handoff-1","package":kind,"revision":308,
        "artwork_commit":SOURCE_COMMIT,"mobile_base":MOBILE_BASE,
        "source_files":provenance(matrix),
        "coordinates":"glTF +Y up, +Z forward. Preserve authored node transforms.",
        "browser_studio":{"viewer":"270/viewer.js","tone_mapping":"ACESFilmic","exposure":.95},
        "assets":assets,"files":files,**data})
    archive = out.with_suffix(".zip")
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=3) as z:
        for p in sorted(out.rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(out).as_posix())
    digest = sha(archive)
    archive.with_suffix(".zip.sha256").write_text(f"{digest}  {archive.name}\n", encoding="ascii", newline="\n")
    print(f"PACKED {archive.name}: {archive.stat().st_size} bytes / {len(assets)} GLBs / {digest}", flush=True)
    return {"file":archive.name,"sha256":digest,"bytes":archive.stat().st_size,"glbs":len(assets)}


def fixtures_pack(browser, delivery, matrix, baseline):
    out = delivery / "Ravedio308-native-fixtures"
    out.mkdir()
    appearance = wardrobe(out, matrix)
    rows = json.loads((browser / "fixtures.json").read_text())
    assets, digests = {}, {}
    fixtures = {key: render_fixture(key, row, out, browser, assets, digests, appearance)
                for key, row in rows.items()}
    with zipfile.ZipFile(baseline) as z:
        prior = json.loads(z.read("manifest.json"))["fixtures"]
    control = {}
    for build, key in (("Feminine","r308-curls-pashmina"), ("Masculine","r308-flow-cap")):
        current, old = fixtures[key], prior[build]
        assert current["features"] == old["features"], key
        assert current["components"].keys() == old["components"].keys(), key
        control[key] = [role for role, part in current["components"].items()
                        if part["asset"] != old["components"][role]["sha256"]]
    write_stage(out, fixtures, assets)
    data = {"fixtures":fixtures,"changed_298_control_roles":control}
    receipt = pack(out,"fixtures",matrix,assets,data)
    return {**receipt,"fixtures":len(fixtures),
            "matched_pairs":sum(len(f["references"])+len(f["diagnostics"]) for f in fixtures.values()),
            "distinct_appearances":16,"seeded_rows":64,"changed_298_control_roles":control}


def catalogue_pack(delivery, before, after):
    out = delivery / "Ravedio308-catalogue-delta"
    out.mkdir()
    assets, digests = {}, {}
    wardrobe(out, after)

    def replacement(old, new, role):
        a, b = source(old,298), source(new,308)
        if a == b:
            return None
        for path in (a,b):
            if path and path not in digests:
                digests[path] = sha(path)
        if digests.get(a) == digests.get(b):
            return None
        return {"role":role,"before_sha256":digests.get(a),
                "target":add_asset(b,out,assets,digests) if b else None}

    assert before["rows"].keys() == after["rows"].keys()
    assert before["grooms"].keys() == after["grooms"].keys()
    entries = {}
    for key, roles in after["rows"].items():
        changes = [change for role, uri in roles.items()
                   if (change := replacement(before["rows"][key][role],uri,"sprout" if role=="extra" else role))]
        if changes:
            entries[key] = changes
    grooms = {key: change for key, uri in after["grooms"].items()
              if (change := replacement(before["grooms"][key],uri,"groom"))}
    delta = {"schema":"ravedio-catalogue-delta-1","base_revision":298,"revision":308,
             "selector_fields":["build","hair","headwear","top","baked_hair_finish"],
             "scanned_selections":len(after["rows"]),"entries":entries,"grooms":grooms,
             "base_source_files":provenance(before)}
    write_json(out / "catalogue-delta.json", delta)
    receipt = pack(out,"catalogue-delta",after,assets,{"delta":"catalogue-delta.json"})
    return {**receipt,"scanned_selections":len(after["rows"]),"changed_selections":len(entries),
            "groom_updates":len(grooms)}


if __name__ == "__main__":
    browser, delivery, baseline = map(Path,sys.argv[-3:])
    selectors = json.loads((browser / "selectors.json").read_text())
    result = {"art_revision":308,"artwork_commit":SOURCE_COMMIT,"mobile_base":MOBILE_BASE}
    result["fixtures"] = fixtures_pack(browser,delivery,selectors["308"],baseline)
    result["catalogue_delta"] = catalogue_pack(delivery,selectors["298"],selectors["308"])
    write_json(delivery / "native-archive.json", result)
