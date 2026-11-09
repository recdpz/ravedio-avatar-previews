Ravedio review 312
==================
Ponytail placement, crown coverage and beanie fringe refinement based on 311.

- The tie and five locks move as a rigid bundle along the head to a modest
  viewer-right position. The uncovered gather sits at X=0.082 in the
  existing glTF coordinates. The cap uses a smaller offset to stay within
  the rear opening. The beanie retains its lower exit, with a right offset.
- The uncovered scalp spot came from the open inner perimeter of the crown.
  Close that ring using its existing edge colors and normals. Redirect
  the crown flow along the sculpted strands so their hairline stays put.
  Ray samples in both finishes confirm coverage over the gather. The cap's
  covered roots also have slightly softer sheen in its rear window.
- At the beanie, move whole front-lock sections through a rounded,
  downward release. The curve starts at the cuff and returns to the
  existing lengths. There is clearance at the cuff and no shelf step.
- The bandana rear gathers, knot and sprout seating follow the offset.
  The bucket-hat tail drops just enough to clear the brim. The cowboy
  hat and ears fit the right-side pose. The pashmina's enclosed tail
  uses its dedicated existing route.

Checks
- Eight views of eight headwear options in both finishes.
- Selection and geometry checks on all 16 hair/hat pairs and 128
  outfit combinations covering eight tops with the sprout. Verify the
  moved tails meet their crowns and clear headwear and wardrobe parts.
- fit.json records the fitting angles, coverage and GLB hashes.
  checks.json records the resolved selection audit.

Reproduce
- Run tools/review.cjs with 311 to capture the input selection receipt.
  Set CAPTURE_DIR and, if needed, PLAYWRIGHT_MODULE and CHROMIUM_PATH.
- Run tools/build.py in Blender 5.2 with parts-311.json after --.
- Capture 312 with tools/review.cjs. Run tools/verify.py in Blender with
  parts-311.json, parts-312.json, wardrobe-311.json and wardrobe-312.json
  after --. Assemble the boards with tools/compare_sheets.py.
