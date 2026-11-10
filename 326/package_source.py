"""Package the complete current source catalogue as verified, ordinary GLBs."""
import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def package(root, target):
    catalogue_file = root / "catalogue.json"
    catalogue = json.loads(catalogue_file.read_bytes())
    components = catalogue["components"]
    assert catalogue["revision"] == 322 and len(catalogue["fit_rows"]) == 1792 and len(components) == 620

    def verify_roles(data):
        if isinstance(data, dict):
            for value in data.values():
                verify_roles(value)
        elif data is not None:
            assert data in components, data

    for key in ("fit_rows", "independent_roles", "groom_mouths"):
        verify_roles(catalogue[key])
    paths = {"catalogue.json": sha(catalogue_file)}
    for digest, entry in components.items():
        path = root / entry["file"]
        assert root in path.resolve().parents and not path.is_symlink()
        assert path.stat().st_size == entry["bytes"] and sha(path) == digest
        paths[entry["file"]] = digest
    for name in ("palette", "studio", "finish"):
        path = root / catalogue[name]
        paths[catalogue[name]] = sha(path)
    for path in (root / catalogue["shared_jersey_dyes_dir"]).rglob("*.png"):
        paths[path.relative_to(root).as_posix()] = sha(path)
    manifest = dict(schema="ravedio-catalogue-archive-1", revision=322, artwork_commit="5a8dd51",
                    component_count=len(components), fit_rows=len(catalogue["fit_rows"]), files=paths)
    pending = target.with_suffix(".partial")
    with ZipFile(pending, "w", ZIP_DEFLATED, compresslevel=1) as archive:
        for name in sorted(paths):
            archive.write(root / name, name)
        archive.writestr("manifest.json", json.dumps(manifest, indent=2) + "\n")
    with ZipFile(pending) as archive:
        assert len(archive.namelist()) == len(paths) + 1
        for name, digest in paths.items():
            with archive.open(name) as stream:
                assert hashlib.file_digest(stream, "sha256").hexdigest() == digest, name
    pending.replace(target)
    target.with_suffix(".zip.sha256").write_text(f"{sha(target)}  {target.name}\n", encoding="ascii")
    print("Verified", target, target.stat().st_size, "bytes")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("target", type=Path)
    args = parser.parse_args()
    package(args.root.resolve(), args.target)
