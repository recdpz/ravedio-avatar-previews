"""Build the Twin Braids drape and the beanie's original-shape Ponytail."""
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from twin import ROOT, fit
from beanie import build as beanie
from fit import local_path

REV=Path(__file__).resolve().parents[1]


def main(receipt):
    rows=json.loads(receipt.read_text(encoding="utf-8-sig"))
    fits=json.loads((ROOT/"304/hair-fits.json").read_text(encoding="utf-8").replace('"./assets/','"../304/assets/'))
    assets=REV/"assets"

    def components(hair,hat,color,top="open"):
        f=dict(hair=hair,headwear=hat,hairColor=color,top=top)
        return next(row["components"] for row in rows if all(row["features"][k]==v for k,v in f.items()))

    tops=[row["features"]["top"] for row in rows if row["features"]["hair"]=="twin-braids"
          and row["features"]["headwear"]=="none" and row["features"]["hairColor"]=="default"]
    assert len(tops)==len(set(tops))==8
    for hat in ("none","pashmina"):
        selection=fits["Feminine"]["twin-braids"]["fits"].setdefault(hat,{})
        selection["lengths"]={}
        for color in ("default","ombre"):
            source=local_path(components("twin-braids",hat,color)["hair"])
            selection[color]="../"+source.relative_to(ROOT).as_posix()
            for top in tops:
                parts=components("twin-braids",hat,color,top)
                source=local_path(parts["hairLengths"])
                support=tuple(local_path(parts[role]) for role in ("base","top","headgear") if role in parts)
                target=assets/f"twins-{hat}-{top}-{color}.glb"
                fit(source,target,hat=="pashmina",support)
                selection["lengths"].setdefault(top,{})[color]="./assets/"+target.name
        print("Twin Braids",hat,flush=True)
    colors=("default","ombre")
    plain={color:local_path(components("ponytail","none",color)["hair"]) for color in colors}
    old={color:local_path(components("ponytail","beanie",color)["hair"]) for color in colors}
    hat=local_path(components("ponytail","beanie","default")["headgear"])
    fitted,report=beanie(plain,old,hat,assets)
    entry=fits["Feminine"]["ponytail"]["fits"]["beanie"]
    for color,(crown,tail) in fitted.items():
        entry[color]="./assets/"+crown.name
        for top in tops:
            entry.setdefault("lengths",{}).setdefault(top,{})[color]="./assets/"+tail.name
    fits["Feminine"]["twin-braids"]["note"]="Twin plaits settle over the shoulders and turn around the lower pashmina edge."
    (REV/"hair-fits.json").write_text(json.dumps(fits,indent=2)+"\n",encoding="utf-8")
    (REV/"verification/beanie-pose.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print("Beanie",report,flush=True)


if __name__=="__main__":
    main(Path(sys.argv[-1]))
