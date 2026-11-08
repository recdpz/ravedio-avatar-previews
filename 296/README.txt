Ravedio 296 | Pashmina neck and hair fit

In 295, the hair followed the broad outline of the hood and hung in
a row below its edge. The lower corners also projected past the
shoulders, making the open space around the neck look unsupported.

296 brings the lower hood and face edge into the neck wrap. The back
hangs a little lower across the nape, while the fabric makes local room
at the sides where hair emerges. The fit samples the torso and top
surfaces so a thicker garment has more clearance. This is an authored
fit baked into ordinary GLBs.

Curls and Straight retain their original lock cross-sections and move
along fitted paths. Most rear locks tuck under the wrap, with a few
ends visible nearer the sides of the neck. Box Braids keep their
front length and gather at the back. Twin Braids retain space at the
two front exits. The crossed panels preserve their design and texture.

The browser review covers 16 hairstyles in pashmina and 60 hair and
top assemblies from eight angles. The same selectors were checked in
Ombré. The geometry report verifies topology, textures, attributes,
scene transforms, and the unchanged component paths outside the hair
and scarf. The two sampled side points on the Curls and Button-up
hem sit about 19% closer together. The Box Braids are still crowded
at the back edge, and some under-layer contact remains. The separate iOS
and Android handoff ZIP remains pinned to 295.

Rebuild with the art repo, the local 270 asset cache, the 295 assets,
and the local preview server. Use Node, Playwright, Blender 5.2,
and Python with Pillow for the contact sheets.

1. Set ART_REVISION=295 and CAPTURE_DIR to a new baseline folder.
   node 295/tools/capture.cjs
2. Build the local assets.
   blender -b --python-exit-code 1 --python 296/tools/drape.py -- <baseline/review.json>
3. Set ART_REVISION=296 and CAPTURE_DIR to a new review folder, then
   repeat the same Node capture.
4. Verify the GLBs and build the boards.
   blender -b --python-exit-code 1 --python 296/tools/verify.py -- <baseline/review.json> <review/review.json>
   python 296/tools/boards.py <baseline> <review> 296/verification

The generated GLBs are local preview assets. The source and output
hashes are recorded in verification/geometry.json.
