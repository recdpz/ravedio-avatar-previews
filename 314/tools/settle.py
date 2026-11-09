"""Keep the original side of the gather with a small shift toward center."""
from pathlib import Path
import sys

REV = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(REV.parent/"312/tools"))
from build import main, read

# X is screen right in the front view. Closed-brim fits started centered.
TARGET_X = {"none":-.069,"ears":-.069,"beanie":-.144,"cap":-.016,"headband":-.049,
            "bucket":0.,"cowboy":0.}

if __name__=="__main__":
    main(read(Path(sys.argv[-1])),revision=REV,targets=TARGET_X)
