Ravedio 304 | Box braids and Ponytail Ombré

The bare front box braids use a gradual shoulder curve that settles
closer to the torso. Each woven braid and its cuff follow the same
path. The covered front groups turn around the lower front edge of
the pashmina. Neighboring braids stay under the side drape and emerge
below its hem. A narrow braid detail remains along the face opening.

Ponytail Ombré follows the visible length of each lock, with chestnut
near the roots, warm caramel through the tail and softer color on the
face-framing ends. The eight worn and uncovered variants share this
palette. The texture is embedded in each GLB. Positions, normals and
indices match the earlier Ombré files exactly.

Verification covers 60 browser selections, the 12 revised GLBs, and
all eight tops with and without the pashmina. The front braid check
found no intersections with the pashmina or clothing in the covered
fits. The bare-hair check still finds contacts between the outer braids
and some sleeves. See verification/fit.json for the contact counts.

Rebuild locally with revision 303 and its generated assets available.
Serve the preview root and set ART_REVISION=303. Run
node 304/tools/resolve.cjs <before.json>. Run Blender in background
mode with 304/tools/build.py, passing <before.json> after --.
Set ART_REVISION=304 and run the resolver to produce <after.json>.
Run Blender with 304/tools/check.py, passing both receipts after --.
Set CAPTURE_DIR and run the review-braids.cjs and review-pony.cjs
scripts to reproduce the angle checks. Preview GLBs are in 304/assets.
