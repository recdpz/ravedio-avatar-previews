Ravedio 292 | Long Bangs lower hair correction

The original lower thickness offset crossed neighboring faces. The side
walls of neighboring locks also shared a plane at the beginning of the
split, and some tip corners dipped below their own end. Revision 292
rebuilds the lower inside surface with an inward radial inset, separates
the side walls below the root, and keeps each row descending to its tip.
The side fall above the tips was smoothed locally. The 290 fringe and
overall length are retained.

The comparison shows the same low three-quarter camera on the assembled
avatar and an isolated underside view. The mesh check reports zero
nonadjacent triangle intersections below the lower-hair test plane
(y = 1.68) for all eight fits. The seven headwear options and all eight
tops cleared the corrected hair. Each Ombré file shares its positions,
normals and indices with its corresponding solid-color file.

Rebuild from the artwork repo root with the local 270 asset cache.
  blender -b --python-exit-code 1 --python 292/tools/build_inside.py
  blender -b --python-exit-code 1 --python 292/tools/verify_inside.py

Serve the artwork root, set ART_REVISION=292 and set CAPTURE_DIR to a
writable folder. Run the browser check with Node and Playwright.
  node 291/tools/review.cjs
