"""Restore the long beard volume below the connected mustache."""
from argparse import ArgumentParser
import importlib.util
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("fit318",ROOT/"318/tools/refine.py")
previous = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous)
fit = previous.fit


def long_beard(points):
    x,y,z = points.T
    lateral = abs(x)
    front = fit.smooth(.191,.258,z)
    rim = fit.smooth(1.537,1.598,y)
    clearance = (.003+.009*fit.smooth(.035,.092,lateral))*front*rim
    clearance *= 1-fit.smooth(.089,.120,lateral)
    cheek = .009*front*rim*fit.smooth(.095,.126,lateral)*(1-fit.smooth(.150,.199,lateral))
    # Refit the hairline while retaining the original cross-section below it.
    return previous.conform(x,y,z,x,y+cheek-clearance)


def main():
    parser = ArgumentParser(description=__doc__)
    for name in ("output","source317","baseline","palette","mobile_tools"):
        parser.add_argument(name,type=Path)
    args = parser.parse_args(sys.argv[sys.argv.index("--")+1:])
    for folder in ("assets","raw","blender"):
        (args.output/folder).mkdir(parents=True,exist_ok=True)
    source = json.loads((args.source317/"source.json").read_bytes())
    key,body = previous.CASES["long"]
    groom = args.output/"assets/groom-long.glb"
    mouth = args.output/"assets/bearded-smile.glb"
    shutil.copyfile(args.baseline/"assets"/mouth.name,mouth)
    original = Path(source["cases"][key]["parts"]["groom"]["new"])
    previous.edit(original,groom,{"shared mustache":lambda points: previous.mustache(points,True),body:long_beard},groom=True)
    mustache = fit.surface(groom,lambda name: "shared mustache" in name)
    beard = fit.surface(groom,lambda name: body in name)
    smile = fit.surface(mouth)
    assert mustache.overlap(beard)
    assert not mustache.overlap(smile)
    assert not beard.overlap(smile)
    case = {
        "source_case":"long","groom":groom.name,"groom_sha256":fit.sha(groom),
        "mouth":mouth.name,"mouth_sha256":fit.sha(mouth),
    }
    (args.output/"source.json").write_text(json.dumps({"base":318,"revision":319,"cases":{"long":case}},indent=2)+"\n")
    previous.review(args,{"long":case})


if __name__=="__main__":
    main()
