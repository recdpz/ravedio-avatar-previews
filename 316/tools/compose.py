"""Validate the comparison and derive transparent 48/64 px crops from it."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output",type=Path)
    args = parser.parse_args()
    out = args.output
    raw = out/"raw"
    target = out/"chat"
    target.mkdir(exist_ok=True)
    receipt = json.loads((raw/"receipt.json").read_bytes())
    sources = json.loads((out/"source-receipt.json").read_bytes())
    cases = sources["cases"]
    angles = receipt["cameras"]
    expected = {f"{revision}-{case}-skin{skin}-{angle}.png"
        for revision in (314,316) for case in cases for skin in range(4)
        for angle in (angles if skin==3 else ("chat",))}
    assert set(receipt["frames"])==expected
    for name,digest in receipt["frames"].items():
        assert hashlib.sha256((raw/name).read_bytes()).hexdigest()==digest
    scores = []
    portraits = 0
    for name in sorted(expected):
        img = Image.open(raw/name).convert("RGBA")
        assert img.size==(512,512)
        if name.startswith("316-"):
            before = Image.open(raw/("314-"+name[4:])).convert("RGBA")
            a,b = [np.asarray(image.getchannel("A"))>127 for image in (before,img)]
            scores.append(np.count_nonzero(a&b)/np.count_nonzero(a|b))
        if name.endswith("-chat.png"):
            for size in (48,64):
                path = target/(name.removesuffix("-chat.png")+f"-{size}.png")
                img.resize((size,size),Image.Resampling.LANCZOS).save(path)
                portraits += 1
    assert min(scores)>.999
    result = {"matched_renders":len(expected)//2,"small_portraits":portraits,
              "source_glbs":len(sources["glbs"]),"material_revisions":sources["changed_glbs"],
              "minimum_alpha_silhouette_overlap":min(scores),"blender_scenes":receipt["blender"]}
    (out/"verification.json").write_text(json.dumps(result,indent=2)+"\n",newline="\n")
    print(result)


if __name__ == "__main__":
    main()
