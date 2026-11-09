"""Build revision 310 from the resolved 309 hairstyle and wardrobe selections."""
from hashlib import sha256
import json
from pathlib import Path
import sys


sys.path.insert(0,str(Path(__file__).resolve().parent))
import knit
import plaits

REV = Path(__file__).resolve().parents[1]
ROOT = REV.parent
OUT = REV/"assets"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(path,data):
    path.write_text(json.dumps(data,indent=2)+"\n",encoding="utf8",newline="\n")


def asset(name):
    return "./assets/"+name.name


def build_hats(rows,art,hair_fits):
    receipt = {}
    old_hat = knit.inside(ROOT/rows["Feminine/ponytail"]["default"]["headgear"])
    pony = read(ROOT/"309/sources.json")["ponytail"]
    for key,variants in rows.items():
        build,hair = key.split("/")
        slug = build.lower()+"-"+hair
        spec = art["beanie"][build][hair]
        current = variants["default"]
        covered = ROOT/current["hair"]
        if hair=="ponytail":
            fits = {}
            for color,selection in variants.items():
                path = OUT/f"ponytail-cuff-{color}.glb"
                knit.press_fringe(ROOT/selection["hair"],path)
                fits[color] = asset(path)
            covered = REV/fits["default"]
            hair_fits["Feminine"]["ponytail"]["fits"]["beanie"].update(fits)
        widths = knit.fit_cuff(knit.inside(covered))
        hat = OUT/f"beanie-{slug}.glb"
        knit.export(hat,widths)
        fitted = knit.inside(hat)
        pin = OUT/f"beanie-sprout-{slug}.glb"
        knit.seat_sprout(ROOT/current["extra"],pin,old_hat,fitted)
        spec.update(headgear=asset(hat),sprout=asset(pin))
        receipt[key] = {"meanHemChange":round(float(widths[0].mean()),5),
                        "meanCuffChange":round(float(widths[1].mean()),5),
                        "minCuffChange":round(float(widths[:3].min()),5)}
        if hair == "ponytail":
            prior = knit.inside(ROOT/current["hairLengths"])
            if prior.overlap(fitted):
                pose,evidence = knit.old.pose_ponytail(ROOT/pony["default"]["bare"],covered,fitted)
                for color in variants:
                    temp = OUT/f".tail-{color}.glb"
                    dst = OUT/f"ponytail-beanie-{color}.glb"
                    knit.updos.write_pose(ROOT/pony[color]["bare"],temp,"ponytail",pose)
                    knit.old.isolate(temp,dst,knit.old.attachment)
                    temp.unlink()
                    spec["tail"][color] = asset(dst)
                receipt[key]["newTailPose"] = evidence
            for color in variants:
                tail = knit.inside(REV/spec["tail"][color])
                assert not tail.overlap(fitted), color
                scalp = knit.updos.surface(REV/fits[color],lambda name:"roots220" in name)
                assert tail.overlap(scalp), color
        print(key,receipt[key],flush=True)
    return receipt


def build_braids(rows,fits):
    receipt = {}
    for key,parts in rows.items():
        hat,top,color = key.split("/")
        if hat!="none":
            continue
        source = ROOT/parts["hairLengths"]
        output = OUT/f"twins-{hat}-{top}-{color}.glb"
        support = [ROOT/parts[slot] for slot in ("base","top")]
        receipt[key] = plaits.fit(source,output,*support)
        fits[hat]["lengths"][top][color] = asset(output)
        print(key,receipt[key],flush=True)
    for hat,entry in fits.items():
        if hat!="pashmina":
            entry["lengths"] = fits["none"]["lengths"]
    return receipt


def main(source):
    rows = read(source)
    art = json.loads((ROOT/"309/art.json").read_text().replace('"./assets/','"../309/assets/'))
    hair_fits = json.loads((ROOT/"307/hair-fits.json").read_text().replace('"./assets/','"../307/assets/'))
    receipt = {"hats":build_hats(rows["hats"],art,hair_fits)}
    twins = hair_fits["Feminine"]["twin-braids"]
    twins["note"] = "Twin plaits fall beside the face before turning over the shoulders."
    receipt["braids"] = build_braids(rows["twins"],twins["fits"])
    receipt["assets"] = {p.name:{"bytes":p.stat().st_size,"sha256":sha256(p.read_bytes()).hexdigest()}
                         for p in sorted(OUT.glob("*.glb"))}
    write(REV/"art.json",art)
    write(REV/"hair-fits.json",hair_fits)
    write(REV/"verification/geometry.json",receipt)


if __name__=="__main__":
    main(Path(sys.argv[-1]))
