Ravedio 305 | Twin Braids and Ponytail with beanie

Twin Braids use a gradual shoulder curve and settle against the
selected top. With the pashmina, each plait turns around the lower
front edge and follows the chest below the scarf. Both fits keep the
woven plaits, cuffs, and roots. Each top has an authored length fit.

The beanie uses the same five locks and tie as the uncovered ponytail.
The bundle moves to the lower cuff in a single rigid pose. The fitted
crown and front wisps carry forward from 304. Both Original Brown and
Ombré retain their color treatment.

Revision 304 Box Braids and the uncovered Ponytail Ombré carry forward.
The preview retains the existing selectors and shared coordinates.

Review covers 104 selector combinations, including 44 unchanged Box
Braids selections, 32 Twin Braids exports, and four Ponytail exports.
Front braid triangles cleared all eight tops and the pashmina in both
finishes. Some upper braid triangles still seat into the head near the
root. See verification/fit.json for contact counts and rigid fit error.
The matching browser renders are in verification/twins.jpg and
verification/beanie.jpg.

Rebuild with revision 304 and its assets available. Serve the preview
root. Set ART_REVISION=304 and run node 305/tools/resolve.cjs before.json.
Run Blender in background mode with 305/tools/build.py, passing
before.json after --. Set ART_REVISION=305 and run the resolver to
produce after.json. Run Blender with 305/tools/check.py, passing both
receipts after --. Set CAPTURE_DIR and run review-twins.cjs and
review-beanie.cjs to reproduce the browser captures. Generated GLBs
are in 305/assets.
