Ravedio 270 | Full catalogue at the selected proportions

Both builds use the approved spherical head at 0.8 scale and height -8%
of the original 0.96 head height. The radius is 0.384 and the common center
is (0, 1.8032, -0.015).

Scope and fits
All 16 hairstyles, seven headwear options, seven glasses styles, four eye
shapes, facial hair, Sprout, HOT sticker, and the 263 wardrobe are selectable.
The existing per-hair covered fits, per-top pashmina and braid-length fits,
and pants-fitted bases are used by the viewer. Original 263 tops and bottoms
remain direct dependencies. 81 fitted component paths reuse exact 269 exports.
The other fitted paths use ordinary GLBs. Node transforms, materials, UVs,
indices and vertex alpha are verified against the sources. Only the head is
changed in the base GLBs.

Cloth at the lower chest stays anchored on pashmina and braid fits, with a
localized front adjustment for the masculine button-up. The Taper and Curly
Top bandanas lift gently across the front to close the scalp strip while
retaining the rear tie. All 143 Ombré files have the same positions and normals
as their corresponding selected styles.

Local preview
http://127.0.0.1:9251/270/
The assets manifest points to the selected fitted file and SHA-256 per
catalogue source. Generated GLBs are a build cache. They occupy about 1.6 GB
and are excluded from Git. The local Windows copy uses a junction to
D:/Ravedio-Avatar-Work/catalogue270. On another checkout, run the bake
with the default output directory and serve the artwork repository root.

Review
128 hairstyle/headwear combinations checked from front, left, right and
rear. 112 pashmina outfit fits checked at three-quarter and from the side.
Checks also cover all seven glasses styles on each build, 16 Ombré portraits,
covered Ombré switching, and shorts-to-pants selection at mobile width.
The asset validator checks bounds, head radius, original protected data,
color pose identity, and pashmina vertex clearance. Verification data and
contact sheets are in verification/.

Phone appearance handoff
The local Ravedio270-phone ZIP contains two selected looks using the new
fits, with their separate GLBs, packed Blender scenes and 12 paired color
and linear depth renders at 48, 64 and 512 pixels. Its content manifest and
receipt are in verification/. See PHONE-CHECK.md for staging and evidence
to capture in the Development labs. Physical device comparison is pending.

Rebuild
Run tools/bake_catalogue.py with Python and NumPy.
Run tools/verify_assets.py to verify the generated catalogue.
Run tools/review.cjs with Playwright and CAPTURE_DIR. CHROMIUM_PATH and
PREVIEW_ORIGIN are optional.
Run Blender 5.2 with --background --python tools/phone_fixtures.py -- OUTPUT
to build the selected phone archive in a fresh output directory.
