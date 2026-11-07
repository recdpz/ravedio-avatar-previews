"""Build a Soft brow fringe whose locks separate below a shared crown."""
import json
import sys
from pathlib import Path

import bpy
import numpy as np

REV = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REV.parent / "281/tools"))
from build_studies import air_radius, soft_edge
from build_hair import BANGS_COLOR, CENTER, RADIUS, bangs_body, ease, hair_material, smooth_max

# Left and right root angles, end height, and gentle sideways movement.
LOCKS = (
    (-.756, -.614, 1.950, -.030),
    (-.614, -.457, 1.973, -.039),
    (-.457, -.350, 1.984, -.018),
    (-.350, -.164, 1.955, -.025),
    (-.164, -.011, 1.968, .018),
    (-.011, .122, 1.978, .023),
    (.122, .294, 1.956, .028),
    (.294, .438, 1.968, .031),
    (.438, .570, 1.974, .038),
    (.570, .737, 1.951, .040),
)


def backing_edge(angle, original):
    old = soft_edge(angle, original, "air")
    front = 1 - ease((np.abs(angle) - .66) / .23)
    shoulder = ease((np.abs(angle) - .54) / 1.01)
    root = 2.018 + .005 * np.sin(4.5 * angle + .73)
    root += .012 * np.exp(-((angle + .164) / .081)**2)
    root += .010 * np.exp(-((angle - .294) / .095)**2)
    return old + front * (root + .706 * shoulder - old)


def scalp_radius(y):
    return np.sqrt(np.maximum(.000001, RADIUS**2 - (y - CENTER[1])**2))


def fringe_radius(y, angle):
    # Use one continuous profile above and below the split. The surface
    # rolls out gently through the forehead and then settles toward the skin.
    peak = 2.077 + .010 * np.sin(4 * angle + .42)
    arc = .018 * np.exp(-((y - peak) / .072)**2)
    lift = .011 * ease((y - 2.049) / .112)
    grain = .0016 * np.cos(27 * angle + .8 * np.sin(3 * angle))
    layers = np.zeros_like(y)
    for left, right, _, drift in LOCKS:
        center = .5 * (left + right) + drift * ease((2.022 - y) / .081)
        width = .53 * (right - left)
        layers += .004 * np.exp(-((angle - center) / width)**2)
    settled = scalp_radius(y) + .007 + arc + lift + grain + layers
    cap = air_radius(y)
    fit = ease((2.182 - y) / .101)
    return cap + fit * (settled - cap)


def crown_surface(angles):
    points, _, _ = bangs_body("none", hairline=backing_edge, angles=angles)
    y = points[:, :, 1]
    # Soften the inherited nape points while keeping the length of the lob.
    edge = y[-1].copy()
    smoothed = .50 * edge + .25 * (np.roll(edge, 13) + np.roll(edge, -13))
    nape = ease((np.abs(angles) - 1.35) / .68)
    y += nape * (smoothed - edge) * ease((1.67 - y) / .32)
    a = np.arctan2(points[:, :, 0], points[:, :, 2] - CENTER[2])
    rho = np.hypot(points[:, :, 0], points[:, :, 2] - CENTER[2])
    front = (1 - ease((np.abs(a) - .77) / .34)) * ease((2.213 - y) / .059)
    core = smooth_max(fringe_radius(y, a), scalp_radius(y) + .006, .008)
    rho += front * (core - rho)
    points[:, :, 0] = rho * np.sin(a)
    points[:, :, 2] = CENTER[2] + rho * np.cos(a)
    return points

def add_lock(vertices, faces, roots, ids, end, drift, index):
    # The first edge of every lock is part of the crown mesh. Curvature and
    # taper are introduced below the root, leaving open spaces at the tips.
    a = np.arctan2(roots[:, 0], roots[:, 2] - CENTER[2])
    base_y = roots[:, 1]
    radius = np.hypot(roots[:, 0], roots[:, 2] - CENTER[2])
    excess = radius - fringe_radius(base_y, a)
    middle = .5 * (a[0] + a[-1])
    u = np.linspace(-1, 1, len(ids))
    tip_drift = np.clip(drift, .80 * (a[0] - middle), .80 * (a[-1] - middle))
    previous = ids
    segments = 30
    for row in range(1, segments):
        t = row / segments
        rounded = np.sqrt(1 - np.clip((t - .75) / .25, 0, 1)**2)
        width = (1 - (.18 + .042 * (index % 3)) * ease(t / .82)) * rounded
        # Sweep only into space released by tapering. Neighbouring strips
        # remain in their own angular ranges even near the shared roots.
        theta = middle + (a - middle) * width + tip_drift * (1 - width)
        y = base_y + (end - base_y) * t + .006 * u**2 * np.sin(np.pi * t)
        r = fringe_radius(y, theta) + excess * (1 - ease(t))
        r += .003 * (1 - u*u) * np.sin(np.pi * t)**2
        points = np.column_stack((r * np.sin(theta), y, CENTER[2] + r * np.cos(theta)))
        next_row = list(range(len(vertices), len(vertices) + len(points)))
        vertices.extend(points.tolist())
        faces.extend((previous[i], next_row[i], next_row[i+1], previous[i+1])
                     for i in range(len(ids) - 1))
        previous = next_row

    tip = len(vertices)
    theta = middle + tip_drift
    r = fringe_radius(np.asarray(end), theta)
    vertices.append((r * np.sin(theta), end, CENTER[2] + r * np.cos(theta)))
    faces.extend((previous[i], tip, previous[i+1]) for i in range(len(ids) - 1))


def make_hair(material):
    angles = np.linspace(-np.pi, np.pi, 288, endpoint=False)
    # Explicit root boundaries keep the split points shared by both sides.
    bounds = [left for left, _, _, _ in LOCKS] + [LOCKS[-1][1]]
    angles = np.unique(np.concatenate((angles, bounds)))
    points = crown_surface(angles)
    rows, cols, _ = points.shape
    vertices = points.reshape(-1, 3).tolist()
    faces = [tuple(range(cols))]
    for j in range(rows - 1):
        top = j * cols
        bottom = top + cols
        faces.extend((top + i, bottom + i, bottom + (i + 1) % cols, top + (i + 1) % cols)
                     for i in range(cols))
    for index, (left, right, end, drift) in enumerate(LOCKS):
        first = np.searchsorted(angles, left)
        last = np.searchsorted(angles, right)
        ids = [(rows - 1) * cols + col for col in range(first, last + 1)]
        add_lock(vertices, faces, points[-1, first:last+1], ids, end, drift, index)
    name = "Hair / soft brow fringe"
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([(x, -z, y) for x, y, z in vertices], [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    mesh.materials.append(material)
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    inset = obj.modifiers.new("Inset edge thickness", "SOLIDIFY")
    inset.thickness = .0045
    inset.offset = -1


def export():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    make_hair(hair_material(False, BANGS_COLOR, .43))
    bpy.ops.export_scene.gltf(filepath=str(REV / "assets/fringe.glb"), export_format="GLB",
                              export_apply=True, export_materials="EXPORT")
    manifest = {"Feminine": {"side-sweep": {
        "label": "Soft brow fringe", "note": "Bare-head review",
        "fits": {"none": {"default": "./assets/fringe.glb", "ombre": "./assets/fringe.glb"}},
    }}}
    (REV / "hair.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf8", newline="\n")


if __name__ == "__main__":
    export()
