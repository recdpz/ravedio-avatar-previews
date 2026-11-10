"""Validate the rendered pairs and produce profile and chat framing assets."""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output",type=Path)
    parser.add_argument("--pilot",action="store_true")
    a=parser.parse_args()
    output=a.output
    raw=output/("pilot" if a.pilot else "raw")
    receipt=json.loads((raw/"receipt.json").read_bytes())
    manifest=json.loads((output/"source.json").read_bytes())
    expected={f"{version}-{key}-skin{skin}-{view}.png"
        for key in manifest["cases"] for version in (316,317) for skin in range(4)
        for view in (("front","side","rear") if skin==3 and key in receipt["side_cases"] else ("front",))}
    if not a.pilot:
        assert set(receipt["frames"])==expected
    target=output/("pilot-crops" if a.pilot else "review")
    target.mkdir(exist_ok=True)
    sizes=(48,64)
    count=0
    for name,digest in receipt["frames"].items():
        path=raw/name
        assert hashlib.sha256(path.read_bytes()).hexdigest()==digest
        image=Image.open(path).convert("RGBA")
        assert image.size==(640,640)
        if name.endswith("-front.png"):
            for mode,settings in receipt["crops"].items():
                crop=image.crop(tuple(settings["box"]))
                identity=name.removesuffix("-front.png")
                crop.resize((512,512),Image.Resampling.LANCZOS).save(target/f"{identity}-{mode}.png")
                if mode in ("original","chat"):
                    for size in sizes:
                        crop.resize((size,size),Image.Resampling.LANCZOS).save(target/f"{identity}-{mode}-{size}.png")
                        count+=1
        else:
            crop=image.crop(tuple(receipt["crops"]["profile"]["box"]))
            crop.resize((512,512),Image.Resampling.LANCZOS).save(target/name)
    labels=(("ponytail-beanie-jersey","Beanie · Ponytail"),
            ("flow-cap-bare-eyes","Short beard"),
            ("flow-mustache","Mustache"))
    sheet=Image.new("RGB",(906,379),"#e5edf4")
    draw=ImageDraw.Draw(sheet)
    draw.text((14,8),"317 · Beanie and facial hair fit",fill="#132a40",font=ImageFont.load_default(23))
    for i,(key,label) in enumerate(labels):
        x=13+i*299
        draw.text((x,43),label,fill="#132a40",font=ImageFont.load_default(16))
        for j,version in enumerate((316,317)):
            left=x+j*145
            draw.text((left,70),str(version),fill="#132a40",font=ImageFont.load_default(14))
            image=Image.open(target/f"{version}-{key}-skin3-profile.png")
            image=image.resize((140,140),Image.Resampling.LANCZOS)
            sheet.paste("#F1F4FA",(left,92,left+140,232))
            sheet.paste(image,(left,92),image)
            angle_file=target/f"{version}-{key}-skin3-side.png"
            if angle_file.exists():
                angle=Image.open(angle_file).resize((124,124),Image.Resampling.LANCZOS)
                sheet.paste("#F1F4FA",(left,243,left+124,367))
                sheet.paste(angle,(left,243),angle)
            else:
                thumb=Image.open(target/f"{version}-{key}-skin3-{'chat' if j else 'original'}-64.png")
                sheet.paste("#F1F4FA",(left,252,left+64,316))
                sheet.paste(thumb,(left,252),thumb)
    sheet.save(target/"comparison.jpg",quality=94,optimize=True)
    if not a.pilot:
        results={"revision":317,"baseline":316,"beanie_fits":manifest["beanies"],"groom_styles":manifest["grooms"],
                 "replacement_glbs":len(manifest["replacement_assets"]),"render_pairs":len(expected)//2,
                 "chat_crops":count,"crops":receipt["crops"],"packed_blender_scenes":receipt["scenes"]}
        (output/"verification.json").write_text(json.dumps(results,indent=2)+"\n",newline="\n")
    print("Verified",len(receipt["frames"]),"rendered frames and",count,"chat crops",flush=True)


if __name__=="__main__":
    main()
