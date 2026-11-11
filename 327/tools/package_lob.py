"""Build comparison sheets and a portable update for the revision 322 catalogue."""
from argparse import ArgumentParser
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

from PIL import Image, ImageDraw, ImageFont


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def sheet(root, filename, rows, size):
    columns = max(len(row) for row in rows)
    canvas = Image.new("RGB", (columns * size, len(rows) * (size + 27)), "#172331")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default(size=14)
    for y, row in enumerate(rows):
        for x, (label, file) in enumerate(row):
            point = (x * size, y * (size + 27))
            draw.text((point[0] + 12, point[1] + 5), label, font=font, fill="white")
            with Image.open(root / "review" / (file + ".png")) as source:
                portrait = source.convert("RGBA").resize((size, size), Image.Resampling.LANCZOS)
            canvas.paste(portrait, (point[0], point[1] + 27), portrait)
    canvas.save(root / filename, quality=94)


def package(base, root):
    catalogue = json.loads((root / "catalogue.json").read_bytes())
    receipt = json.loads((root / "receipt.json").read_bytes())
    revision = catalogue["revision"]
    label = receipt["label"]
    scene = f"Ravedio{revision}-{label}.blend"
    angles = ("front","threequarter","profile","rear")
    labels = ("Front","Three-quarter","Left","Back")
    sheet(root, "comparison.jpg", [
        [(f"{title} · {label}", f"{number}-none-default-{angle}") for angle, label in zip(angles, labels)]
        for number, title in ((322,"Original Bob"),(revision,label))
    ], 290)
    sheet(root, "angles.jpg", [
        [(label, f"{revision}-none-default-" + angle) for angle, label in zip(angles, labels)],
        [(label, f"{revision}-none-default-" + angle) for angle, label in (
            ("rightprofile","Right"),("rearquarter","Rear three-quarter"),("above","Above"),("underneath","Underneath"))],
    ], 265)
    hats = (("cap","Cap"),("beanie","Beanie"),("bucket","Bucket hat"),("cowboy","Cowboy hat"),
            ("ears","Animal ears"),("headband","Bandana"),("pashmina","Pashmina"))
    sheet(root, "headwear.jpg", [
        [(label, f"{revision}-{hat}-default-{angle}") for hat, label in hats]
        for angle in ("threequarter","rearquarter")
    ], 240)
    sheet(root, "ombre.jpg", [
        [(label, f"{revision}-{hat}-ombre-{angle}") for hat, angle, label in (
            ("none","threequarter","Ombre · Front"),("none","rear","Ombre · Back"),
            ("pashmina","threequarter","Ombre · Pashmina"))]
    ], 310)

    source = json.loads((base / "catalogue.json").read_bytes())
    updated = [catalogue["components"][row["sha256"]]["file"] for row in receipt["replacements"].values()]
    removed = [source["components"][digest]["file"] for digest in receipt["replacements"]]
    files = ["catalogue.json", "overlay.json", "receipt.json", "fit-review.json", scene, *updated]
    digests = {name: sha(root / name) for name in files}
    for name in updated:
        assert digests[name] == Path(name).stem
    manifest = dict(revision=revision, base_revision=322, base_catalogue_sha256=sha(base/"catalogue.json"),
                    replaced_paths=removed, files=digests)
    readme = f"""# Revision {revision} {label} source update

Apply the eight new GLBs and catalogue.json over a copy of the extracted
revision 322 full catalogue. Validate the base catalogue digest against
delta-manifest.json before replacing it. Use the updated catalogue.json
to resolve the new {label} bindings. The manifest.json shipped with 322
describes that original archive. The delta manifest covers this update.

{scene} is the packed editable studio model with the new bare
{label} and a feminine jersey. Both fitted hair finishes and the pashmina
version are included in the eight source GLBs. The fit-review report
records checks against the original fitted garments and headwear.
"""
    (root / "delivery").mkdir(exist_ok=True)
    archive_path = root / f"delivery/Ravedio{revision}-{label.lower()}-source.zip"
    with ZipFile(archive_path, "w", ZIP_DEFLATED, compresslevel=3) as archive:
        for name in files:
            archive.write(root / name, name)
        archive.writestr("delta-manifest.json", json.dumps(manifest, indent=2) + "\n")
        archive.writestr("README.md", readme)
    with ZipFile(archive_path) as archive:
        assert archive.testzip() is None
        for name, expected in digests.items():
            with archive.open(name) as stream:
                assert hashlib.file_digest(stream, "sha256").hexdigest() == expected
    archive_path.with_suffix(".zip.sha256").write_text(f"{sha(archive_path)}  {archive_path.name}\n", encoding="ascii")
    print("Verified", archive_path.name, archive_path.stat().st_size, "bytes")


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("base", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    package(args.base, args.output)
