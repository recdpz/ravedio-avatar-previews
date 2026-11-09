"""Check the slight shift and repeat the assembled 312 geometry audit."""
from pathlib import Path
import sys

REV = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(REV.parent/"312/tools"))
from verify import read, verify

RANGES = {"none":(-.102,-.080),"ears":(-.102,-.080),"beanie":(-.179,-.150),
          "cap":(-.041,-.010),"headband":(-.079,-.047),"bucket":(-.003,.003),"cowboy":(-.003,.003)}

if __name__=="__main__":
    verify(*(read(Path(p)) for p in sys.argv[-4:]),revision=REV,ranges=RANGES)
