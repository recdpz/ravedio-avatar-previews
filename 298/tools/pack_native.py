"""Build the revision 298 mobile fixtures from the resolved browser selection."""
import json
import sys
import zipfile
from pathlib import Path

REV = Path(__file__).resolve().parents[1]
ROOT = REV.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from mobile_stage import write_stage
sys.path.insert(0, str(ROOT / "295/tools"))
from pack_native import local_path, pack, sha


def check_control(receipt):
    current = json.loads(receipt.read_text(encoding="utf8"))["fixtures"]
    with zipfile.ZipFile(ROOT / "295/handoff/Ravedio295-native.zip") as archive:
        prior = json.loads(archive.read("manifest.json"))["fixtures"]
    for build, previous in prior.items():
        row = current[build]
        assert row["features"] == previous["features"], build
        assert row["parts"].keys() == previous["components"].keys(), build
        changed = {slot for slot, uri in row["parts"].items()
                   if sha(local_path(uri)) != previous["components"][slot]["sha256"]}
        assert changed == ({"hair", "headgear"} if build == "Feminine" else set()), changed


if __name__ == "__main__":
    source, output = (Path(arg) for arg in sys.argv[-2:])
    check_control(source)
    pack(source, output, art_revision=298, stage_extra=write_stage)
