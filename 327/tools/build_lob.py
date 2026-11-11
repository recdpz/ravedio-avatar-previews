"""Sculpt the feminine Lob into the content-addressed source catalogue."""
from argparse import ArgumentParser
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "296/tools"))
from drape import cartesian, deform, ease, garment_envelope, keep_shoulder_room, polar, soften_field


def sha(path):
    with path.open("rb") as file:
        return hashlib.file_digest(file, "sha256").hexdigest()


def load(path):
    return json.loads(path.read_bytes())


def write(path, data):
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def shape(points, scarf):
    theta, y, radius = polar(points)
    height = points[:, 1]
    side = np.abs(theta)
    drop = ease((1.90 - height) / .46)
    bend = ease((1.87 - height) / .24)
    tip = ease((1.66 - height) / .23)
    face = 1 - ease((side - 1.11) / 1.02)
    # Shoulder-length front sections with shorter, staggered layers at the back.
    layer = .016 * np.cos(6 * theta + .35) + .008 * np.sin(9 * theta)
    length = .086 + .066 * face + layer + .012 * np.sin(theta)
    curl = .044 + .018 * np.sin(5 * theta + .55) + .012 * face
    # Follow the jaw in, then let the free ends turn out and forward in loose sections.
    tuck = .025 * bend * np.exp(-((height - 1.64) / .112)**2)
    sweep = np.sin(theta) * (.13 * bend * (1 - tip) - .29 * tip * (.34 + .66 * face))
    if scarf:
        # Preserve the cloth fit around the nape and let the ends follow the front opening.
        exposed = (1 - ease((side - 1.02) / .30)) * ease((1.75 - height) / .23)
        return cartesian(theta - .22 * np.sin(theta) * exposed, y - .41 * length * drop * exposed,
                         radius - exposed * (.021 * tip + tuck * .22))
    turn = .014 * tip**2 * (.5 + .5 * np.sin(5 * theta + .55))
    return cartesian(theta + sweep, y - length * drop + turn, radius - tuck + curl * tip)


def keep_head_room(before, after):
    _, original_y, original_radius = polar(before)
    angle, y, radius = polar(after)
    old_head = np.sqrt(np.maximum(0, .384**2 - original_y**2))
    new_head = np.sqrt(np.maximum(0, .384**2 - y**2))
    # Carry the pre-existing clearance of each shell through the side of the head.
    # The buried liner remains buried and the outer layer stays outside the skin.
    clearance = np.minimum(original_radius - old_head, .013)
    active = (new_head > 0) & (np.linalg.norm(after - before, axis=1) > 1e-7)
    radius = np.where(active, np.maximum(radius, new_head + clearance), radius)
    return cartesian(angle, y, radius)


def package(base, output, *, revision=327, label="Lob",
            note="Collarbone-length layers with a soft outward turn.", sculpt=None):
    if sculpt is None:
        def sculpt(points, scarf, free_crown):
            return shape(points, scarf)
    catalogue = load(base / "catalogue.json")
    assert catalogue["revision"] == 322
    overlay = load(base / "overlay.json")
    components = catalogue["components"]
    rows = {key: row for key, row in catalogue["fit_rows"].items() if key.startswith("Feminine/bob/")}
    assert len(rows) == 128
    bare = {row["hair"] for key, row in rows.items() if key.split("/")[2] == "none"}
    assets = output / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    # Use the torso and all eight tops as clearance surfaces.
    def part(digest):
        return base / components[digest]["file"]
    style = catalogue["independent_roles"]["Feminine"]
    bodies = {entry["clothed"] for entry in style["bases"].values()}
    tops = {row["top"] for row in rows.values()}
    garments = [(part(digest), lambda name: "torso" in name.lower()) for digest in sorted(bodies)]
    garments.extend((part(digest), lambda name: not any(token in name.lower() for token in ("sleeve", "cuff", "cord", "string")))
                    for digest in sorted(tops))
    clearance = soften_field(garment_envelope(garments), 8)
    changes = {}
    for key, row in rows.items():
        digest = row["hair"]
        scarf = key.split("/")[2] == "pashmina"
        if digest not in changes:
            source = part(digest)
            assert sha(source) == digest
            pending = output / "hair-pending.glb"
            def warp(points):
                moved = keep_head_room(points, sculpt(points, scarf, digest in bare))
                if scarf:
                    return moved
                return keep_shoulder_room(clearance, points, moved)
            distance = deform(source, pending, warp)
            assert distance > (.02 if revision == 327 else .01)
            revised = sha(pending)
            file = assets / (revised + ".glb")
            pending.replace(file)
            changes[digest] = dict(sha256=revised, pashmina=scarf, max_displacement=distance)
            if revision != 327:
                changes[digest]["free_crown"] = digest in bare
            components[revised] = {"file": "assets/" + file.name, "bytes": file.stat().st_size}
        assert changes[digest]["pashmina"] == scarf
        row["hair"] = changes[digest]["sha256"]

    others = {value for key, row in catalogue["fit_rows"].items() if key not in rows for value in row.values()}
    assert not set(changes) & others, "A Bob source is shared by another style"
    for source, digest in overlay["components"].items():
        if digest in changes:
            overlay["components"][source] = changes[digest]["sha256"]
    for digest in changes:
        components.pop(digest)
    for entry in components.values():
        destination = output / entry["file"]
        if destination.exists():
            continue
        original = base / entry["file"]
        try:
            os.link(original, destination)
        except OSError:
            shutil.copyfile(original, destination)
    for role in ("palette", "studio", "finish"):
        path = catalogue[role]
        shutil.copyfile(base / path, output / path)
    dyes = catalogue["shared_jersey_dyes_dir"]
    shutil.copytree(base / dyes, output / dyes, dirs_exist_ok=True)
    catalogue["revision"] = revision
    catalogue["options"]["builds"]["Feminine"]["hair"]["bob"] = label
    overlay["hairLabels"] = {"Feminine": {"bob": {"label":label, "note":note}}}
    write(output / "catalogue.json", catalogue)
    write(output / "overlay.json", overlay)
    write(output / "receipt.json", {"revision":revision, "base_revision":322, "style_id":"bob", "label":label,
                                     "fit_rows":len(rows), "replacements":changes})
    print(f"Updated {len(rows)} fitted rows using {len(changes)} new {label} GLBs", flush=True)


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("base", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    package(args.base, args.output)
