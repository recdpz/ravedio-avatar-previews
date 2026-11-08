Ravedio 295 | Pashmina fit and native artwork handoff

The lower hair is routed beneath the pashmina edge for Curls, Straight,
and Box Braids. The original scarf and top assets are reused. Hair
height, tips below y=1.365, UVs, indices and color data are protected.
The visible side and rear hems were checked in matched renders. The
sweater, tank and button-up received close views alongside the other
tops. Across the three updated cuts, both color variants show lower
hood contact counts and no increased contact with the eight tops.
The remaining inner contact reflects the layered hair and cloth fit.

The visual review covered all 16 hairstyles in pashmina, with 60
hair-and-top assemblies at eight angles. An additional selector pass
resolved the same 60 assemblies in Ombré. The revised geometry is
limited to the six covered GLBs for the three corrected hairstyles.

The separate phone ZIP contains Curls with pashmina and clear Reading
glasses, and Flow with cap and dark Wayfarer glasses. It includes two
packed Blender scenes, 22 independent GLBs and 20 matched color and
depth pairs. See NATIVE-HANDOFF.md, verification/native-manifest.json
and verification/native-archive.json. The ZIP is generated locally
under handoff/. The rendering comparison on physical phones is pending.

Rebuild from the art repo root with the local 270 asset cache and
preview server. Use Node, Playwright and Blender 5.2.

1. Set ART_REVISION=294 and CAPTURE_DIR to a new baseline folder. Run
   node 295/tools/capture.cjs
2. Rebuild from the baseline receipt.
   blender -b --python-exit-code 1 --python 295/tools/fit_pashmina.py -- <baseline/review.json>
3. Repeat the capture with ART_REVISION=295 and a new output folder.
   blender -b --python-exit-code 1 --python 295/tools/verify_fit.py -- <baseline/review.json> <updated/review.json>
4. Create the native ZIP in a fresh output path under handoff/.
   blender -b --python-exit-code 1 --python 295/tools/pack_native.py -- <updated/review.json> 295/handoff/Ravedio295-native
   python 295/tools/verify_archive.py 295/handoff/Ravedio295-native.zip

CAPTURE_DIR may be changed independently for each run. The capture
script supports --fixtures-only for a separate handoff receipt.
