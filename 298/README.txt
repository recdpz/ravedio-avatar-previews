Ravedio 298 | Curls, Box Braids, and Bob

Curls turns higher through the temples and crown into rounder locks.
The immediate part stays smooth so the roots join cleanly. The
outer rings move as complete sections to clear the face. Smaller
inner locks break up the larger rear gaps. Close headwear retains the
previously fitted upper roots, with the curl taking shape lower on the
exposed length. The pashmina has more room for the revised curl volume
and reduces the loft of the covered turns while keeping their length.

Box Braids sit nearer the scalp and the rear rows drop with less
outward flare. The weave, ties, and length are retained. Bob has
slightly longer face-framing locks, a softer sweep, and small changes
in length around the ends.

Browser checks cover 90 combinations across the three cuts, both
finishes, and the headwear and pashmina tops. The default finish was
captured from eight angles with no headwear and with the pashmina on
and hidden. The geometry report records the sampled temple clearance,
rear braid profile, and file checksums.

Rebuild from the art repo root with the local 270 cache and 294–297
preview assets. Use Node, Playwright, Blender 5.2, and Python with Pillow.

1. Set ART_REVISION=297 and CAPTURE_DIR to the baseline folder.
   node 298/tools/capture.cjs --all-tops
2. Generate the local exports.
   blender -b --python-exit-code 1 --python 298/tools/refine.py -- <baseline/review.json>
3. Set ART_REVISION=298 and CAPTURE_DIR to a new review folder and
   repeat the capture with --all-tops.
4. Verify the exports and create the review boards.
   blender -b --python-exit-code 1 --python 298/tools/check.py -- <baseline/review.json> <review/review.json>
   python 298/tools/boards.py <baseline> <review> 298/verification

Generated GLBs live locally under assets/. The separate iOS and Android
handoff remains pinned to 295.
