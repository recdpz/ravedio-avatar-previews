"""Shape upper curl turns, settle the braid rows, and soften the bob."""
import json
import sys
from pathlib import Path

import numpy as np

REV = Path(__file__).resolve().parents[1]
ROOT = REV.parent
sys.path.insert(0, str(ROOT / "297/tools"))
from sculpt import (TAU, CENTER, accessor, cartesian, centerline, cloth_room, deform,
                    ease, envelope, fit_cloth, local_path, polar, rebuild, sample, smooth,
                    turn_along_path, unit)


STYLES = ("curls", "box-braids", "bob")
HEAD = .384


def frame(centers, tangent):
    radial = centers - CENTER
    radial[:, 1] = 0
    radial = unit(radial - np.sum(radial * tangent, axis=1, keepdims=True) * tangent)
    return radial, np.cross(tangent, radial)


def seat_curl(points, ring, theta, parameter, height, covered):
    # Move each section as a whole. The front and temple turns must clear
    # the head; the high buried roots stay seated where they were authored.
    radial = np.column_stack((np.sin(theta), np.zeros(len(theta)), np.cos(theta)))
    d = points - CENTER
    proj = np.sum(d * radial[ring], axis=1)
    reach = np.sqrt(np.maximum(0, (HEAD + .004)**2 - np.sum(d*d, axis=1) + proj*proj))
    needed = np.maximum(reach - proj, 0)
    lift = np.zeros(len(theta))
    np.maximum.at(lift, ring, needed)
    for _ in range(4):
        lift[1:] = np.maximum(lift[1:], lift[:-1] - .007)
        lift[:-1] = np.maximum(lift[:-1], lift[1:] - .007)
    grown = lift.copy()
    grown[1:-1] = np.maximum(lift[1:-1], .22 * lift[:-2] + .56 * lift[1:-1] + .22 * lift[2:])
    exposed = 1 - ease((parameter - .50) / .18)
    if covered:
        exposed *= 1 - ease((height - 1.76) / .19)
    return points + radial[ring] * (grown * exposed)[ring, None]


def curl_lock(points, normals, uv, style, order, tuck=False, inner=False, close_hat=False):
    assert style == "curls"
    parameter, ring, original = centerline(points, uv)
    theta, y, radius = polar(original)
    height = original[:, 1]
    front = 1 - ease((np.abs(theta) - 1.52) / .38)
    lane = round(order * 20)
    takeoff = 1.842 if close_hat else 2.140
    t = np.maximum(0, (takeoff - height) / (takeoff - 1.29))
    # Carry the first turn into the temple and follow with larger coils.
    # Slight differences in phase and lean keep the crown from forming
    # synchronized horizontal ridges.
    start = ease(t / (.24 if close_hat else .28)) * (1 - ease((parameter - .47) / .20))
    lower = ease((1.93 - height) / .29)
    a0 = theta[np.argmin(abs(height - 1.69))] % TAU
    center = .58 * a0 + .42 * (1.18 + (TAU - 2.36) * order)
    drift = np.arctan2(np.sin(center - theta), np.cos(center - theta))
    phase = TAU * (2.70 * t + .08 * t*t) + lane * .76 + .43 * np.sin(lane * 1.36)
    if inner:
        phase += 1.54
    swell = .88 + .12 * np.sin(lane * 2.0 + .60)
    cloth_pressure = ease((np.abs(theta) - .83) / .67) if tuck else np.zeros_like(theta)
    tangential = (.049 if inner else .117) * swell * start * np.sin(phase)
    theta += lower * drift + tangential * (1 - .19 * cloth_pressure)
    base = radius + lower * (.376 - radius)
    loft = (.021 if inner else .046) * swell * start * np.cos(phase) * (1 - .43 * cloth_pressure)
    new_radius = base + loft + .013 * start * (1 - lower)
    if inner:
        # The shorter interior layer stays between the outer turns.
        bank = 1.19 + (TAU - 2.38) * order
        even = np.arctan2(np.sin(bank - theta), np.cos(bank - theta))
        theta += lower * (.84 * even + .038 * np.sin(lane * 1.9 + 3 * t))
        new_radius += lower * (.350 + .014 * np.cos(phase) - new_radius)
        y += .030 * ease((1.62 - height) / .30)
    else:
        y += (.006 + .016 * np.sin(lane * 1.7)) * lower
    if tuck:
        gather = ease((1.53 - height) / .23)
        theta += np.sign(theta) * .16 * gather * front
        new_radius -= .022 * gather
        laid_under_cloth = ease((np.abs(theta) - .96) / .54) * start
        new_radius -= .021 * laid_under_cloth * ease((height - 1.42) / .27)

    path = cartesian(theta, y, new_radius)
    # A slight softening of the centerline samples rounds the turns.
    delta = path - original
    delta[1:-1] = .18 * delta[:-2] + .64 * delta[1:-1] + .18 * delta[2:]
    path = original + delta
    old_t = unit(np.gradient(original, axis=0))
    tangent = unit(np.gradient(path, axis=0))
    across_path = unit(tangent * .72 + np.array([0., .28, 0.]))
    old_r, old_a = frame(original, old_t)
    radial, across = frame(path, across_path)
    guide = np.argmin(abs(height - 1.88))
    local = ring == guide
    q = points[local] - original[guide]
    angle = np.arctan2(q @ old_r[guide], q @ old_a[guide])
    offset_phase = np.angle(np.mean(np.exp(1j * (angle + TAU * uv[local, 0] / 1.25))))
    phase_uv = offset_phase - TAU * uv[:, 0] / 1.25
    c, d = np.cos(phase_uv)[:, None], np.sin(phase_uv)[:, None]
    cap = np.clip(1 - parameter / .072, 0, 1)[ring, None]
    rounded = np.sqrt(1 - cap**2)
    width = .024 if inner else .033 + .003 * np.cos(lane * 1.7)
    thickness = .016 if inner else .023 + .003 * np.sin(lane * 1.3)
    round_section = rounded * (width * c * across[ring] + thickness * d * radial[ring])
    round_normal = unit(rounded * (c * across[ring] + (width / thickness) * d * radial[ring])
                        - cap * across_path[ring])
    original_section = turn_along_path(points - original[ring], old_t[ring], tangent[ring])
    original_normal = turn_along_path(normals, old_t[ring], tangent[ring])
    if inner:
        original_section *= .72
    weight = ease(((takeoff + .035) - height) / .23)[ring, None]
    out = path[ring] + original_section * (1 - weight) + round_section * weight
    out = seat_curl(out, ring, polar(path)[0], parameter, height, close_hat)
    shade = unit(original_normal * (1 - weight) + round_normal * weight)
    if close_hat:
        # Keep the already fitted crown and brim contact. The curl begins
        # lower on the exposed hair, where cloth pressure stops.
        visible_fall = ease((1.865 - height) / .17)[ring, None]
        return points + visible_fall * (out - points), unit(normals + visible_fall * (shade - normals))
    return out, shade


def braid_shape(points, covered):
    theta, y, radius = polar(points)
    h = points[:, 1]
    rear = ease((np.abs(theta) - 1.37) / .69)
    # Reduce the shared outward ledge while letting the lower braids
    # continue to hang outside the torso. All plies and ties move together.
    fall = ease((1.91 - h) / .49)
    flare = np.exp(-((h - 1.445) / .124)**2)
    inset = rear * (.033 * fall + .049 * flare)
    rails = np.exp(-((np.abs(theta) - 2.57) / .29)**2)
    below_crown = ease((2.15 - h) / .26) * ease((h - 1.38) / .17)
    inset += .027 * rails * below_crown
    shoulders = np.exp(-((np.abs(theta) - 1.73) / .33)**2)
    inset += .020 * shoulders * np.exp(-((h - 1.44) / .135)**2)
    if covered:
        inset += .024 * rear * ease((1.84 - h) / .47)
    # The head limits how far a high row can settle. Blend the limit
    # into the drape so a deep channel cannot open between adjacent braids.
    shell = np.sqrt(np.maximum(0, (.384 + .010)**2 - y*y))
    room = np.maximum(radius - shell, 0)
    radius -= room * (1 - np.exp(-inset / np.maximum(room, 1e-6)))
    split = np.arctan2(np.sin(theta - np.pi), np.cos(theta - np.pi))
    part = .49 * np.exp(-(split / .32)**2) * np.exp(-((h - 2.09) / .22)**2)
    theta -= split * part
    moved = cartesian(theta, y, radius)
    near_part = np.exp(-(points[:, 0] / .060)**2)
    nape_side = ease((-.067 - points[:, 2]) / .084) * ease((h - 2.018) / .12)
    moved[:, 0] *= 1 - .25 * near_part * nape_side
    return moved


def bob_shape(points, covered):
    theta, y, radius = polar(points)
    h = points[:, 1]
    tips = ease((1.835 - h) / .32)
    face = 1 - ease((np.abs(theta) - 1.12) / .62)
    # Let the face-framing pieces run a little longer, with loose ends
    # between them and the back. Keep the overall length near the jaw.
    asym = .009 * np.sin(theta)
    layer = .010 * np.cos(7 * theta + .45) + .005 * np.sin(12 * theta)
    y -= tips * (.035 + .056 * face + asym + layer)
    radius += tips * (.021 * face - .011 * (1 - face))
    theta += np.sign(theta) * .065 * tips * face
    # Ease the high sweep down at the front of the part.
    swell = np.exp(-((h - 2.16) / .091)**2) * (1 - ease(np.abs(theta) / 1.8))
    y -= .013 * swell
    if covered:
        radius -= .011 * tips
    return cartesian(theta, y, radius)


def drape_curls(points, allowance, field):
    draped = fit_cloth(points, allowance, field)
    theta, y, radius = polar(draped)
    height = draped[:, 1]
    side = ease((np.abs(theta) - .86) / .65)
    cloth = ease((radius - .24) / .085) * ease((height - 1.39) / .13)
    support = sample(field, theta, height)
    finish = .009 * np.logaddexp(0, (support + .018 - radius) / .009)
    give = .014 * np.exp(-((height - 1.775) / .239)**2)
    return cartesian(theta, y, radius + side * cloth * (give + np.minimum(finish, .058)))


def load(path):
    return json.loads(path.read_text(encoding="utf8"))


def write(path, value):
    (REV / path).write_text(json.dumps(value, indent=2) + "\n", encoding="utf8", newline="\n")


def build(receipt):
    before = load(receipt)
    assert before["revision"] == "297"
    out = REV / "assets"
    out.mkdir(exist_ok=True)
    hair = load(ROOT / "297/hair-fits.json")
    scarf = load(ROOT / "297/pashmina-fits.json")
    sources = load(ROOT / "297/verification/sources.json")
    for styles in hair.values():
        for entry in styles.values():
            for pair in entry["fits"].values():
                for color, p in pair.items():
                    if p.startswith("./"):
                        pair[color] = "../297/" + p[2:]
    for styles in scarf.values():
        for tops in styles.values():
            for top, p in tops.items():
                if p.startswith("./"):
                    tops[top] = "../297/" + p[2:]
    output = {}
    for style in STYLES:
        variant = {}
        entry = hair["Feminine"][style]
        entry["note"] = {"curls": "Sculpted curls with rounded turns from the temples down.",
                         "box-braids": "Woven braids with a closer, softer rear fall.",
                         "bob": "Jaw-length layers with soft face framing."}[style]
        row_paths = {(r["headwear"], r["hairColor"]): local_path(r["parts"]["hair"])
                     for r in before["rows"] if r["hair"] == style and r["top"] == "open"}
        for (hat, color), existing in row_paths.items():
            covered = hat == "pashmina"
            close_hat = style == "curls" and hat in {"cap", "beanie", "bucket", "cowboy", "headband"}
            source = row_paths["none", color] if covered else existing
            if style == "curls":
                source = ROOT / sources[source.name]
            key = source, covered, close_hat
            if key not in variant:
                target = out / f"{style}-{hat}-{color}.glb"
                if style == "curls":
                    def edit(*args, **kwargs):
                        return curl_lock(*args, **kwargs, close_hat=close_hat)
                    rebuild(source, target, style, tuck=covered, edit_lock=edit,
                            inner_rows=range(3, 18) if not close_hat else range(4, 17))
                else:
                    shape = braid_shape if style == "box-braids" else bob_shape
                    deform(source, target, lambda points: shape(points, covered))
                variant[key] = "./assets/" + target.name
                output[target.name] = source.relative_to(ROOT).as_posix()
            entry["fits"].setdefault(hat, {})[color] = variant[key]
        field = envelope(REV / entry["fits"]["pashmina"]["default"])
        for _ in range(8):
            field = np.maximum.reduce((field, np.roll(field, 1, 1) - .004,
                                       np.roll(field, -1, 1) - .004,
                                       np.vstack((field[:1], field[:-1])) - .008,
                                       np.vstack((field[1:], field[-1:])) - .008))
        field = smooth(field, 2.5, 4.2)
        for top, p in scarf["Feminine"][style].items():
            source = (REV / p).resolve()
            # The existing 297 Curls variant already has its drape allowance.
            # Restart from the fitted 296 cloth to avoid accumulating bulk.
            if style == "curls":
                source = ROOT / sources[source.name]
            target = out / f"scarf-{style}-{top}.glb"
            allowance = cloth_room(source, field)
            fit = drape_curls if style == "curls" else fit_cloth
            deform(source, target, lambda points: fit(points, allowance, field))
            scarf["Feminine"][style][top] = "./assets/" + target.name
            output[target.name] = source.relative_to(ROOT).as_posix()
        print(style, len(variant), flush=True)
    write("hair-fits.json", hair)
    write("pashmina-fits.json", scarf)
    write("verification/sources.json", output)


if __name__ == "__main__":
    build(Path(sys.argv[-1]))
