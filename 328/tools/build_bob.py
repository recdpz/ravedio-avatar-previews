"""Sculpt a jaw-length Bob from the revision 322 source hair."""
from argparse import ArgumentParser
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "327/tools"))
from build_lob import cartesian, ease, package, polar


def shape(points, scarf, free_crown):
    angle, y, radius = polar(points)
    height = points[:, 1]
    side = np.abs(angle)
    if scarf:
        # The exposed ends follow the opening. Keep the hair under the wrap fixed.
        exposed = (1 - ease((side - 1.02) / .30)) * ease((1.77 - height) / .26)
        return cartesian(angle + .07 * np.sin(angle) * exposed, y + .030 * exposed,
                         radius - .010 * exposed)

    face = 1 - ease((side - .91) / .93)
    back = ease((side - 1.67) / .55)
    lower = ease((1.98 - height) / .34)
    if free_crown:
        # Keep the back of the bandana seated on the original crown.
        lower *= 1 - back * ease((height - 1.82) / .10)
    else:
        lower *= ease((1.83 - height) / .13)
    end = ease((1.72 - height) / .27)
    # Build soft volume below the cheek, then turn broad sections at the ends.
    phase = 2 * angle + .50 + (2.6 + np.sin(angle)) * lower
    wave = .028 * lower * (1 - .64 * back) * (.50 + .50 * np.sin(phase))
    flick = .034 * end * (.54 + .35 * np.cos(3 * angle + .75) + .11 * np.sin(7 * angle + .2))
    tuck_side = .5 + .5 * np.sin(angle)
    turn = np.sin(angle) * ((.24 + .20 * tuck_side) * end * face - .055 * lower * (1 - end))
    flick += .035 * end**1.3 * np.exp(-((angle + 1.13) / .63)**2)
    turn += .115 * lower * np.sin(2 * angle + .7 + 1.6 * lower)
    turn += .14 * back * end
    # Vary the length around the jaw and break up the hem at the back.
    rise = end * (.041 * face + .013 * np.cos(5 * angle + .5) + .023 * np.sin(angle))
    radius = radius + wave + flick
    if free_crown:
        # Move the front part toward the middle while leaving the crown height intact.
        front = (1 - ease((side - .57) / 1.00)) * ease((height - 2.10) / .105)
        front *= ease(radius / .15)
        turn -= .24 * front
        radius -= .012 * front * (.60 + .40 * np.sin(angle))
    return cartesian(angle + turn, y + rise, radius)


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("base", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    package(args.base, args.output, revision=328, label="Bob",
            note="Jaw-length layers with a soft part and swept ends.", sculpt=shape)
