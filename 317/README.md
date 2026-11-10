# 317 fit and framing

This revision uses the approved Aero Gloss sample light rig and source finish from 316. Both sides of the review use the Cool white plate and the same camera when framing is matched.

The beanie crown sits lower and closer at the back. The rolled cuff, original knit maps, front locks, and tail geometry are retained. The sprout clip follows the revised crown. The fit pass checks both baked hair finishes against the visible knit surface and compares ponytail contacts to the original. Taller swept hair gets a smaller drop. Curly Top retains its crown height above the highest curl and loses some bulk at the back.

The shorter mustache has a curved center and rounded tapered ends. Its depth follows the face, and the existing smile stays in place. The shared change covers Mustache, Patch, Goatee, Short Beard, and Long Beard. Short Beard keeps its existing sideburn fade. Short and Long Beard each gain a small opacity transition along the mouth corners. Long Beard keeps its opaque body and original cheek contour.

The 15° profile crop uses a 1.36 orthographic span at height 1.75, with a 1.25 span at height 1.805 for chat. These share the original top edge and show more shirt below it. The 48 and 64 px thumbnails show the original crop on the left and the more modest chat crop on the right.

## Build

The local outputs are mounted from `D:/Ravedio-Avatar-Work/native317` at `317/files`. Run `tools/refine.py` in Blender with the output directory and the 316 source directory after `--`. Run `tools/render-fit.py` with those two directories, the palette file from the verified 308 fixtures, and the mobile avatar-proof tools directory. Run `tools/compose.py OUTPUT` to validate and crop the finished renders. The generated `source.json` records 37 replacement GLBs and all the resolved review parts.
