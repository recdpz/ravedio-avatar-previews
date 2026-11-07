"""Assemble QA contact sheets from captures made by review.cjs."""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


REV = Path(__file__).resolve().parents[1]
CAPTURES = Path(sys.argv[1])
VERIFICATION = REV / "verification"
REPORT = json.loads((CAPTURES / "browser.json").read_text(encoding="utf8"))
BG = "#16202b"
CELL = "#29394c"
LABEL = "#e2eaf3"
FONT = Path("C:/Windows/Fonts/segoeui.ttf")


def font(size):
    return ImageFont.truetype(str(FONT), size) if FONT.is_file() else ImageFont.load_default(size=size)

HATS = {
    "none": "Bare head", "cap": "Cap", "beanie": "Beanie", "bucket": "Bucket hat",
    "cowboy": "Cowboy hat", "headband": "Bandana", "ears": "Animal ears",
    "pashmina": "Pashmina",
}
COLORS = {
    "default": "Original", "black": "Black", "darkbrown": "Brown", "auburn": "Auburn",
    "blonde": "Blonde", "platinum": "Platinum", "pink": "Pink", "purple": "Purple",
    "ombre": "Ombré",
}


def contact_sheet(path, title, labels, rows, width=190):
    margin = 20
    col_gap = 8
    header = 55
    label_height = 27
    height = header + label_height + sum(size + col_gap for size, _ in rows) + margin
    canvas_width = 2 * margin + len(labels) * (width + col_gap) - col_gap
    canvas = Image.new("RGB", (canvas_width, height), BG)
    draw = ImageDraw.Draw(canvas)
    draw.text((margin, 16), title, fill=LABEL, font=font(24))
    for index, label in enumerate(labels):
        x = margin + index * (width + col_gap) + width // 2
        draw.text((x, header), label, anchor="mt", fill=LABEL,
                  font=font(16))
    y = header + label_height
    for size, names in rows:
        for index, name in enumerate(names):
            x = margin + index * (width + col_gap)
            canvas.paste(CELL, (x, y, x + width, y + size))
            with Image.open(CAPTURES / (name + ".png")) as source:
                rgba = source.convert("RGBA").resize((size, size), Image.Resampling.LANCZOS)
                canvas.paste(rgba, (x + (width - size) // 2, y), rgba)
        y += size + col_gap
    canvas.save(path, quality=92, subsampling=0)


def hair_rows(angles):
    return [(190, [f"{hat}-default-{angle}" for hat in HATS]) for angle in angles]


contact_sheet(VERIFICATION / "headwear.jpg", "Long Bangs  /  Headwear fits",
              list(HATS.values()), hair_rows(["threequarter", "profile", "rear"]))
contact_sheet(VERIFICATION / "colors.jpg", "Long Bangs  /  Colors and 120 px chat portraits",
              list(COLORS.values()), [
                  (164, [f"color-{color}-threequarter" for color in COLORS]),
                  (120, [f"chat-{color}-front" for color in COLORS]),
              ], width=164)
contact_sheet(CAPTURES / "other-angles.jpg", "Long Bangs  /  Front, right, rear three-quarter, above, below",
              list(HATS.values()), hair_rows(["front", "rightprofile", "rearquarter", "top", "underside"]))
contact_sheet(CAPTURES / "pashmina-wardrobe.jpg", "Long Bangs  /  Pashmina across tops",
              REPORT["pashminaTops"], [(190, [f"scarf-{top}-{angle}" for top in REPORT["pashminaTops"]])
                                     for angle in ("threequarter", "profile", "rear")])
contact_sheet(CAPTURES / "ombre-fits.jpg", "Long Bangs  /  Ombré by fit",
              list(HATS.values()), [(190, [f"{hat}-ombre-{angle}" for hat in HATS])
                                   for angle in ("threequarter", "rear")])
(VERIFICATION / "browser.json").write_text(json.dumps(REPORT, indent=2) + "\n",
                                          encoding="utf8", newline="\n")
