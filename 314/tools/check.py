"""Check the slight shift and repeat the assembled 312 geometry audit."""
from pathlib import Path
import sys

REV = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(REV.parent/"312/tools"))
from verify import read, verify

RANGES = {"none":(-.074,-.064),"ears":(-.074,-.064),"beanie":(-.149,-.139),
          "cap":(-.022,-.010),"headband":(-.054,-.044),"bucket":(-.003,.003),"cowboy":(-.003,.003)}

if __name__=="__main__":
    verify(*(read(Path(p)) for p in sys.argv[-4:]),revision=REV,ranges=RANGES)
