"""Make the chosen and rebuilt Bob comparison sheets."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "327/tools"))
from package_lob import sheet

if __name__ == "__main__":
    output = Path(sys.argv[1])
    views = (("front", "Front"), ("threequarter", "Three-quarter"), ("profile", "Side"), ("rear", "Back"))
    sheet(output, "comparison.jpg",
          [[(f"{title} · {label}", f"{style}-{angle}") for angle, label in views]
           for style, title in (("chosen", "Chosen"), ("curtain", "New"))], 305)
    sheet(output, "angles.jpg",
          [[(label, f"curtain-{angle}") for angle, label in group] for group in (
              views, (("rightprofile", "Right side"), ("rearquarter", "Rear three-quarter"),
                      ("above", "Above"), ("underneath", "Underneath")))], 280)
