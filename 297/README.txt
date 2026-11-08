Ravedio 297 | Curls, Straight, and pashmina

Both hairstyles were edited without headwear first. Curls has rounded
turns below the crown, a curved center lock, and narrower interior
locks filling the largest rear gaps. Straight has a mostly vertical
fall below the temples with a small inward taper at the tips.

The pashmina uses those revised cuts with a light sweep behind the
shoulders on the free ends. The scalp and upper lengths match the
uncovered hair. The original scarf fabric and crossing stay in use,
with more room over the bundle and a lower rear edge. The additional
room follows the broad silhouette of the hair. Turn off Cloth in the
viewer to see the actual fitted locks.

The review covers 60 selector combinations across the two cuts, both
finishes, all existing headwear, and all eight pashmina tops. The
default finish is captured from eight angles for pashmina, both with
and without the cloth. Other hairstyles keep their 296 assets. The
iOS and Android handoff remains pinned to 295.

Rebuild from the art repo root with the local 270 cache and 294–296
preview assets. Use Node, Playwright, Blender 5.2, and Python with Pillow.

1. Set ART_REVISION=296 and CAPTURE_DIR to a baseline directory.
   node 297/tools/capture.cjs
2. Generate the local exports.
   blender -b --python-exit-code 1 --python 297/tools/sculpt.py -- <baseline/review.json>
3. Set ART_REVISION=297 and CAPTURE_DIR to a new review directory, then
   repeat the same capture.
4. Verify the exports and make the review sheets.
   blender -b --python-exit-code 1 --python 297/tools/verify.py -- <baseline/review.json> <review/review.json>
   python 297/tools/boards.py <baseline> <review> 297/verification

The ordinary GLBs are generated locally under assets/. Source and
output checksums are recorded in verification/geometry.json.
