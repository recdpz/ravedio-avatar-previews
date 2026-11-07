"""Verify the local scarf assets and unchanged catalogue dependencies."""
import hashlib
import json
from pathlib import Path

REV = Path(__file__).resolve().parents[1]
ROOT = REV.parent

def load(path):
    return json.loads(path.read_text(encoding="utf8"))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

current = load(REV / "bandana-fits.json")
previous = load(ROOT / "272/bandana-fits.json")
components = load(ROOT / "270/assets.json")["components"]
revised = {"Feminine-ponytail", "Feminine-space-buns"}
assert current.keys() == previous.keys()
for key, fit in current.items():
    before = previous[key]
    if key in revised:
        assert fit["hair"] == before["hair"]
        assert fit["hair_sha256"] == before["hair_sha256"]
        hair = ROOT / "270" / components[fit["hair"]]["path"]
        assert sha(hair) == fit["hair_sha256"]
        assert fit["construction"] == "triangular crown scarf"
        assert fit["exported_scarf_hair_overlap_pairs"] == fit["ponytail_overlap_pairs"] == 0
        assert fit["wrap_tie_contact_pairs"] > 0
    else:
        expected = dict(before)
        for role in ("headgear", "sprout"):
            expected[role] = "../272/" + expected[role].removeprefix("./")
        assert fit == expected, key
    for role in ("headgear", "sprout"):
        assert sha(REV / fit[role]) == fit[role+"_sha256"], (key,role)
print("Verified 2 new scarf fits and 14 unchanged bandana dependencies")
