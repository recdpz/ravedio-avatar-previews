"""Compare three different end treatments in the packed revision 330 studio."""
from argparse import ArgumentParser
from pathlib import Path
import math
import sys

import bpy
from mathutils import Matrix, Vector
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "327/tools"))
from build_lob import cartesian, ease, keep_head_room, polar
from drape import CENTER, islands, warp_normals

DIRECTIONS = ("current", "feathered", "flipped", "tucked")
ANGLES = {"front": (0, 0), "threequarter": (-33, 0), "profile": (-90, 0),
          "rear": (180, 0), "rightprofile": (90, 0), "rearquarter": (-144, 0),
          "above": (-33, 36), "underneath": (-33, -24)}
# glTF x/y/z to Blender x/-z/y.
TO_BLENDER = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]])
FINISH = {"feathered": (.40, .28, .34), "flipped": (.36, .34, .32), "tucked": (.35, .47, .29)}


def lock_profile(points):
    theta, _, radius = polar(points)
    height = points[:, 1]
    low = height.min()
    tip = float(theta[height.argmin()])
    relative = (theta - tip + np.pi) % (2 * np.pi) - np.pi
    levels = np.linspace(low, 1.94, 35)
    # Fit a center at each height from the vertices of the original lock.
    weights = np.exp(-.5 * ((levels[:, None] - height) / .013)**2)
    weights /= weights.sum(axis=1, keepdims=True)
    axis = weights @ relative
    depth = weights @ radius

    def sample(h):
        return np.interp(h, levels, axis), np.interp(h, levels, depth)

    return tip, low, sample


def section_shape(points, tip, low, profile, style):
    theta, y, radius = polar(points)
    h = points[:, 1]
    relative = (theta - tip + np.pi) % (2 * np.pi) - np.pi
    axis, center = profile(h)
    across = relative - axis
    bottom = ease((1.76 - h) / (1.76 - low))
    outer = ease((radius - center) / .014)
    variation = np.sin(8 * tip + .65)

    if style == "feathered":
        # Flatten the end into a fine blade. Two shallow channels follow the sweep.
        theta = tip + axis + across * (1 - .45 * bottom) + .051 * bottom * variation
        radius = center + (radius - center) * (1 - .51 * bottom)
        groove = np.exp(-((across - .023) / .009)**2) + .60 * np.exp(-((across + .031) / .010)**2)
        fade = ease((1.91 - h) / .13) * ease((h - low) / .058)
        radius -= .0028 * groove * fade * outer
        y += bottom * (.012 + .014 * variation)
    elif style == "flipped":
        # Brush the lower section inward first, then roll thin edges up and out.
        bend = ease((1.80 - h) / (1.80 - low))
        kick = bend**1.35
        side = np.sin(3 * tip + .42)
        theta = tip + axis + across * (1 - .28 * bottom) + kick * (.082 * side + .079 * np.sin(tip))
        radius = center + (radius - center) * (1 - .39 * bottom)
        radius -= .005 * np.sin(np.pi * bend)**2
        radius += (.039 + .008 * variation) * kick
        y += (.015 + .010 * side) * kick
    else:
        # Keep a more even line around the nape and roll the thin edge inward.
        face = 1 - ease((abs(tip) - 1.48) / .50)
        hem = 1.518 + .017 * face + .008 * variation
        shoulder, _ = profile(1.84)
        endpoint, _ = profile(low)
        straight = np.interp(h, (low, 1.84), (endpoint, shoulder))
        tuck = .16 * bottom * np.sin(tip) * face
        theta = tip + axis + across * (1 - .19 * bottom) + tuck
        theta += .47 * ease((1.85 - h) / .19) * (straight - axis)
        radius = center + (radius - center) * (1 - .48 * bottom) - .027 * bottom
        y += (hem - low) * bottom

    return keep_head_room(points, cartesian(theta, y, radius))


def refine(scene, style):
    roughness, coat, coat_roughness = FINISH[style]
    hair = [obj for obj in scene.objects if obj.type == "MESH" and obj.get("component269") == "hair"]
    assert len(hair) == 4
    for obj in hair:
        for material in obj.data.materials:
            shader = next(node for node in material.node_tree.nodes if node.type == "BSDF_PRINCIPLED")
            shader.inputs["Roughness"].default_value = roughness
            shader.inputs["Coat Weight"].default_value = coat
            shader.inputs["Coat Roughness"].default_value = coat_roughness
        if "Bob / side sweep" not in obj.data.name:
            continue
        assert obj.matrix_world == Matrix.Identity(4)
        mesh = obj.data
        count = len(mesh.vertices)
        xyz, normals = (np.empty(count * 3, dtype=np.float32) for _ in range(2))
        mesh.vertices.foreach_get("co", xyz)
        mesh.vertices.foreach_get("normal", normals)
        p = xyz.reshape((-1, 3)) @ TO_BLENDER.T
        n = normals.reshape((-1, 3)) @ TO_BLENDER.T
        mesh.calc_loop_triangles()
        triangles = np.empty(len(mesh.loop_triangles) * 3, dtype=np.int32)
        mesh.loop_triangles.foreach_get("vertices", triangles)
        label = islands(p, triangles.reshape((-1, 3)))
        moved, shading = p.copy(), n.copy()
        for key in np.unique(label):
            member = label == key
            tip, low, profile = lock_profile(p[member])
            def flow(coords):
                return section_shape(coords, tip, low, profile, style)

            moved[member] = flow(p[member])
            shading[member] = warp_normals(flow, p[member], n[member])
        assert np.isfinite(moved).all() and np.isfinite(shading).all()
        mesh.vertices.foreach_set("co", (moved @ TO_BLENDER).ravel())
        mesh.update()
        mesh.normals_split_custom_set_from_vertices((shading @ TO_BLENDER).tolist())


def render(base, output, quick, directions):
    review = output / "review"
    review.mkdir(parents=True, exist_ok=True)
    bpy.context.preferences.filepaths.save_version = 0
    for style in directions:
        bpy.ops.wm.open_mainfile(filepath=str(base))
        scene = bpy.context.scene
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.compute_device_type = "CUDA"
        prefs.get_devices()
        for device in prefs.devices:
            device.use = device.type == "CUDA"
        scene.cycles.device = "GPU" if any(d.use for d in prefs.devices) else "CPU"
        scene.cycles.samples = 20 if quick else 32
        scene.render.resolution_x = scene.render.resolution_y = 480 if quick else 600
        if style != "current":
            refine(scene, style)
        for angle, (yaw, pitch) in ANGLES.items():
            if quick and angle not in ("threequarter", "profile", "rear"):
                continue
            yaw, pitch = math.radians(yaw), math.radians(pitch)
            center = Vector((0, 0, 1.79))
            scene.camera.data.ortho_scale = 1.18
            scene.camera.location = center + 8 * Vector((math.sin(yaw) * math.cos(pitch),
                -math.cos(yaw) * math.cos(pitch), math.sin(pitch)))
            scene.camera.rotation_euler = (center - scene.camera.location).to_track_quat("-Z", "Y").to_euler()
            if not quick and style != "current" and angle == "threequarter":
                bpy.ops.file.pack_all()
                scene.render.filepath = f"//review/{style}-threequarter.png"
                bpy.ops.wm.save_as_mainfile(filepath=str(output / f"Ravedio331-{style}.blend"))
            scene.render.filepath = str(review / f"{style}-{angle}.png")
            bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("base", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--direction", choices=DIRECTIONS)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    render(args.base, args.output, args.quick, (args.direction,) if args.direction else DIRECTIONS)
