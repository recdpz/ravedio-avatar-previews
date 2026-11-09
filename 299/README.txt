Ravedio 299 | Hair under the pashmina

Curls and Straight separate the face-framing locks from the lower nape
bank. The front paths move slightly forward before they reach the cloth
edge, then fall on either side of the crossing. The nape bank turns under
the scarf without changing the crown or the unhooded style. Bob has a
small fit at the jaw. Box Braids keep their plies and cuffs together as
each braid rounds the scarf. Twin Braids bend around the front opening
and lie over the scarf ends where they meet the chest.

The Curls and Button-up combination uses the exact collar fit from the
published mobile checkpoint. Each other top retains its authored scarf.
Select Cloth to inspect the fitted locks in isolation. Select Headwear
None to inspect the original uncovered hair. Both hair finishes use
the same catalogue selection. The existing coloured materials are retained.

The geometry receipt counts distinct hair triangles contacting the cloth
below the temple. It is a clearance diagnostic, not a pixel comparison.
The preview was inspected from front, both profiles, rear, overhead
and underside, with the fitted cloth on and hidden. Small contacts in the
dense Box Braids remain near the underside of the hem. The artwork and
native fixture are ready for review.

Rebuild locally from 298 and its existing preview assets.

1. Set ART_REVISION=298 and CAPTURE_DIR to a new directory. Run
   node 299/tools/capture.cjs. Repeat in a second directory with --all-tops.
2. Retrieve the ordinary fitted headgear GLB from the pinned mobile handoff.
   Expected SHA-256 c1fb925b46d44243aba671716733f223de6ac57ad59c9dd22c0897f2ede09d20.
3. blender -b --python-exit-code 1 --python 299/tools/fit.py -- <fitted GLB> <open/review.json> <all-tops/review.json>
4. Repeat the browser capture at 299 with --all-tops. Capture both 298 and
   299 with --uncovered in separate directories.
5. blender -b --python-exit-code 1 --python 299/tools/check.py -- <298 all-tops/review.json> <299 all-tops/review.json> <298 uncovered/review.json> <299 uncovered/review.json> 299/verification/geometry.json

The pinned mobile component and the standalone 299 ZIP are separate
from the archived 298 handoff. See NATIVE-HANDOFF.md for the intended
native comparison. To reproduce the ZIP, set ART_REVISION=299 and run
node 295/tools/capture.cjs --fixtures-only with a new CAPTURE_DIR.
Then run Blender with 299/tools/pack_native.py and these arguments after --:
the capture review.json, the extracted 298 package's manifest.json, and a fresh
output directory. Verify with python 299/tools/verify_handoff.py <299 ZIP>.
