"""Generate revision 304 assets and the corresponding fit selections."""
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from braids import REV, ROOT, process
from fit import local_path
from pony import recolor


def read(revision,name):
    return json.loads((ROOT/str(revision)/name).read_text(encoding="utf-8").replace('"./assets/',f'"../{revision}/assets/'))


def write(name,data):
    (REV/name).write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")


def main(receipt):
    rows=json.loads(receipt.read_text(encoding="utf-8-sig"))
    fits=read(300,"hair-fits.json")
    family=fits["Feminine"]
    stages={}
    hashes={}
    for hair,hat_values in [("box-braids",("none","pashmina")),("ponytail",("none","cap","beanie","bucket","cowboy","headband","ears","pashmina"))]:
        for hat in hat_values:
            def part(color):
                row=next(r for r in rows if all(r["features"][k]==v for k,v in
                     {"hair":hair,"headwear":hat,"hairColor":color,"top":"open"}.items()))
                return local_path(row["components"]["hair"])
            default=part("default")
            if hair=="box-braids" and hat=="none":
                basis=default
            selection=family[hair]["fits"].setdefault(hat,{})
            for color in (("default","ombre") if hair=="box-braids" else ("ombre",)):
                target=REV/"assets"/f"{hair}-{hat}-{color}.glb"
                source=part(color)
                if hair=="box-braids":
                    process(source,target,hat=="pashmina",basis)
                else:
                    stages[hat]=recolor(source,default,target)
                selection[color]="./assets/"+target.name
                hashes[target.name]=hashlib.sha256(target.read_bytes()).hexdigest()
                print(target.name,flush=True)
            if hair=="ponytail":
                selection["default"]="../"+default.relative_to(ROOT).as_posix()
    write("hair-fits.json",fits)
    write("verification/assets.json",{"sha256":hashes,"pony_progress":stages})


if __name__=="__main__":
    main(Path(sys.argv[-1]))
