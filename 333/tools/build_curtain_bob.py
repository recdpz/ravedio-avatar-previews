"""Build a center-parted curtain Bob beside the selected Tucked + Brushed source."""
from argparse import ArgumentParser
from pathlib import Path
import math
import sys

import bpy
from mathutils import Vector
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "332/tools"))
from study_bob import normalized, ANGLES, TO_BLENDER, CENTER, ease


def sample_path(points, count=80):
    points = np.asarray(points, dtype=float)
    out = []
    for position in np.linspace(0, len(points) - 1, count):
        i = min(int(position), len(points) - 2)
        t = position - i
        p1, p2 = points[i:i+2]
        p0 = points[i-1] if i else p1 * 2 - p2
        p3 = points[i+2] if i+2 < len(points) else p2 * 2 - p1
        out.append(.5 * ((2*p1) + (-p0+p2)*t + (2*p0-5*p1+4*p2-p3)*t*t
                         + (-p0+3*p1-3*p2+p3)*t*t*t))
    return np.asarray(out)


def support(points, clearance=.012):
    relative = points - CENTER
    length = np.linalg.norm(relative, axis=1)
    return CENTER + relative * np.maximum(1, (.384 + clearance) / np.maximum(length, 1e-8))[:, None]


def mesh_object(name, vertices, faces, material, uv=None):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.polygons.foreach_set("use_smooth", np.ones(len(mesh.polygons), dtype=bool))
    mesh.materials.append(material)
    mesh.update()
    if uv is not None:
        layer = mesh.uv_layers.new(name="Lock flow")
        for polygon in mesh.polygons:
            coords = np.asarray([uv[i] for i in polygon.vertices])
            if np.ptp(coords[:, 0]) > .5:
                coords[coords[:, 0] < .5, 0] += 1
            for loop, value in zip(polygon.loop_indices, coords):
                layer.data[loop].uv = value
    obj = bpy.data.objects.new(name, mesh)
    obj["component269"] = "hair"
    bpy.context.scene.collection.objects.link(obj)
    return obj


def strand(name, path, widths, depths, material, phase):
    points = sample_path(path)
    points = support(points, .014)
    along = np.linspace(0, 1, len(points))
    root_blend = ease(along / .055)
    relative = points - CENTER
    radius = np.linalg.norm(relative, axis=1)
    points = CENTER + normalized(relative) * (.387 + (radius - .387) * root_blend)[:, None]
    tangent = normalized(np.gradient(points, axis=0))
    outward = normalized(points - CENTER)
    # A transported frame gives the brushed detail a steady direction around each bend.
    across = normalized(np.cross(tangent[0], outward[0]))
    frame = []
    for t in tangent:
        across = normalized(across - t * np.dot(across, t))
        frame.append(across)
    frame = np.asarray(frame)
    normal = normalized(np.cross(frame, tangent))
    if np.mean(np.sum(normal * outward, axis=1)) < 0:
        normal = -normal
        frame = -frame
    n, sides = len(points), 32
    along = np.linspace(0, 1, n)
    width = np.interp(along, np.linspace(0, 1, len(widths)), widths)
    depth = np.interp(along, np.linspace(0, 1, len(depths)), depths)
    # A short bevel finishes each lock without a long pointed or bulbous tip.
    cap = np.sqrt(np.maximum(.0003, 1 - ease((along - .92) / .081)))
    width *= cap
    depth *= cap * (.08 + .92 * ease(along / .06))
    q = np.arange(sides) * 2 * np.pi / sides
    ridge = .0006 * np.cos(6*q[None, :] + phase) * np.sin(q[None, :])**2
    p = (points[:, None, :] + frame[:, None, :] * width[:, None, None] * np.cos(q)[None, :, None]
         + normal[:, None, :] * (depth[:, None, None] * np.sin(q)[None, :, None] + ridge[:, :, None]))
    p = support(p.reshape((-1, 3)), .004)
    vertices = (p @ TO_BLENDER).tolist()
    faces = []
    uv = [(j/sides, i/(n-1)) for i in range(n) for j in range(sides)]
    for i in range(n-1):
        for j in range(sides):
            a, b = i*sides+j, i*sides+(j+1)%sides
            faces.append((b, a, a+sides, b+sides))
    faces.extend((tuple(range(sides)), tuple((n-1)*sides+j for j in reversed(range(sides)))))
    obj = mesh_object(name, vertices, faces, material, uv)
    # Blend the root shading into the scalp direction so the cut ends of the
    # rooted tubes do not produce a row of disconnected highlights at the part.
    shading = np.array([v.normal[:] for v in obj.data.vertices])
    center = CENTER @ TO_BLENDER
    radial = normalized(np.asarray(vertices) - center)
    blend = np.repeat(1 - ease(along/.15), sides)[:,None]
    shading = normalized(shading*(1-blend) + radial*blend)
    obj.data.normals_split_custom_set_from_vertices(shading.tolist())
    return obj


def scalp(material):
    rows, columns = 72, 160
    phi = np.arange(columns) * 2 * np.pi / columns
    angle = np.abs((phi + np.pi) % (2*np.pi) - np.pi)
    end = .78 + 1.44 * ease((angle - .60) / 1.52)
    t = np.linspace(.002, 1, rows)[:, None]
    theta = t * end
    radius = .391 - .009 * ease((t - .92) / .08)
    # The final lip recedes into the skin under the outer sections.
    p = np.stack((radius*np.sin(theta)*np.sin(phi),
                  np.broadcast_to(radius*np.cos(theta), theta.shape),
                  radius*np.sin(theta)*np.cos(phi)), axis=-1) + CENTER
    vertices = (p.reshape((-1, 3)) @ TO_BLENDER).tolist()
    faces = []
    for i in range(rows-1):
        for j in range(columns):
            a, b = i*columns+j, i*columns+(j+1)%columns
            faces.append((b, a, a+columns, b+columns))
    faces.append(tuple(range(columns)))
    return mesh_object("Curtain Bob / recessed coverage", vertices, faces, material)


def back_surface(material):
    rows, columns = 90, 81
    t = np.linspace(0, 1, rows)
    u = np.linspace(-1, 1, columns)
    profile = sample_path((
        (.115,2.155,.155),
        (.191,2.107,.265),
        (.235,2.06,.322),
        (.302,1.92,.405),
        (.315,1.77,.411),
        (.288,1.62,.371),
        (.251,1.515,.303),
    ), rows)
    width, height, depth = profile.T
    hem = .0035 * np.cos(5*np.pi*u+.4)
    x = width[:,None] * u[None,:]
    h = height[:,None] + ease((t[:,None]-.83)/.17) * hem[None,:]
    y = depth[:,None] - .092 * u[None,:]**2
    # Broad shallow ridges define the layers while the ends share a soft hem.
    phase = 5*np.pi*u[None,:] + .35*np.sin(t[:,None]*np.pi)
    relief = .0045 * np.cos(phase) * (1-u[None,:]**8) * np.sin(np.pi*t[:,None])**2
    outer = np.stack((x, h, CENTER[2] - y - relief),axis=-1)
    inner = outer.copy()
    inner[:,:,2] += .008
    # Bury the upper edge in the crown and emerge smoothly from the coverage.
    outer_flat = outer.reshape((-1,3))
    inner_flat = inner.reshape((-1,3))
    for points, clearance in ((outer_flat,.007),(inner_flat,.003)):
        target = support(points,clearance)
        amount = np.repeat(ease(t/.13),columns)[:,None]
        buried = CENTER + normalized(points-CENTER)*.383
        points[:] = buried*(1-amount)+target*amount
    vertices = np.concatenate((outer_flat,inner_flat)) @ TO_BLENDER
    count = rows*columns
    uv = [(j/(columns-1),i/(rows-1)) for i in range(rows) for j in range(columns)]*2
    faces = []
    for i in range(rows-1):
        for j in range(columns-1):
            a=i*columns+j
            faces.append((a,a+1,a+1+columns,a+columns))
            faces.append((a+count+1,a+count,a+count+columns,a+count+columns+1))
    boundary = [*range(columns)]
    boundary += [(i+1)*columns-1 for i in range(1,rows)]
    boundary += list(range(rows*columns-2,(rows-1)*columns-1,-1))
    boundary += [i*columns for i in reversed(range(1,rows-1))]
    for j,a in enumerate(boundary):
        b=boundary[(j+1)%len(boundary)]
        faces.append((b,a,a+count,b+count))
    return mesh_object("Curtain Bob / shaped back layers",vertices.tolist(),faces,material,uv)


def build(scene):
    hair = [o for o in scene.objects if o.type=="MESH" and o.get("component269")=="hair"]
    materials = [o.data.materials[0] for o in hair if "Bob / side sweep" in o.data.name]
    coverage = next(o.data.materials[0] for o in hair if "coverage" in o.data.name.lower())
    for obj in list(scene.objects):
        if obj.get("component269") == "hair":
            bpy.data.objects.remove(obj, do_unlink=True)
    scalp(coverage)
    # Two face-framing curtains replace the diagonal side sweep.
    for side in (-1, 1):
        path = np.array([
            (side*.001, 2.096, .262),
            (side*.105, 2.100, .303),
            (side*.235, 2.016, .282),
            (side*.329, 1.865, .205),
            (side*.351, 1.686, .133),
            (side*.318, 1.535, .101),
        ])
        path[:, 2] += CENTER[2]
        # Rooted front sections follow the skull before the free ends turn in.
        rooted = path[:3] - CENTER
        length = np.linalg.norm(rooted, axis=1)
        path[:3] = CENTER + rooted * np.minimum(1, .415/length)[:,None]
        strand(f"Curtain Bob / face frame {side}", path,
               (.060,.062,.060,.047,.036),(.012,.017,.015,.012,.009),materials[0], .4)
        for j, root_z in enumerate(np.linspace(.174, -.305, 8)):
            # Cross the crown in transverse sections, then fall at the sides.
            cross = math.sqrt(max(.02, .405**2 - root_z**2))
            path = []
            for angle in np.linspace(.002, 1.43, 9):
                path.append((side*cross*math.sin(angle), CENTER[1]+cross*math.cos(angle),
                             CENTER[2]+root_z-.012*math.sin(angle)*math.sin(j*.70)))
            x, y, z = path[-1]
            hem = 1.521 + .019*math.sin(j*1.1 + side*.4)
            sweep = .022 + .024*(root_z+.305)/.479
            path.extend(((side*(cross+.016+.008*math.sin(j*.9)),1.77,z-sweep*.55),
                         (side*(cross*.97),1.615,z-sweep),
                         (side*(cross*.88),hem,z-sweep*.60+.009*math.sin(j*.8))))
            strand(f"Curtain Bob / side layer {side} {j}", path,
                   (.052,.051,.050,.041,.027),(.010,.013,.014,.012,.008),
                   materials[(j+1)%len(materials)],j*.8)
    back_surface(materials[1])


def render(base, output, quick):
    review = output / "review"
    review.mkdir(parents=True, exist_ok=True)
    bpy.context.preferences.filepaths.save_version = 0
    for style in ("chosen", "curtain"):
        bpy.ops.wm.open_mainfile(filepath=str(base))
        scene = bpy.context.scene
        preferences = bpy.context.preferences.addons["cycles"].preferences
        preferences.compute_device_type = "CUDA"
        preferences.get_devices()
        for device in preferences.devices:
            device.use = device.type == "CUDA"
        scene.cycles.device = "GPU" if any(d.use for d in preferences.devices) else "CPU"
        scene.cycles.samples = 20 if quick else 32
        scene.render.resolution_x = scene.render.resolution_y = 480 if quick else 600
        if style == "curtain":
            build(scene)
        for angle, (yaw, pitch) in ANGLES.items():
            if quick and angle not in ("front", "threequarter", "profile", "rear", "rightprofile"):
                continue
            yaw, pitch = math.radians(yaw), math.radians(pitch)
            target = Vector((0, 0, 1.79))
            scene.camera.data.ortho_scale = 1.18
            scene.camera.location = target + 8 * Vector((
                math.sin(yaw) * math.cos(pitch),
                -math.cos(yaw) * math.cos(pitch),
                math.sin(pitch),
            ))
            scene.camera.rotation_euler = (target - scene.camera.location).to_track_quat("-Z", "Y").to_euler()
            if not quick and style == "curtain" and angle == "threequarter":
                bpy.ops.file.pack_all()
                scene.render.filepath = "//review/curtain-threequarter.png"
                bpy.ops.wm.save_as_mainfile(filepath=str(output / "Ravedio333-curtain-bob.blend"))
            scene.render.filepath = str(review / f"{style}-{angle}.png")
            bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("base", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    render(args.base, args.output, args.quick)
