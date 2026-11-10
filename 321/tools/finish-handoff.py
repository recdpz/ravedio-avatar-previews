"""Check the 321 portrait references and build the portable art handoff."""
from argparse import ArgumentParser
import hashlib
import json
from pathlib import Path
import shutil
import sys
from zipfile import ZIP_DEFLATED, ZipFile

import numpy as np
from PIL import Image


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream,"sha256").hexdigest()


def write(path,value):
    path.write_text(json.dumps(value,sort_keys=True,indent=2)+"\n",encoding="utf8",newline="\n")


def finish(root,tools,archive,art_commit):
    sys.path.insert(0,str(tools))
    from alpha_pack import Q, plate_transfer
    from linear_depth_exr import read_depth

    source = Path(__file__).resolve().parents[1]
    index = json.loads((root/"fixtures.json").read_bytes())
    assert index["revision"]==321 and len(index["pairs"])==16 and len(index["fixtures"])==4
    assert index["plate_srgb"]==[241,244,250]
    index["art_commit"] = art_commit
    files = {"fixtures.json","palette.json"}
    for fixture in index["fixtures"].values():
        for part in fixture["parts"].values():
            assert sha(root/part["file"])==part["sha256"]
            files.add(part["file"])
        if "scene" in fixture:
            files.add(fixture["scene"])

    forward, reverse = plate_transfer()
    background = forward[index["plate_srgb"]].astype(np.float64)
    for name,pair in index["pairs"].items():
        size = index["size"]
        with Image.open(root/pair["color"]) as image:
            rgba = np.array(image.convert("RGBA"))
        assert rgba.shape==(size,size,4)
        depth = read_depth(root/pair["depth"],size)
        visible = rgba[...,3]>127
        recorded = np.isfinite(depth)&(depth>0)&(depth<16)
        score = np.count_nonzero(visible&recorded)/np.count_nonzero(visible|recorded)
        assert score>=.98,(name,score)
        pair["color_depth_overlap"] = round(score,6)
        files.update((pair["color"],pair["depth"]))
        alpha = rgba[...,3,None].astype(np.float64)/255
        linear = forward[rgba[...,:3]]*alpha+background*(1-alpha)
        previews = {}
        for width in (48,64,120):
            values = np.stack([np.asarray(Image.fromarray(linear[...,channel].astype(np.float32)).resize(
                (width,width),Image.Resampling.LANCZOS)) for channel in range(3)],axis=-1)
            rgb = reverse[np.rint(np.clip(values,0,Q)).astype(np.int64)]
            path = f"references/{name}-cool-{width}.png"
            assert rgb[0,0].tolist()==index["plate_srgb"]
            Image.fromarray(rgb).save(root/path)
            previews[str(width)] = path
            files.add(path)
        pair["previews"] = previews
    write(root/"fixtures.json",index)
    for name,origin in (("index.html",source/"tools/review.html"),("README.md",source/"MOBILE-REVIEW.md")):
        shutil.copyfile(origin,root/name)
        files.add(name)
    receipt = {file:sha(root/file) for file in sorted(files)}
    write(root/"sha256.json",receipt)
    archive.parent.mkdir(parents=True,exist_ok=True)
    with ZipFile(archive,"w",ZIP_DEFLATED,compresslevel=6) as package:
        for path in (*receipt,"sha256.json"):
            package.write(root/path,path)
    with ZipFile(archive) as package:
        assert set(package.namelist())==receipt.keys()|{"sha256.json"}
        for name,digest in receipt.items():
            with package.open(name) as stream:
                assert hashlib.file_digest(stream,"sha256").hexdigest()==digest,name
    archive.with_suffix(".zip.sha256").write_text(f"{sha(archive)}  {archive.name}\n",encoding="ascii")
    print(f"Verified {len(index['pairs'])} color/depth pairs and {len(receipt)} archive entries.")
    print("Minimum color/depth overlap",min(pair["color_depth_overlap"] for pair in index["pairs"].values()))


if __name__=="__main__":
    parser = ArgumentParser(description=__doc__)
    for name in ("root","tools","archive"):
        parser.add_argument(name,type=Path)
    parser.add_argument("art_commit")
    args = parser.parse_args()
    finish(args.root,args.tools,args.archive,args.art_commit)
