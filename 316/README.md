# 316 Aero Gloss source comparison

This review covers four matched looks assembled from 314. It applies a higher clearcoat to skin, sculpted hair, frames, hardware and the sprout. Tall cool reflection strips sit on either side of the avatar. The front fill and the world are broad, and the clear lens gets a quieter reflection so the eyes are easier to see. Hair ties, woven cloth and the graphic inks keep their existing visual roles.

The preview uses one plain background per comparison, the same camera and the same skin tones for both versions. It has a 15° close-up on all four tones, four additional angles on the deepest tone, and the actual 48 and 64 px crops. The ponytail sample uses the default jersey and a fitted sprout on both sides.

The source export modifies material records and leaves every GLB binary chunk byte-identical. The assembled Blender files are editable, with packed images. The source receipt binds each component to its original 314 path and digest. The light rig is separate from the GLB materials.

The local asset directory is `D:/Ravedio-Avatar-Work/native316` and is mounted at `316/files`. Run `tools/source.py OUTPUT --source-mount WORK_ASSETS` to rebuild the GLBs. Run `tools/render.py` with Blender 5.2 after `--`, passing the verified 308 fixture directory, the 308 selector JSON, the mobile avatar-proof tools directory, and the 316 output directory. Run `tools/compose.py OUTPUT` to verify the renders and create the chat portraits.
