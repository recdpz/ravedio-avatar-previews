"""Check browser-resolved roles, braid clearance and the new knit surfaces."""
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parent))
import knit
from plaits import collider, contact, geometry, read_glb, tree

REV = Path(__file__).resolve().parents[1]
ROOT = REV.parent


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


@lru_cache(maxsize=80)
def meshes(path,limit=None):
    parts = []
    for _,_,pos,_,rotation,offset,faces in geometry(*read_glb(path)):
        points = pos@rotation.T+offset
        selected = faces if limit is None else faces[points[faces,1].min(1)<limit]
        if len(selected):
            parts.append(tree(points,selected))
    return parts


def collision(hair,other,limit=None):
    return sum(contact(mesh,collider(other)) for mesh in meshes(hair,limit))


def surface_breaches(hair,hat):
    scalp, shell = collider(hair),collider(hat)
    peak = 0.
    for h in [.034,.08,.13,.18,.24,.32,.42,.54,.66,.79,.91]:
        points = knit.old.cap_ring(knit.SECTORS,np.arcsin(h))
        for a,(_,y,_) in zip(knit.SECTORS,points,strict=True):
            direction = np.array([np.sin(a),0.,np.cos(a)])
            origin = [0.,y,knit.CENTER[2]]+.66*direction
            distances = [mesh.ray_cast(origin,-direction,.66)[-1] for mesh in (shell,scalp)]
            if all(d is not None for d in distances):
                peak = max(peak,distances[0]-distances[1])
    return round(float(peak),6)


def verify(before,after):
    assert before.keys()==after.keys()
    knots = {}
    for key,tones in after["hats"].items():
        assert tones.keys()=={"default","ombre"}
        for tone,parts in tones.items():
            old = before["hats"][key][tone]
            assert parts.keys()==old.keys()
            assert parts["base"]==old["base"]
            assert parts["headgear"].startswith("310/assets/")
            assert parts["extra"].startswith("310/assets/")
            is_pony = key=="Feminine/ponytail"
            assert (parts["hair"]!=old["hair"])==is_pony
            assert parts.get("hairLengths")==old.get("hairLengths") or is_pony or key=="Feminine/twin-braids"
            hat = ROOT/parts["headgear"]
            if is_pony:
                tail = ROOT/parts["hairLengths"]
                assert collision(tail,hat)==0
            peak = surface_breaches(ROOT/parts["hair"],hat)
            knots[key+"/"+tone] = peak
    stats = {}
    for key,parts in after["twins"].items():
        old = before["twins"][key]
        hat = key.split("/",1)[0]
        assert parts.keys()==old.keys()
        expected = set() if hat=="pashmina" else {"hairLengths"}
        if hat=="beanie":
            expected.add("headgear")
        assert {role for role in parts if parts[role]!=old[role]}==expected,key
        current = ROOT/parts["hairLengths"]
        previous = ROOT/old["hairLengths"]
        for other,limit in [("base",1.53),("top",None),("headgear",None)]:
            if other not in parts:
                continue
            got = collision(current,ROOT/parts[other],limit)
            old_count = collision(previous,ROOT/old[other],limit)
            assert got<=old_count or (other=="headgear" and hat=="beanie"),(key,other,got,old_count)
        stats[hat]=stats.get(hat,0)+1
    receipt = read(REV/"verification/geometry.json")
    for name,row in receipt["assets"].items():
        blob = (REV/"assets"/name).read_bytes()
        assert sha256(blob).hexdigest()==row["sha256"] and len(blob)==row["bytes"],name
    print("Highest visible cuff samples:",sorted(knots.items(),key=lambda row:-row[1])[:8],flush=True)
    return {"beanieClearanceSamples":knots,"twinBraidSelections":stats}


if __name__=="__main__":
    before,after = map(read,sys.argv[-2:])
    report = verify(before,after)
    (REV/"verification/checks.json").write_text(json.dumps(report,indent=2)+"\n",newline="\n")
    print("Checked",len(report["beanieClearanceSamples"]),"beanie finish selections and",
          sum(report["twinBraidSelections"].values()),"braid combinations",flush=True)
