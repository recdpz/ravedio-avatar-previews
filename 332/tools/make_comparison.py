"""Make shape and texture comparisons from the study renders."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "327/tools"))
from package_lob import sheet

if __name__ == "__main__":
    output = Path(sys.argv[1])
    shapes = (("tucked", "Tucked"), ("volume", "Rounded volume"), ("side-tuck", "One-sided tuck"))
    textures = (("smooth", "Smooth"), ("brushed", "Brushed"), ("channels", "Sculpted channels"))
    views = (("threequarter", "Three-quarter"), ("profile", "Side"), ("rear", "Back"))
    sheet(output, "shapes.jpg",
          [[(f"{label} · {view}", f"{shape}-brushed-{angle}") for shape, label in shapes]
           for angle, view in views], 335)
    sheet(output, "textures.jpg",
          [[(f"{label} · {view}", f"tucked-{texture}-{angle}") for texture, label in textures]
           for angle, view in views], 335)
