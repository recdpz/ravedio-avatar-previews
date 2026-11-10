"""Render chat-only illustrations from the same source geometry as the studio portraits."""
from argparse import ArgumentParser
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "314/tools/handoff"))
from render import change_parts

# Two same-skin pairs deliberately test silhouette and accessory recognition.
LOOKS = (
    ("ponytail", "Ponytail", "Feminine/ponytail/none/jersey/ombre", 0, "none", "none"),
    ("fringe", "Long bangs + reading glasses", "Feminine/side-sweep/none/jersey/default", 1, "none", "reading"),
    ("buns", "Space buns", "Feminine/space-buns/none/jersey/default", 2, "none", "none"),
    ("braids", "Box braids", "Feminine/box-braids/none/jersey/default", 2, "none", "none"),
    ("pashmina", "Pashmina", "Feminine/ponytail/pashmina/jersey/default", 3, "none", "none"),
    ("afro", "Afro", "Masculine/afro/none/sweatshirt/default", 0, "none", "none"),
    ("cap", "Flow + cap + long beard", "Masculine/flow/cap/sweatshirt/default", 3, "long", "none"),
    ("beanie", "Taper + beanie + short beard", "Masculine/taper/beanie/sweatshirt/default", 3, "short", "none"),
)
ICON_SPAN = 1.12
ICON_Z = 1.86


def load(path):
    return json.loads(path.read_bytes())


def simple_material(material, role):
    if not material or not material.use_nodes:
        return
    tree = material.node_tree
    nodes, links = tree.nodes, tree.links
    source = next((node for node in nodes if node.type == "BSDF_PRINCIPLED"), None)
    output = next((node for node in nodes if node.type == "OUTPUT_MATERIAL" and node.is_active_output), None)
    if not source or not output:
        return

    normal = nodes.new("ShaderNodeNewGeometry")
    transform = nodes.new("ShaderNodeVectorTransform")
    transform.vector_type = "NORMAL"
    transform.convert_from, transform.convert_to = "WORLD", "CAMERA"
    links.new(normal.outputs["Normal"], transform.inputs[0])
    dot = nodes.new("ShaderNodeVectorMath")
    dot.operation = "DOT_PRODUCT"
    dot.inputs[1].default_value = Vector((-.53, .64, .55)).normalized()
    links.new(transform.outputs[0], dot.inputs[0])
    ramp = nodes.new("ShaderNodeMapRange")
    ramp.clamp = True
    ramp.inputs["From Min"].default_value = -.45
    ramp.inputs["From Max"].default_value = 1
    # Broad facial fill keeps dark skin legible. A stronger range on hair
    # brings back the sculpted coils and braid ridges without specular glare.
    low, high = {
        "base": (.57, 1.05),
        "hair": (.40, 1.26),
        "groom": (.50, 1.12),
        "headgear": (.50, 1.13),
    }.get(role, (.48, 1.05))
    if material.name.startswith("Beanie / knit"):
        # Separate the lighter knit crown from the rolled cuff and navy cap.
        low, high = .76, 1.42
    ramp.inputs["To Min"].default_value = low
    ramp.inputs["To Max"].default_value = high
    links.new(dot.outputs["Value"], ramp.inputs["Value"])

    shade = nodes.new("ShaderNodeMixRGB")
    shade.blend_type = "MULTIPLY"
    shade.inputs[0].default_value = 1
    color = source.inputs["Base Color"]
    shade.inputs[1].default_value = color.default_value
    if color.is_linked:
        links.new(color.links[0].from_socket, shade.inputs[1])
    links.new(ramp.outputs[0], shade.inputs[2])

    emission = nodes.new("ShaderNodeEmission")
    links.new(shade.outputs[0], emission.inputs["Color"])
    final = emission.outputs[0]
    alpha = source.inputs["Alpha"]
    if role == "lenses" or alpha.is_linked or alpha.default_value < .999:
        # Keep eyes visible through clear lenses and retain authored taper opacity.
        transparent = nodes.new("ShaderNodeBsdfTransparent")
        mix = nodes.new("ShaderNodeMixShader")
        mix.inputs[0].default_value = .075 if role == "lenses" else alpha.default_value
        if role != "lenses" and alpha.is_linked:
            links.new(alpha.links[0].from_socket, mix.inputs[0])
        links.new(transparent.outputs[0], mix.inputs[1])
        links.new(final, mix.inputs[2])
        final = mix.outputs[0]
    links.new(final, output.inputs["Surface"])


def main():
    parser = ArgumentParser(description=__doc__)
    for key in ("work", "tools", "output"):
        parser.add_argument(key, type=Path)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    sys.path.insert(0, str(args.tools))
    from chat_portrait_blender import reduce_clear_lens_glare
    from render_chat_review_blender import recolor

    art = args.work / "native322"
    packed = args.work / "native321/handoff"
    catalogue = load(art / "catalogue.json")
    references = load(packed / "fixtures.json")["fixtures"]
    palette = load(art / "palette.json")
    output = args.output
    (output / "raw").mkdir(parents=True, exist_ok=True)
    preferences = bpy.context.preferences.addons["cycles"].preferences
    preferences.compute_device_type = "CUDA"
    preferences.get_devices()
    for adapter in preferences.devices:
        adapter.use = adapter.type == "CUDA"
    device = "GPU" if any(adapter.use for adapter in preferences.devices) else "CPU"
    rows = []
    for name, label, selector, skin, groom, glasses in LOOKS:
        build, _, _, _, _ = selector.split("/")
        feminine = build == "Feminine"
        fixture_name = "r321-ponytail-jersey" if feminine else "r321-flow-long-beard"
        fixture = references[fixture_name]
        scene_file = packed / f"scenes/{fixture_name}.blend"
        bpy.ops.wm.open_mainfile(filepath=str(scene_file))
        scene = bpy.context.scene
        frame = catalogue["fit_rows"][selector]
        independent = catalogue["independent_roles"][build]
        old = {role: value["sha256"] for role, value in fixture["parts"].items()}
        fitted = {**old, **{role: frame[role] for role in ("hair", "headgear", "top")}}
        fitted["groom"] = independent["grooms"][groom]
        fitted["mouth"] = catalogue["groom_mouths"].get(groom, independent["faces"]["bean"]["mouth"])
        if glasses != "none":
            lens_set = independent["glasses"][glasses]
            fitted["glasses"], fitted["lenses"] = lens_set["glasses"], lens_set["lenses"]["clear"]
        fitted = {role: key for role, key in fitted.items() if key}
        parts = {role: str(art / catalogue["components"][key]["file"]) for role, key in fitted.items()}
        sources = {role: parts[role] if old[role] == fitted.get(role) else "packed" for role in old}
        change_parts(scene, sources, parts)
        recolor(scene, palette, skin)
        materials = {}
        for obj in scene.objects:
            if obj.type == "MESH":
                for material in obj.data.materials:
                    if material:
                        materials.setdefault(material, obj.get("component269"))
        if glasses != "none":
            reduce_clear_lens_glare(material for material, role in materials.items() if role == "lenses")

        scene.render.use_compositing = False
        scene.render.film_transparent = True
        scene.render.resolution_x = scene.render.resolution_y = 384
        scene.render.resolution_percentage = 100
        scene.render.image_settings.file_format = "PNG"
        scene.render.image_settings.color_mode = "RGBA"
        scene.cycles.device = device
        scene.cycles.samples = 24
        for mode in ("studio", "icon"):
            if mode == "icon":
                for material, role in materials.items():
                    simple_material(material, role)
                scene.view_settings.view_transform = "Standard"
                scene.view_settings.look = "None"
                scene.view_settings.exposure = 0
                scene.view_settings.gamma = 1
                scene.camera.data.ortho_scale = ICON_SPAN
                # Raise the orthographic framing without changing the face angle.
                scene.camera.location.z += ICON_Z - 1.805
            scene.render.filepath = str(output / "raw" / f"{name}-{mode}.png")
            bpy.ops.render.render(write_still=True)
        rows.append(dict(id=name, label=label, selector=selector, skin=skin, groom=groom, glasses=glasses, parts=fitted))
    (output / "looks.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf8")


if __name__ == "__main__":
    main()
