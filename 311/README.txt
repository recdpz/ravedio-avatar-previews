Ravedio review 311
==================
Ponytail front locks and elastic fit, based on 310.

Beanie front locks
- Use the uncovered sculpt for the two front locks. Match the original
  and covered meshes by their authored UVs.
- Seat the upper strand only where it would break through the fitted shell.
  The correction acts radially against the actual shell at and above the
  cuff. There is zero position change for the 9,247 exposed strand vertices
  in each finish.

Ponytail tie
- Replace the small tilted loop with a rounded elastic around the local
  cross-section of the gathered tail. Its width is 0.021 scene units.
  The surface is a warm charcoal with a soft sheen.
- Use the new tie for the bare ponytail, beanie, cap, bandana and ears in
  both hair finishes. Bucket, cowboy and pashmina use separate covered
  constructions and retain their existing parts.
- Mesh checks confirm the elastic contacts the gathered bundle and clears
  each headwear piece. The beanie tail still connects to its crown. The
  verifier checks all 16 headwear/finish selections and compares the
  revised tail assets against their original non-tie vertex positions.

Reproduce
- Run tools/review.cjs with 310 to capture its selected components. Set
  CAPTURE_DIR and, if needed, PLAYWRIGHT_MODULE and CHROMIUM_PATH.
- Run tools/build.py in Blender 5.2 with the resulting parts-310.json
  after --. Run tools/review.cjs with 311.
- Run tools/verify.py in Blender with parts-310.json and parts-311.json
  after --. Run tools/compare_sheets.py with the capture directory.
