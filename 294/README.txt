Ravedio 294 | Lower hair audit

Reviewed every hairstyle from below and both low three-quarter angles.
Each bare-head style was also inspected with the hair isolated. The
browser captured all 128 hairstyle and headwear combinations, plus 28
extra assemblies with an open shirt or hoodie. The variant checks
covered 288 selections across the original finish and Ombré.

Corrections
- Bob, Straight, and Curls. Tuck the edge of the recessed coverage
  layer at the nape. The outer locks use the original mesh data.
- Box braids. Bring the central braids closer across the lower rear gap
  and keep the rear crown part, woven relief, and ties.
- Flow with cap. Fit the layers beneath the cap around the opening and
  strap. The hair visible through the opening still follows the cut.

Use index.html for the rotatable preview and verification/changes.jpg
for matched comparisons. The two build sheets show the full catalogue
from below, in isolation, and with the pashmina.

The inspection used the existing viewer lighting. The geometry report
compares contacts with the selected garments and headwear. Existing
contact in layered fits can represent intentional tuck or coverage.
The acceptance check also uses the rendered views.

Reproduce from the artwork repo root with the existing local asset
cache and preview server. Set ART_REVISION=293 and CAPTURE_DIR to a
writable baseline folder. Run the capture script with Node and
Playwright. Rebuild using the resulting review.json.

  node 294/tools/capture.cjs
  blender -b --python-exit-code 1 --python 294/tools/repair.py -- <baseline/review.json>

Repeat the capture with ART_REVISION=294 in a different output folder.
Run the geometry and assembly checks against both receipts.

  blender -b --python-exit-code 1 --python 294/tools/verify.py -- <baseline/review.json> <updated/review.json>
