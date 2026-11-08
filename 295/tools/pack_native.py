"""Package the selected artwork for the two existing Development avatar labs."""
import hashlib
import json
import math
import shutil
import struct
import sys
from pathlib import Path

import bpy
from mathutils import Vector

REV = Path(__file__).resolve().parents[1]
ROOT = REV.parent
sys.path.insert(0, str(ROOT / "294/tools"))
from repair import local_path, read_glb
sys.path.insert(0, str(ROOT / "269/tools"))
from render_references import camera, configure, load_studio, skin_tone
from verify_delivery import exr_depth


SIZES = (48, 64, 120, 512)
FIXTURE_IDS = {"Feminine": "r295-curls-pashmina", "Masculine": "r295-flow-cap"}
PALETTE = ROOT / "264/palette.json"


def sha(path):
    with path.open("rb") as file:
        return hashlib.file_digest(file, "sha256").hexdigest()


def srgb(value):
    value /= 255
    return value / 12.92 if value <= .04045 else ((value + .055) / 1.055)**2.4


def material_overrides(build):
    selected = json.loads((ROOT / "263/catalogue263.json").read_text(encoding="utf8"))
    frame = next(x[2] for x in selected["colors"]["frames"] if x[0] == "black").lstrip("#")
    return {
        "glasses": {
            "base_color_linear": [srgb(int(frame[i:i+2], 16)) for i in (0, 2, 4)],
            "metallic": .08, "roughness": .28,
        },
        "lenses": {
            "alpha_mode": "BLEND", "opacity": .075 if build == "Feminine" else .84,
            "roughness": .025, "ior": 1, "transmission": 0,
            "double_sided": False, "depth_write": False,
        },
    }


def apply_materials(scene, choices):
    for role, values in choices.items():
        materials = {m for obj in scene.objects if obj.type == "MESH" and obj.get("component269") == role
                     for m in obj.data.materials}
        assert materials, role
        for material in materials:
            bsdf = next(n for n in material.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
            if role == "glasses":
                bsdf.inputs["Base Color"].default_value = (*values["base_color_linear"], 1)
                bsdf.inputs["Metallic"].default_value = values["metallic"]
            else:
                bsdf.inputs["Alpha"].default_value = values["opacity"]
                bsdf.inputs["IOR"].default_value = values["ior"]
                bsdf.inputs["Transmission Weight"].default_value = 0.
                # Match the preview's front-face lens policy in the Cycles reference.
                nodes, links = material.node_tree.nodes, material.node_tree.links
                output = next(n for n in nodes if n.type == "OUTPUT_MATERIAL" and n.is_active_output)
                shader = output.inputs["Surface"].links[0].from_socket
                back = nodes.new("ShaderNodeNewGeometry")
                mix = nodes.new("ShaderNodeMixShader")
                transparent = nodes.new("ShaderNodeBsdfTransparent")
                links.new(back.outputs["Backfacing"], mix.inputs[0])
                links.new(shader, mix.inputs[1])
                links.new(transparent.outputs[0], mix.inputs[2])
                links.new(mix.outputs[0], output.inputs["Surface"])
                material.use_backface_culling = True
            bsdf.inputs["Roughness"].default_value = values["roughness"]


def asset_metrics(path):
    model, binary = read_glb(path)
    assert not {"KHR_draco_mesh_compression", "EXT_meshopt_compression", "KHR_mesh_quantization"}.intersection(
        model.get("extensionsUsed", []))
    primitives = [p for node in model["nodes"] if "mesh" in node
                  for p in model["meshes"][node["mesh"]]["primitives"]]
    images = []
    for image in model.get("images", []):
        view = model["bufferViews"][image["bufferView"]]
        start = view.get("byteOffset", 0)
        assert image["mimeType"] == "image/png" and binary[start:start+8] == b"\x89PNG\r\n\x1a\n"
        width, height = struct.unpack_from(">II", binary, start + 16)
        images.append({"name": image.get("name", ""), "mime_type": image["mimeType"],
                       "width": width, "height": height, "bytes": view["byteLength"]})
    assert all(p.get("mode", 4) == 4 for p in primitives)
    return {
        "bytes": path.stat().st_size,
        "triangles": sum(model["accessors"][p["indices"]]["count"] // 3 if "indices" in p
                         else model["accessors"][p["attributes"]["POSITION"]]["count"] // 3 for p in primitives),
        "primitives": len(primitives),
        "material_count": len(model.get("materials", [])),
        "materials": model.get("materials", []),
        "textures": images,
        "extensions_used": model.get("extensionsUsed", []),
        "extensions_required": model.get("extensionsRequired", []),
    }


def studio_info(scene):
    return {
        "lights": [{"type": o.data.type, "name": o.name, "energy": o.data.energy,
                    "color": list(o.data.color), "shape": o.data.shape,
                    "size": o.data.size, "size_y": o.data.size_y,
                    "matrix_world": [list(row) for row in o.matrix_world]}
                   for o in scene.objects if o.type == "LIGHT"],
        "world": scene.world.name if scene.world else None,
        "world_surface": [{"type": n.bl_idname, "color": list(n.inputs["Color"].default_value),
                           "strength": n.inputs["Strength"].default_value}
                          for n in scene.world.node_tree.nodes if n.type == "BACKGROUND"],
        "color_management": {k: getattr(scene.view_settings, k)
                             for k in ("view_transform", "look", "exposure", "gamma")},
        "engine": "CYCLES",
        "samples": scene.cycles.samples, "seed": scene.cycles.seed,
        "denoise": scene.cycles.use_denoising, "transparent_background": scene.render.film_transparent,
    }


def diagnostic_camera(scene, angle):
    target = Vector((0, 0, 1.88))
    yaw = math.pi / 2 if angle == "rightprofile" else math.pi
    scene.camera.data.type = "ORTHO"
    scene.camera.data.ortho_scale = 1.50
    scene.camera.location = target + Vector((8 * math.sin(yaw), -8 * math.cos(yaw), 0))
    scene.camera.rotation_euler = (target - scene.camera.location).to_track_quat("-Z", "Y").to_euler()
    bpy.context.view_layer.update()
    return {"matrix_world": [list(row) for row in scene.camera.matrix_world],
            "ortho_scale": scene.camera.data.ortho_scale, "target": list(target),
            "clip_start": scene.camera.data.clip_start, "clip_end": scene.camera.data.clip_end}


def stage(build, row, out, browser, art_revision):
    target = out / build
    (target / "components").mkdir(parents=True)
    packed, components = {}, {}
    for slot, uri in row["parts"].items():
        source = local_path(uri)
        destination = target / "components" / f"{slot}.glb"
        packed[slot] = Path(shutil.copyfile(source, destination))
        components[slot] = {"file": destination.relative_to(out).as_posix(),
                            "source": source.relative_to(ROOT).as_posix(),
                            "sha256": sha(destination), **asset_metrics(destination)}
        assert components[slot]["sha256"] == sha(source)
    assert {"hair", "headgear", "glasses", "lenses", "extra", "top", "bottom"} <= packed.keys()
    assert all(m["alphaMode"] == "BLEND" and
               not {"KHR_materials_transmission", "KHR_materials_volume"}.intersection(m.get("extensions", {}))
               for m in components["lenses"]["materials"])
    scene, studio = load_studio(build, packed)
    scene.name = f"Ravedio {art_revision} {build}"
    scene["avatar_revision"] = str(art_revision)
    overrides = material_overrides(build)
    apply_materials(scene, overrides)
    depth = configure(scene)
    depth.directory = "//"
    depth.file_name = "depth"
    scene.render.filepath = "//color.png"
    skin_tone(0)
    camera(scene, "front", 512)
    reference = target / "reference.blend"
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(reference), compress=True)
    depth.directory = str(target)
    info = studio_info(scene)
    pairs = []
    for tone in (0, 3):
        skin_tone(tone)
        for size in SIZES:
            cam = camera(scene, "front", size)
            name = f"front-skin{tone}-{size}"
            depth.file_name = name + "-depth"
            color = target / (name + "-color.png")
            scene.render.filepath = str(color)
            bpy.ops.render.render(write_still=True)
            exr, = target.glob(name + "-depth*.exr")
            assert struct.unpack_from(">II", color.read_bytes(), 16) == (size, size)
            values = exr_depth(exr, size)
            assert ((values > 0) & (values < 100)).sum() > size**2 * .12
            web = target / (name + "-web.png")
            shutil.copyfile(browser / f"fixture-{build}-skin{tone}-{size}-front.png", web)
            pairs.append({
                "size": size, "skin": tone, "camera": cam, "alpha_threshold": .5,
                "color": color.relative_to(out).as_posix(), "depth": exr.relative_to(out).as_posix(),
                "web_comparison": web.relative_to(out).as_posix(),
            })
            print(f"REFERENCE{art_revision}", build, name, flush=True)
    diagnostics = []
    skin_tone(1)
    for angle in ("rightprofile", "rear"):
        cam = diagnostic_camera(scene, angle)
        name = f"{angle}-skin1-512"
        depth.file_name = name + "-depth"
        color = target / (name + "-color.png")
        scene.render.filepath = str(color)
        bpy.ops.render.render(write_still=True)
        exr, = target.glob(name + "-depth*.exr")
        values = exr_depth(exr, 512)
        assert ((values > 0) & (values < 100)).sum() > 512**2 * .12
        web = target / (name + "-web.png")
        shutil.copyfile(browser / f"fixture-{build}-fit-{angle}.png", web)
        diagnostics.append({
            "angle": angle, "skin": 1, "size": 512, "camera": cam, "alpha_threshold": .5,
            "color": color.relative_to(out).as_posix(), "depth": exr.relative_to(out).as_posix(),
            "web_comparison": web.relative_to(out).as_posix(),
        })
    return {
        "id": FIXTURE_IDS[build].replace("r295-", f"r{art_revision}-", 1), "features": row["features"], "tones": [0, 3],
        "scene": reference.relative_to(out).as_posix(), "scene_skin": 0,
        "studio_source_sha256": sha(studio), "studio": info,
        "components": components, "appearance_overrides": overrides, "references": pairs, "diagnostics": diagnostics,
    }


def pack(receipt, out, art_revision=295, stage_extra=None):
    report = json.loads(receipt.read_text(encoding="utf8"))
    assert report["revision"] == str(art_revision)
    out.mkdir(parents=True, exist_ok=False)
    fixtures = {build: stage(build, row, out, receipt.parent, art_revision) for build, row in report["fixtures"].items()}
    shutil.copyfile(PALETTE, out / "palette.json")
    source_revision = ROOT / str(art_revision)
    shutil.copyfile(source_revision / "NATIVE-HANDOFF.md", out / "README.md")
    shutil.copyfile(REV / "tools/verify_archive.py", out / "verify_archive.py")
    if stage_extra is not None:
        stage_extra(out, fixtures)
    hashes = {p.relative_to(out).as_posix(): sha(p) for p in sorted(out.rglob("*")) if p.is_file()}
    manifest = {
        "schema": "ravedio-native-art-fixtures-1", "revision": art_revision,
        "source_catalogue": {"file": f"{art_revision}/hair-fits.json", "sha256": sha(source_revision / "hair-fits.json")},
        "coordinates": "glTF +Y up and +Z forward. Preserve authored node transforms.",
        "web_comparison": {"studio": "270 viewer", "viewer_sha256": sha(ROOT / "270/viewer.js"),
                           "exposure": .95, "tone_mapping": "ACESFilmic",
                           "lighting": "existing browser environment and fixed directional panels",
                           "camera": "front, span 1.35, target y=1.90"},
        "fixtures": fixtures, "files": hashes,
    }
    if art_revision != 295:
        scarf = source_revision / "pashmina-fits.json"
        manifest["scarf_catalogue"] = {"file": f"{art_revision}/pashmina-fits.json", "sha256": sha(scarf)}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf8", newline="\n")
    archive = Path(shutil.make_archive(str(out), "zip", root_dir=out))
    print(f"PACK{art_revision}", archive, sha(archive), flush=True)


if __name__ == "__main__":
    pack(Path(sys.argv[-2]), Path(sys.argv[-1]))