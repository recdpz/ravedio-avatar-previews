Ravedio 300 | Pashmina drape and rear hem

The lower hood curves into the nape and upper back. A continuous cloth
surface replaces the flat shelf and closes the open rear slot on tucked
styles. The front ends still cross high, with a rounded transition from
the hood into each end. Their depth is fitted over the selected top,
including the hoodie, jersey and button-up.

The hood uses a smoothed clearance envelope over the hair and garment.
Curls and Straight retain the locks framing the face. Short rear tips
sit under the scarf. The covered Box Braids keep their texture and cuffs,
with front lengths shifted to lie over the scarf. The longer rear braid
ends emerge at the hem. Twin Braids continue down the front. Ponytail
stays tucked with no exposed rear cutout. Bob has a small covered fit.

Review the Fit comparison and Hairstyle fit views from the preview.
Some comparison images hide hair to expose the cloth. The Blender
reference shows the Curls fixture under the existing studio lights.
See verification/geometry.json for the per-combination contact check.
It measures triangle contacts in the lower cloth region, including
contacts that may be hidden by the layers.

The check covers 112 hairstyle and top combinations. No lower-cloth
self-crossing or contact with the base or top was detected. Four Box
Braids combinations register minor hair-to-cloth contact. Close-up
front, side and low rear review showed no visible poke-through there.

Rebuild with the complete local 299 preview and its source assets.
Serve the preview root and set PREVIEW_ORIGIN if using a port other
than 9251. Set PLAYWRIGHT_MODULE or make playwright available to Node.
Set CHROMIUM_PATH to use an installed Chromium-based browser.

1. Set ART_REVISION=299. Run node 300/tools/resolve.cjs <before.json>.
2. Run Blender with 300/tools/tailor.py, passing <before.json> after --.
3. Set ART_REVISION=300. Run node 300/tools/resolve.cjs <after.json>.
4. Run Blender with 300/tools/check.py, passing <before.json> <after.json>
   300/verification/geometry.json after --.
5. Set CAPTURE_DIR to a review folder. Run node 300/tools/capture.cjs.
   Pass a hairstyle key to capture only that style.
6. For the Blender color and depth check, set ART_REVISION=300 and point
   CAPTURE_DIR to a new folder. Run node 295/tools/capture.cjs
   --fixtures-only. Run Blender with 300/tools/review_blender.py,
   passing the fixture review.json and a new output folder after --.

Use blender -b --python-exit-code 1 --python <script> -- <arguments>
for the Blender commands. The generated local GLBs are in 300/assets.
