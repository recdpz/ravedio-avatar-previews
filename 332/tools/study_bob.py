"""Compare Bob silhouettes and lock-aligned normal and roughness textures."""
from argparse import ArgumentParser
from pathlib import Path
import math
import sys

import bpy
from mathutils import Vector
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "331/tools"))
from bob_directions import ANGLES, TO_BLENDER
from build_lob import cartesian, ease, keep_head_room, polar
from drape import CENTER, islands, turn_along_path, warp_normals

SHAPES = ("tucked", "volume", "side-tuck")
TEXTURES = ("smooth", "brushed", "channels")


def normalized(v):
    return v / np.maximum(np.linalg.norm(v, axis=-1, keepdims=True), 1e-8)


def image_map(name, rgb, output):
    height, width, _ = rgb.shape
    image = bpy.data.images.new(name, width=width, height=height, alpha=True)
    image.colorspace_settings.name = "Non-Color"
    rgba = np.concatenate((rgb, np.ones((height, width, 1))), axis=2)
    image.pixels.foreach_set(rgba.astype(np.float32).ravel())
    image.filepath_raw = str(output / (name + ".png"))
    image.file_format = "PNG"
    image.save()
    image.pack()
    return image


def texture_maps(style, output):
    height, width = 1024, 512
    u, v = np.meshgrid(np.arange(width) / width, np.arange(height) / height)
    drift = .13 * np.sin(2 * np.pi * v) + .035 * np.sin(6 * np.pi * v)
    fine = np.cos(2 * np.pi * (u * 17 + drift))
    if style == "brushed":
        relief = .00044 * fine + .00016 * np.cos(2 * np.pi * (u * 29 - .18 * v))
        roughness = .305 + .035 * fine + .015 * np.sin(2 * np.pi * (u * 7 + .25 * v))
    else:
        groove = (.5 + .5 * np.cos(2 * np.pi * (u * 6 + .45 * drift)))**7
        relief = -.0018 * groove + .00013 * fine
        roughness = .285 + .090 * groove + .012 * fine
    # Encode relief as a normal map in a lock's tangent frame. The maps are
    # ordinary glTF-compatible images, aligned from the crown toward the ends.
    dx = (np.roll(relief, -1, axis=1) - np.roll(relief, 1, axis=1)) * width / (.13 * 2)
    dy = np.gradient(relief, axis=0) * height / .72
    normal = normalized(np.stack((-dx, -dy, np.ones_like(dx)), axis=-1))
    return (image_map("bob-" + style + "-normal", normal * .5 + .5, output),
            image_map("bob-" + style + "-roughness", np.repeat(roughness[:, :, None], 3, axis=2), output))


def surface_finish(material, style, maps):
    # Use the same overall gloss for each sample so the surface construction
    # can be compared directly.
    result = material.copy()
    result.name = material.name + " / " + style
    result.use_fake_user = True
    nodes, links = result.node_tree.nodes, result.node_tree.links
    shader = next(node for node in nodes if node.type == "BSDF_PRINCIPLED")
    shader.inputs["Roughness"].default_value = .31
    shader.inputs["Coat Weight"].default_value = .46
    shader.inputs["Coat Roughness"].default_value = .25
    if style != "smooth":
        normal = nodes.new("ShaderNodeTexImage")
        normal.name = "Directional normal map"
        normal.image = maps[style][0]
        normal_map = nodes.new("ShaderNodeNormalMap")
        normal_map.uv_map = "Lock flow"
        normal_map.inputs["Strength"].default_value = 1.
        rough = nodes.new("ShaderNodeTexImage")
        rough.name = "Directional roughness map"
        rough.image = maps[style][1]
        uv = nodes.new("ShaderNodeUVMap")
        uv.uv_map = "Lock flow"
        links.new(uv.outputs["UV"], normal.inputs["Vector"])
        links.new(uv.outputs["UV"], rough.inputs["Vector"])
        links.new(normal.outputs["Color"], normal_map.inputs["Color"])
        links.new(normal_map.outputs["Normal"], shader.inputs["Normal"])
        links.new(rough.outputs["Color"], shader.inputs["Roughness"])
    return result


def path_shape(points, style):
    theta, y, radius = polar(points)
    h = points[:, 1]
    side = np.sin(theta)
    if style == "volume":
        middle = ease((2.12 - h) / .20) * ease((h - 1.53) / .24)
        back = ease((np.abs(theta) - 1.61) / 1.12)
        radius += (.046 + .013 * np.sin(3 * theta + .25)) * middle
        theta += .027 * middle * np.sin(2 * theta + .5)
        y += .019 * middle * back
    elif style == "side-tuck":
        side_tuck = ease((side - .15) / .68) * (1 - ease((np.abs(theta) - 1.70) / .63))
        lower = ease((2.065 - h) / .33)
        theta += .19 * side_tuck * lower
        # Give the exposed side a little more lift through the sweep.
        opposite = ease((-side - .32) / .50) * ease((2.10 - h) / .20) * ease((h - 1.52) / .25)
        radius += .026 * opposite
    return keep_head_room(points, cartesian(theta, y, radius))


def author_hair(scene, style):
    hair = [obj for obj in scene.objects if obj.type == "MESH" and obj.get("component269") == "hair"]
    assert len(hair) == 4
    for obj in hair:
        mesh = obj.data
        if "Bob / side sweep" not in mesh.name:
            if style != "tucked":
                p = np.array([v.co[:] for v in mesh.vertices]) @ TO_BLENDER.T
                mesh.vertices.foreach_set("co", (path_shape(p, style) @ TO_BLENDER).ravel())
                mesh.update()
            continue
        p = np.array([v.co[:] for v in mesh.vertices]) @ TO_BLENDER.T
        n = np.array([v.normal[:] for v in mesh.vertices]) @ TO_BLENDER.T
        mesh.calc_loop_triangles()
        faces = np.array([t.vertices[:] for t in mesh.loop_triangles])
        label = islands(p, faces)
        adjacency = [[] for _ in p]
        for edge in mesh.edges:
            a, b = edge.vertices
            adjacency[a].append(b)
            adjacency[b].append(a)
        moved, shading = p.copy(), n.copy()
        uv = np.empty((len(p), 2), dtype=float)
        for key in np.unique(label):
            ids = np.flatnonzero(label == key)
            poles = [i for i in ids if len(adjacency[i]) == 32]
            assert len(poles) == 2
            root = max(poles, key=lambda i: p[i, 1])
            distance = np.full(len(p), -1)
            distance[root] = 0
            queue = [root]
            for i in queue:
                for j in adjacency[i]:
                    if distance[j] < 0:
                        distance[j] = distance[i] + 1
                        queue.append(j)
            ring = distance[ids]
            count = np.bincount(ring)
            assert len(count) == 65 and (count[1:-1] == 32).all()
            centers = np.column_stack([np.bincount(ring, weights=axis) / count for axis in p[ids].T])
            target = path_shape(centers, style)
            before = normalized(np.gradient(centers, axis=0))
            after = normalized(np.gradient(target, axis=0))
            offset = turn_along_path(p[ids] - centers[ring], before[ring], after[ring])
            radial = normalized(target - CENTER)
            lateral = normalized(np.cross(after, radial))
            width_scale = np.ones(len(target))
            if style == "volume":
                # Preserve the angular coverage of each section as the silhouette expands.
                original_radius = np.hypot(centers[:, 0], centers[:, 2] - CENTER[2])
                new_radius = np.hypot(target[:, 0], target[:, 2] - CENTER[2])
                width_scale = np.clip(new_radius / np.maximum(original_radius, .06), 1, 1.20)
                offset += lateral[ring] * np.sum(offset * lateral[ring], axis=1, keepdims=True) * (width_scale[ring, None] - 1)
            moved[ids] = target[ring] + offset
            normals = turn_along_path(n[ids], before[ring], after[ring])
            normals += lateral[ring] * np.sum(normals * lateral[ring], axis=1, keepdims=True) * (1 / width_scale[ring, None] - 1)
            shading[ids] = normalized(normals)
            if style == "side-tuck":
                # A shared spatial warp keeps adjacent sections together where
                # the hair is pressed toward the side of the head.
                moved[ids] = path_shape(p[ids], style)
                shading[ids] = warp_normals(lambda coords: path_shape(coords, style), p[ids], n[ids])

            tangent = before
            outward = normalized(centers - CENTER)
            outward = normalized(outward - np.sum(outward * tangent, axis=1, keepdims=True) * tangent)
            across = normalized(np.cross(tangent, outward))
            relative = p[ids] - centers[ring]
            x = np.sum(relative * across[ring], axis=1)
            z = np.sum(relative * outward[ring], axis=1)
            uv[ids, 0] = np.arctan2(x, z) / (2 * np.pi) + .5
            arc = np.r_[0, np.cumsum(np.linalg.norm(np.diff(centers, axis=0), axis=1))]
            uv[ids, 1] = arc[ring] / max(arc[-1], 1e-8)
            uv[[root, max(poles, key=lambda i: distance[i])], 0] = .5

        if style == "volume":
            # The centerline transport can move the inner edge of a section
            # toward the scalp. Preserve the original shell clearance per vertex.
            shading = warp_normals(lambda coords: keep_head_room(p, coords), moved, shading)
            moved = keep_head_room(p, moved)
        assert np.isfinite(moved).all() and np.isfinite(shading).all() and np.isfinite(uv).all()
        mesh.vertices.foreach_set("co", (moved @ TO_BLENDER).ravel())
        mesh.update()
        mesh.normals_split_custom_set_from_vertices((shading @ TO_BLENDER).tolist())
        layer = mesh.uv_layers.get("Lock flow") or mesh.uv_layers.new(name="Lock flow")
        mesh.uv_layers.active = layer
        # Keep the cylindrical seam on the inner side of each lock.
        for face in mesh.polygons:
            ids = np.array(face.vertices)
            face_uv = uv[ids].copy()
            if np.ptp(face_uv[:, 0]) > .5:
                face_uv[face_uv[:, 0] < .5, 0] += 1
            for loop, coords in zip(face.loop_indices, face_uv):
                layer.data[loop].uv = coords
    return hair


def render(base, output, quick, selected_shape=None):
    output.mkdir(parents=True, exist_ok=True)
    review = output / "review"
    textures = output / "textures"
    review.mkdir(exist_ok=True)
    textures.mkdir(exist_ok=True)
    bpy.context.preferences.filepaths.save_version = 0
    for shape in (SHAPES if selected_shape is None else (selected_shape,)):
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
        hair = author_hair(scene, shape)
        maps = {style: texture_maps(style, textures) for style in ("brushed", "channels")}
        material_sets = {}
        for texture in TEXTURES:
            for obj in hair:
                base_material = obj.data.materials[0]
                if "Lock flow" not in obj.data.uv_layers:
                    material_sets[(obj.name, texture)] = surface_finish(base_material, "smooth", maps)
                else:
                    material_sets[(obj.name, texture)] = surface_finish(base_material, texture, maps)
        for texture in TEXTURES:
            for obj in hair:
                obj.data.materials[0] = material_sets[(obj.name, texture)]
            for angle, (yaw, pitch) in ANGLES.items():
                if quick and angle not in ("threequarter", "profile", "rear"):
                    continue
                yaw, pitch = math.radians(yaw), math.radians(pitch)
                target = Vector((0, 0, 1.79))
                scene.camera.data.ortho_scale = 1.18
                scene.camera.location = target + 8 * Vector((math.sin(yaw) * math.cos(pitch),
                    -math.cos(yaw) * math.cos(pitch), math.sin(pitch)))
                scene.camera.rotation_euler = (target - scene.camera.location).to_track_quat("-Z", "Y").to_euler()
                if not quick and texture == "brushed" and angle == "threequarter":
                    bpy.ops.file.pack_all()
                    scene.render.filepath = f"//review/{shape}-{texture}-{angle}.png"
                    bpy.ops.wm.save_as_mainfile(filepath=str(output / f"Ravedio332-{shape}.blend"))
                scene.render.filepath = str(review / f"{shape}-{texture}-{angle}.png")
                bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("base", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--shape", choices=SHAPES)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    render(args.base, args.output, args.quick, args.shape)
