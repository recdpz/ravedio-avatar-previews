"""Build the three-angle comparison from the Blender review renders."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "327/tools"))
from package_lob import sheet

STYLES = (("current", "330"), ("feathered", "A · Feathered"),
          ("flipped", "B · Flipped"), ("tucked", "C · Tucked"))
VIEWS = (("threequarter", "Three-quarter"), ("profile", "Side"), ("rear", "Back"))

if __name__ == "__main__":
    output = Path(sys.argv[1])
    rows = [[(f"{title} · {view}", f"{style}-{angle}") for style, title in STYLES]
            for angle, view in VIEWS]
    sheet(output, "comparison.jpg", rows, 305)
