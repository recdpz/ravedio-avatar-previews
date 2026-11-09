Ravedio 307 | Twin Braids and restored Box Braids

Box Braids resolves to the same assets as revision 305 for all tested
selections. The 306 comparison is retained as a historical preview.

Twin Braids now follow a smoother shoulder curve. The lower weave uses
rounded plies spaced by distance along the new path, with a gradual
taper, slightly staggered tips and smaller ties. The pashmina keeps its
separate low exit. The other hats keep their fitted crowns and share
the new lengths with the uncovered style, fitted to the selected top.

Verified 188 browser selections, including 44 restored Box Braids
selections and 128 Twin Braids fits. The 32 revised exports retain
their topology, material data and upper attachment. The new lengths
clear all eight tops, the lower body and the pashmina. The full braid
mesh still overlaps the cap, beanie, bucket hat and cowboy hat near the
existing upper attachment to the same extent. See verification/fit.json
for contact checks and hashes. Browser images cover all eight tops
with and without pashmina, plus headwear and 120 px portrait checks
in Original Brown and Ombré.

Rebuild with revision 305 and its local assets available. Serve the
preview root and run 307/tools/resolve.cjs with ART_REVISION=305 to
create before.json. Run Blender in background mode with
307/tools/braidfit.py, passing before.json after --. Run the resolver
with ART_REVISION=307 to create after.json, then run Blender with
307/tools/verify.py and both receipts after --. The comparison is in
verification/twins.jpg. Set CAPTURE_DIR and run 307/tools/review.cjs
to capture all angles. Set REVIEW_HEADWEAR=1 to add the hat and
portrait checks.
