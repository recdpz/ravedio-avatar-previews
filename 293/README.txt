Ravedio 293 | Long Bangs inner ridge

Revision 292 removed the intersections between the lower locks. A step
in the inset at their roots still produced a thin line across the
underside. The inner surface now has a constant radial inset through
that join, blended into the upper surface. The outer mesh positions
and the existing headwear fit are retained.

Matched underside and low three-quarter captures show the change.
The lower-hair intersection check and headwear and top clearance checks
passed across all eight fits. The solid-color and Ombré exports use
identical geometry within each fit.

Rebuild from the artwork repo root with the local 270 asset cache.

  blender -b --python-exit-code 1 --python 293/tools/build_surface.py
  blender -b --python-exit-code 1 --python 292/tools/verify_inside.py -- 293 292

Serve the artwork root, set ART_REVISION=293, and set CAPTURE_DIR to
a writable folder. Run the browser check with Node and Playwright.

  node 291/tools/review.cjs
