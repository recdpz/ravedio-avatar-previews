"""Package the packed Blender studio and portable catalogue rendering source."""
from argparse import ArgumentParser
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def package(work, mobile, output):
    studio = work / "native321/handoff"
    tools = mobile / "tools/avatar-proof"
    source = work / "native326"
    inputs = {
        "render_catalogue.py": tools / "render_catalogue_blender.py",
        "bake_portraits.py": tools / "bake_catalogue_portraits.py",
        "chat_portrait_blender.py": tools / "chat_portrait_blender.py",
        "render_chat_review_blender.py": tools / "render_chat_review_blender.py",
        "alpha_pack.py": tools / "alpha_pack.py",
        "matrix.json": source / "looks.json",
        "fixtures.json": studio / "fixtures.json",
        "studio-settings.json": source / "studio-settings.json",
    }
    for name in ("r321-ponytail-jersey", "r321-flow-long-beard"):
        inputs[f"scenes/{name}.blend"] = studio / f"scenes/{name}.blend"
    settings = json.loads((source / "studio-settings.json").read_bytes())
    assert all(not row["external_images"] for row in settings.values())
    generated = {
        "requirements.txt": "numpy\nPillow\n",
        "README.md": """# Revision 322 rendering source

Download and extract Ravedio322-catalogue-full.zip alongside this archive.
The catalogue supplies the 620 ordinary GLBs, colors and fitted selectors.
This archive supplies both packed Blender studios, their exact camera and
lighting settings, the 28-look test matrix, and all rendering helpers.

Use Blender 5.2.0. The CPU default works on macOS and Windows. Apple Silicon
can use --device METAL, and a CUDA workstation can use --device CUDA.

From this extracted rendering-source directory:

```sh
blender --background --python-exit-code 1 --python render_catalogue.py -- \
  /absolute/path/to/full-catalogue . /absolute/path/to/render-output \
  --device METAL --depth
python3 -m pip install -r requirements.txt
python3 bake_portraits.py /absolute/path/to/render-output
```

Add --only f-ponytail-none m-flow-cap for a quick two-build smoke render.
Omit --device METAL to use the CPU. Outputs are transparent 384 px PNGs
and, with --depth, matching camera-depth EXRs from the same render.
The separate bake creates 24, 48, 72 and 120 px portraits on cool white.

The packed scenes contain the exact 15-degree reference studio. Read
studio-settings.json for the saved light and camera values. The catalogue's
studio.json records an earlier portable viewer recipe. The packed scenes
supply the lighting for these references.

All helper modules are included in this directory. The renderer preserves
shared component coordinates and switches the selected fitted parts before
rendering. Geometry and materials in the full catalogue carry revision 322.
""",
    }
    files = {name: sha(path) for name, path in inputs.items()}
    files.update({name: hashlib.sha256(value.encode()).hexdigest() for name, value in generated.items()})
    manifest = dict(schema=1, art_revision=322, source_catalogue_sha256="4636150b503826b344bb788e95540a34fc44f0caea062ee560ee0b1239fc6d76",
                    studio_revision=321, files=files)
    with ZipFile(output, "w", ZIP_DEFLATED, compresslevel=3) as archive:
        for name, path in inputs.items():
            archive.write(path, name)
        for name, value in generated.items():
            archive.writestr(name, value)
        archive.writestr("manifest.json", json.dumps(manifest, indent=2) + "\n")
    with ZipFile(output) as archive:
        assert set(archive.namelist()) == set(files) | {"manifest.json"}
        for name, digest in files.items():
            with archive.open(name) as stream:
                assert hashlib.file_digest(stream, "sha256").hexdigest() == digest
    output.with_suffix(".zip.sha256").write_text(f"{sha(output)}  {output.name}\n", encoding="ascii")
    print("Verified rendering archive:", output, output.stat().st_size, "bytes")


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    for name in ("work", "mobile", "output"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    package(args.work, args.mobile, args.output)
