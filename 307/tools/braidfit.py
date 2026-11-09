"""Lay the existing Twin Braids weave over smoother, tapered plait paths."""
import json
from pathlib import Path
import sys

import numpy as np

REV = Path(__file__).resolve().parents[1]
ROOT = REV.parent
sys.path.insert(0, str(ROOT / "305/tools"))
from twin import front_surface, garment_support, smooth_profile
from fit import CENTER, ease, geometry, local_path, read_glb, turn_along_path, unit, write_glb

HEIGHTS = np.linspace(1.00, 1.99, 300)
RING_COUNT = 130
SIDES = 10
WEAVE_SIZE = 3 * RING_COUNT * SIDES
BRAID_SIZE = WEAVE_SIZE + 280
TIE_SIZE = 256


def guide(center, side, covered):
    height = center[:, 1]
    if covered:
        knots = [1.06, 1.15, 1.24, 1.32, 1.40, 1.48, 1.56, 1.65]
        across = [.236, .239, .240, .239, .241, .250, .315, .369]
        forward = [.235, .247, .258, .253, .213, .135, .085, .024]
        # Keep the upper turn tucked beside the wrap.
        blend = ease((1.491 - height) / .155)
    else:
        knots = [1.06, 1.15, 1.24, 1.32, 1.40, 1.48, 1.56, 1.65, 1.73]
        across = [.234, .239, .245, .252, .273, .301, .333, .369, .389]
        forward = [.202, .215, .234, .238, .218, .173, .105, .012, -.070]
        blend = ease((1.757 - height) / .272)
    authored = smooth_profile(np.array(knots), np.column_stack((side*np.array(across), forward)),
                              HEIGHTS, .032)
    target = center.copy()
    for i, axis in enumerate((0, 2)):
        target[:, axis] += blend * (np.interp(height, HEIGHTS, authored[:, i]) - center[:, axis])
    # A slight difference between the tips makes each plait feel independent.
    lower = ease((1.36 - height) / .27)
    target[:, 0] += .006 * lower
    target[:, 1] += side * .012 * lower
    return target


def tangent(centers):
    """Smooth the sampled tangent, including the densely sampled shoulder."""
    padded = np.pad(centers, ((3, 3), (0, 0)), mode="edge")
    kernel = np.array([1., 3., 5., 6., 5., 3., 1.]) / 24
    smooth = np.column_stack([np.convolve(axis, kernel, "valid") for axis in padded.T])
    return unit(np.gradient(smooth, axis=0))


def braid_frame(points, axis):
    radial = points - CENTER
    outward = unit(radial - np.sum(radial * axis, axis=1, keepdims=True) * axis)
    return outward, np.cross(axis, outward)


def rounded_weave(original, center, old_axis, rail, new_axis, covered):
    """Author the lower plies in distance along the new path."""
    _, old_across = braid_frame(center, old_axis)
    ply_offsets = original.mean(axis=2) - center[None, :, :]
    displacement = np.sum(ply_offsets * old_across[None, :, :], axis=2)
    phases = np.arange(3) * (2 * np.pi / 3)
    old_phase = np.unwrap(np.arctan2(np.cos(phases) @ displacement, np.sin(phases) @ displacement))
    height = center[:, 1]
    anchor = np.argmin(abs(height - (1.55 if covered else 1.65)))
    arc = np.r_[0., np.cumsum(np.linalg.norm(np.diff(rail, axis=0), axis=1))]
    phase = old_phase[anchor] + (arc - arc[anchor]) * (2 * np.pi / .099)
    outward, across = braid_frame(rail, new_axis)
    radius = .051 - .009 * ease((1.76 - height) / .33) - .010 * ease((1.41 - height) / .32)
    ring_angle = np.arange(SIDES) * (2 * np.pi / SIDES)

    sections = []
    for offset in phases:
        q = phase + offset
        ply = rail + across * (.60 * radius * np.sin(q))[:, None]
        ply += outward * (.34 * radius * np.sin(2 * q))[:, None]
        direction = unit(np.gradient(ply, axis=0))
        a = unit(np.cross(direction, [0., 0., -1.]))
        b = np.cross(direction, a)
        section = ply[:, None, :] + a[:, None, :] * (.48 * radius[:, None] * np.cos(ring_angle))[:, :, None]
        section += b[:, None, :] * (.42 * radius[:, None] * np.sin(ring_angle))[:, :, None]
        sections.append(section)
    return np.stack(sections)


def pose(braid, tie, center, target, old_axis, covered):
    new_axis = tangent(target)
    original = braid[:WEAVE_SIZE].reshape(3, RING_COUNT, SIDES, 3)
    relative = original - center[None, :, None, :]
    # Move each complete woven section in its local frame so the plies
    # keep their round cross-sections as the main path turns.
    weight = ease(((1.65 if covered else 1.76) - center[:, 1]) / .34)
    scale = 1. - .11 * weight - .17 * ease((1.42 - center[:, 1]) / .34)
    relative *= scale[None, :, None, None]
    moved = turn_along_path(relative.reshape(-1, 3),
                           np.tile(np.repeat(old_axis, SIDES, axis=0), (3, 1)),
                           np.tile(np.repeat(new_axis, SIDES, axis=0), (3, 1)))
    output = braid.copy()
    carried = moved.reshape(original.shape) + target[None, :, None, :]
    rounded = rounded_weave(original, center, old_axis, target, new_axis, covered)
    blend = ease(((1.62 if covered else 1.73) - center[:, 1]) / .16)
    output[:WEAVE_SIZE] = (carried + (rounded - carried) * blend[None, :, None, None]).reshape(-1, 3)

    def terminal(points, length, width):
        local = points - center[-1]
        axial = local @ old_axis[-1]
        radial = local - axial[:, None] * old_axis[-1]
        offsets = radial * width + axial[:, None] * old_axis[-1] * length
        return target[-1] + turn_along_path(offsets, np.broadcast_to(old_axis[-1], offsets.shape),
                                            np.broadcast_to(new_axis[-1], offsets.shape))

    brush = braid[WEAVE_SIZE:]
    brush_taper = (scale[-1] * (1. - .26 * ease(((brush - center[-1]) @ old_axis[-1]) / .063)))[:, None]
    output[WEAVE_SIZE:] = terminal(brush, .62, brush_taper)
    return output, terminal(tie, .78, scale[-1])


def shading(points, faces, old_normals, weight):
    triangles = points[faces]
    areas = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
    normals = np.zeros_like(points)
    for corner in faces.T:
        np.add.at(normals, corner, areas)
    # Keep the original exported shading at the attachment above the transition.
    return unit(old_normals + (unit(normals) - old_normals) * weight[:, None])


def fit(source, target, covered, support_paths):
    doc, data = read_glb(source)
    braid, tie = list(geometry(doc, data))
    world = [part[2] @ part[4].T + part[5] for part in (braid, tie)]
    assert [len(p) for p in world] == [2 * BRAID_SIZE, 2 * TIE_SIZE], source
    support = tuple(front_surface(path) for path in support_paths)
    for index, side in enumerate((-1, 1)):
        braid_slice = slice(index * BRAID_SIZE, (index + 1) * BRAID_SIZE)
        tie_slice = slice(index * TIE_SIZE, (index + 1) * TIE_SIZE)
        weave, band = world[0][braid_slice], world[1][tie_slice]
        assert (side * band[:, 0] > 0).all() and (side * weave[:, 0] > 0).all()
        center = weave[:WEAVE_SIZE].reshape(3, RING_COUNT, SIDES, 3).mean(axis=(0, 2))
        assert center[0, 1] > 1.90 and center[-1, 1] < 1.10, source
        rail = guide(center, side, covered)
        axis = tangent(center)
        first = pose(weave, band, center, rail, axis, covered)
        push = garment_support(HEIGHTS, first, support, 1.385)
        rail[:, 2] += np.interp(rail[:, 1], HEIGHTS, push)
        new_weave, new_band = pose(weave, band, center, rail, axis, covered)
        # Protect the existing root/cap join. All vertices on a weave ring
        # receive the same root blend.
        root_blend = ease(((1.785 if covered else 1.77) - center[:, 1]) / .17)
        weight = np.concatenate((np.tile(np.repeat(root_blend, SIDES), 3), np.ones(280)))
        world[0][braid_slice] = weave + (new_weave - weave) * weight[:, None]
        world[1][tie_slice] = new_band

    for part, points in zip((braid, tie), world, strict=True):
        _, bounds, pos, normals, rotation, offset, faces = part
        original = pos @ rotation.T + offset
        weight = ease((1.765 - original[:, 1]) / .215)
        touched = np.linalg.norm(points - original, axis=1) > 1e-8
        new_normals = shading(points, faces, normals @ rotation.T, weight)
        pos[touched] = (points[touched] - offset) @ rotation
        normals[touched] = new_normals[touched] @ rotation
        bounds.update(min=pos.min(axis=0).tolist(), max=pos.max(axis=0).tolist())
    write_glb(target, doc, data)


def build(receipt):
    rows = json.loads(receipt.read_text(encoding="utf-8-sig"))
    manifest = (ROOT / "305/hair-fits.json").read_text(encoding="utf-8")
    fits = json.loads(manifest.replace('"./assets/', '"../305/assets/'))
    twins = fits["Feminine"]["twin-braids"]
    twins["note"] = "Twin plaits taper along a smoother shoulder curve and sit below the pashmina edge."
    other_hats = set()
    for row in rows:
        f, parts = row["features"], row["components"]
        if f["hair"] != "twin-braids":
            continue
        hat, top, color = (f[k] for k in ("headwear", "top", "hairColor"))
        if hat not in {"none", "pashmina"}:
            crown = local_path(parts["hair"]).relative_to(ROOT).as_posix()
            twins["fits"].setdefault(hat, {})[color] = "../" + crown
            other_hats.add(hat)
            continue
        target = REV / "assets" / f"twins-{hat}-{top}-{color}.glb"
        support = tuple(local_path(parts[key]) for key in ("base", "top", "headgear") if key in parts)
        fit(local_path(parts["hairLengths"]), target, hat == "pashmina", support)
        twins["fits"][hat]["lengths"][top][color] = "./assets/" + target.name
    for hat in other_hats:
        twins["fits"][hat]["lengths"] = twins["fits"]["none"]["lengths"]
    (REV / "hair-fits.json").write_text(json.dumps(fits, indent=2) + "\n", encoding="utf-8")
    print("Built the 32 Twin Braids fittings")


if __name__ == "__main__":
    build(Path(sys.argv[-1]))
