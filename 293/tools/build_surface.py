"""Remove the thickness ridge along the lower inner surface of Long Bangs."""
import sys
from functools import partial
from pathlib import Path

REV = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REV.parent / "292/tools"))
from build_inside import build, smooth_inside


if __name__ == "__main__":
    build(REV, finish=partial(smooth_inside, lower_thickness=.0057))
