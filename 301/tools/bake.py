"""Bake the shared brown into resolved hair and groom GLBs without rewriting geometry."""
import argparse
import copy
import hashlib
import json
import os
import struct
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

REVISION = Path(__file__).resolve().parents[1]
ROOT = REVISION.parent
BROWN = (0.160, 0.059, 0.030)  # Linear RGB, between the previous dark and light originals.
GROOM_SHADE = 0.82


def read_glb(path):
    data = path.read_bytes()
    magic, version, size, n, kind = struct.unpack_from("<4sIII4s", data)
    if (magic, version, size, kind) != (b"glTF", 2, len(data), b"JSON"):
        raise ValueError(f"Expected a glTF 2.0 binary file at {path}")
    return json.loads(data[20:20 + n]), data[20 + n:]


def encode_glb(model, trailing_chunks):
    data = json.dumps(model, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    data += b" " * (-len(data) % 4)
    size = 20 + len(data) + len(trailing_chunks)
    return struct.pack("<4sIII4s", b"glTF", 2, size, len(data), b"JSON") + data + trailing_chunks


def asset_path(uri, preview_url):
    root_url = urljoin(preview_url, "../")
    absolute = urljoin(preview_url, uri)
    base = urlsplit(root_url)
    path = urlsplit(absolute)
    if (path.scheme, path.netloc) != (base.scheme, base.netloc) or not path.path.startswith(base.path):
        raise ValueError(f"Component outside the preview catalogue: {uri}")
    relative = Path(unquote(path.path[len(base.path):]))
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"Invalid component path: {uri}")
    return ROOT / relative


def brown_factor(name, style, previous):
    if "crisp pulled roots220" in name:
        # Color is in the vertex RGB. Scale its three channels through the
        # material factor so the authored variation and vertex alpha survive.
        vertex_base = (0.2155, 0.0710, 0.0313)
        return [0.99 * channel / authored for channel, authored in zip(BROWN, vertex_base)]
    if style == "ponytail":
        if "sculpted front locks222" in name or "chestnut212 0" in name:
            shade = 0.98
        elif "chestnut212 2" in name:
            shade = 1.03
        else:
            shade = 1.0
    elif "sculpted" in name or "terminal tips" in name:
        # Keep smaller tonal separations between sculpted locks.
        shade = {0.162: 0.94, 0.1878: 1.0, 0.2195: 1.06}.get(round(previous[0], 4), 1.0)
    else:
        shade = 1.0
    return [channel * shade for channel in BROWN]


def recolor(model, role, style):
    changes = 0
    for material in model.get("materials", []):
        name = material.get("name", "")
        if role == "groom":
            if not name.startswith("Groom / ") or "stubble" in name.lower():
                continue
        elif not name.startswith("Hair") or any(word in name.lower() for word in ("tie", "band", "elastic", "metal")):
            continue
        pbr = material["pbrMetallicRoughness"]
        previous = pbr.get("baseColorFactor", [1, 1, 1, 1])
        rgb = [channel * GROOM_SHADE for channel in BROWN] if role == "groom" else brown_factor(name, style, previous)
        pbr["baseColorFactor"] = [*rgb, previous[3]]
        extras = material.get("extras", {})
        if "hairBase252" in extras:
            extras["hairBase252"] = pbr["baseColorFactor"]
        changes += 1
    return changes


def swatch_hex(linear):
    def byte(channel):
        srgb = 12.92 * channel if channel <= 0.0031308 else 1.055 * channel ** (1 / 2.4) - 0.055
        return f"{round(255 * srgb):02X}"
    return "#" + "".join(byte(channel) for channel in linear)


def bake(receipt, preview_url):
    assets = REVISION / "assets"
    assets.mkdir(exist_ok=True)
    components = {}
    processed = set()
    for row in receipt:
        feature = row["features"]
        if feature["hairColor"] != "default":
            continue
        for role in ("hair", "hairLengths", "groom"):
            if role not in row["components"]:
                continue
            source = asset_path(row["components"][role], preview_url)
            key = source.relative_to(ROOT).as_posix()
            if key in processed:
                continue
            processed.add(key)
            original, trailing = read_glb(source)
            model = copy.deepcopy(original)
            if not recolor(model, role, feature["hair"]):
                continue
            data = encode_glb(model, trailing)
            name = f"{hashlib.sha256(data).hexdigest()[:18]}-{role}.glb"
            target = assets / name
            if not target.exists():
                target.write_bytes(data)
            assert target.read_bytes() == data, target
            # The JSON material colors are the only data that may differ.
            assert {k: v for k, v in model.items() if k != "materials"} == {
                k: v for k, v in original.items() if k != "materials"}
            components["../" + key] = "./assets/" + name
    report = {"brownLinear": BROWN, "brownSrgb": swatch_hex(BROWN), "components": dict(sorted(components.items()))}
    (REVISION / "material-assets.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Recolored {len(components)} component paths to {len(set(components.values()))} GLBs")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--preview-url", default=os.environ.get("PREVIEW_ORIGIN", "http://127.0.0.1:9251") + "/300/")
    args = parser.parse_args()
    bake(json.loads(args.receipt.read_text(encoding="utf-8-sig")), args.preview_url)
