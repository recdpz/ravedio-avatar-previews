"""Verify paired chat renders and build native-size Cool white comparisons."""
import argparse
import html
import json
from pathlib import Path
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0,str(Path(__file__).resolve().parent))
from pack import sha, write

PLATE = [241,244,250]
SIZE = 384
DISPLAY = (48,64,120,SIZE)
CASES = {
    "curls-pashmina":"Curls · Clear Reading glasses",
    "flow-cap":"Flow · Dark Wayfarers",
    "twin-jersey-pashmina":"Twin Braids · Pashmina",
    "ponytail-beanie-jersey":"Ombre Ponytail · Beanie",
    "twin-jersey-bare":"Twin Braids · Uncovered",
    "flow-cap-bare-eyes":"Flow · Uncovered eyes",
}


def package(generated,approved,out,tools):
    sys.path.insert(0,str(tools))
    from alpha_pack import Q,plate_transfer
    from linear_depth_exr import read_depth
    manifest = json.loads((generated/"renders.json").read_bytes())
    original = json.loads((approved/"handoff.json").read_bytes())
    assert manifest["yaw_degrees"]==original["yaw_degrees"]==15
    assert manifest["plate_srgb"]==original["background_srgb"]==PLATE
    assert manifest["camera_span"]==original["camera_span"]==1.16
    assert manifest["target_y"]==original["target_y"]==1.85
    assert manifest["size"]==SIZE and manifest["depth_alpha_threshold"]==.5
    assert len(manifest["pairs"])==32
    forward,reverse = plate_transfer()
    plate = forward[PLATE].astype(np.float64)
    yy,xx = np.mgrid[:SIZE,:SIZE]
    circle = (xx+.5-SIZE/2)**2+(yy+.5-SIZE/2)**2 < (SIZE/2)**2
    receipt = {}
    for revision in (308,314):
        for key in CASES:
            for skin in range(4):
                identity = f"r{revision}-{key}-skin{skin}"
                if identity in manifest["pairs"]:
                    pair = manifest["pairs"][identity]
                    color,depth = generated/pair["color"],generated/pair["depth"]
                    assert (sha(color),sha(depth))==(pair["color_sha256"],pair["depth_sha256"])
                else:
                    assert revision==308 and identity in original["reference_pairs"]
                    rel = "references/"+identity
                    color,depth = approved/rel/"color-rgba.png",approved/rel/"depth-z.exr"
                    for source in (color,depth):
                        assert sha(source)==original["files"][source.relative_to(approved).as_posix()]
                rgba = np.asarray(Image.open(color).convert("RGBA"))
                assert rgba.shape==(SIZE,SIZE,4)
                z = read_depth(depth,SIZE)
                visible = rgba[...,3]>127
                recorded = (z>0)&(z<16)
                score = np.count_nonzero(visible&recorded)/np.count_nonzero(visible|recorded)
                assert score>=.98 and not np.any(visible&(yy<SIZE*.56)&~circle),(identity,score)
                folder = out/"references"/identity
                folder.mkdir(parents=True)
                shutil.copyfile(color,folder/"color-rgba.png")
                shutil.copyfile(depth,folder/"depth-z.exr")
                a = rgba[...,3,None].astype(np.float64)/255
                linear = forward[rgba[...,:3]]*a+plate*(1-a)
                for size in DISPLAY:
                    sample = np.stack([np.asarray(Image.fromarray(linear[...,c].astype(np.float32)).resize(
                        (size,size),Image.Resampling.LANCZOS)) for c in range(3)],axis=-1)
                    rgb = reverse[np.rint(np.clip(sample,0,Q)).astype(np.int64)]
                    assert rgb[0,0].tolist()==PLATE
                    Image.fromarray(rgb).save(folder/f"cool-{size}.png")
                receipt[identity] = {"art_revision":revision,"skin":skin,"case":key,
                    "rgba_sha256":sha(color),"depth_sha256":sha(depth),"color_depth_overlap":round(score,6)}
    write(out/"references/receipt.json",{"recipe":{k:v for k,v in manifest.items() if k!="pairs"},
                                        "pairs":receipt})
    board(out)
    page(out)
    print("Verified",len(receipt),"aligned color/depth pairs; minimum coverage agreement",
          min(v["color_depth_overlap"] for v in receipt.values()),flush=True)


def board(out):
    canvas = Image.new("RGB",(700,106+74*len(CASES)),"#141C2A")
    pen = ImageDraw.Draw(canvas)
    pen.text((14,14),"Chat portraits on the deepest tone",font=ImageFont.load_default(22),fill="#F1F4FA")
    pen.text((14,46),"15° | Cool white | Actual 48 and 64 px",font=ImageFont.load_default(14),fill="#B7C5DC")
    for col,revision in enumerate((308,314)):
        pen.text((328+col*170,76),str(revision),font=ImageFont.load_default(15),fill="#F1F4FA")
    for row,(case,label) in enumerate(CASES.items()):
        y = 99+row*74
        pen.text((14,y+23),label,font=ImageFont.load_default(15),fill="#F1F4FA")
        for col,revision in enumerate((308,314)):
            for size,dx in ((48,0),(64,62)):
                img = Image.open(out/f"references/r{revision}-{case}-skin3/cool-{size}.png")
                mask = Image.new("L",(size,size))
                ImageDraw.Draw(mask).ellipse((0,0,size-1,size-1),fill=255)
                canvas.paste(img,(328+col*170+dx,y+(64-size)//2),mask)
    canvas.save(out/"deepest-tone.png")


def page(out):
    options = "".join(f'<option value="{i}" {"selected" if i==3 else ""}>Skin {i+1}</option>' for i in range(4))
    rows = []
    for key,label in CASES.items():
        cells = ["".join(f'<img width="{s}" height="{s}" alt="{s} pixels" data-revision="{r}" data-case="{key}" '
                  f'src="references/r{r}-{key}-skin3/cool-{s}.png">' for s in (48,64)) for r in (308,314)]
        rows.append(f"<tr><th>{html.escape(label)}</th><td>{cells[0]}</td><td>{cells[1]}</td></tr>")
    (out/"index.html").write_text("""<!doctype html>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ravedio chat portrait comparison</title>
<style>
body{font:15px system-ui;background:#141c2a;color:#f1f4fa;margin:20px}
body.light{background:#e8edf5;color:#161f30} table{border-collapse:collapse}
th{text-align:left;font-weight:500}th,td{padding:8px;border-bottom:1px solid #7c8896}
img{display:inline-block;border-radius:50%;vertical-align:middle;margin:2px}
@media(max-width:500px){body{margin:8px;font-size:13px}th,td{padding:5px}img{display:block;margin:3px auto}}
</style>
<h1>Chat portraits</h1><p>15° on Cool white. Each image is shown at 48 or 64 CSS pixels.</p>
<label>Skin <select id="skin">""" + options + """</select></label>
<label><input type="checkbox" id="theme"> Light chat</label>
<table><thead><tr><th>Look</th><th>308</th><th>314</th></tr></thead><tbody>""" +
        "".join(rows) + """</tbody></table>
<script>
const skin = document.getElementById("skin");
const theme = document.getElementById("theme");
skin.onchange=()=>document.querySelectorAll("img").forEach(img=>{
  img.src="references/r"+img.dataset.revision+"-"+img.dataset.case+"-skin"+skin.value+"/cool-"+img.width+".png";
});
theme.onchange=()=>document.body.classList.toggle("light",theme.checked);
</script>""",encoding="utf8")


if __name__=="__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("generated","approved","out","tools"):
        parser.add_argument(name,type=Path)
    a = parser.parse_args()
    package(a.generated,a.approved,a.out,a.tools)
