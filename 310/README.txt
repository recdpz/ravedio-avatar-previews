Ravedio review 310
==================
Beanie and Twin Braids fit refinement based on 309.

Beanie
- The lower cuff is fitted separately to the silhouette under each of the
  sixteen covered hairstyles. The fit averages the hair envelope across
  fabric panels, with a continuous taper into the relaxed crown. The tighter
  hem follows short hair while making room for larger covered styles.
- The ponytail front locks tuck in slightly where the cuff crosses them.
  The bare ponytail still uses its original paths. Both worn ponytail finishes
  retain scalp attachment and have zero triangle overlap with the beanie.
- A rolled cuff and broad ribs define the main form. The small repeating knit
  loops have a packed tone map and a normal map for close-ups. Dye and grain
  are separate so the same detail works on recolored hats. The sprout clip
  keeps its separate selection and sits on the fitted crown.

Twin Braids
- Both woven plaits keep their roots, taper and ties. They hang closer to
  vertical beside the cheek, then turn forward near the shoulder and settle
  over the selected top. Eight tops have separate clearance fits in both
  hair finishes. The pashmina uses its dedicated existing braid route.

Verification
- The live viewer was captured from eight angles for every beanie fit.
  The alternate hair finish and white hat with the sprout were checked on
  all sixteen styles. Twin Braids were reviewed on eight tops and with
  each headwear option.
- checks.json records 32 sampled beanie and finish combinations and the
  clearance checks across 128 Twin Braids assemblies. At all sampled
  heights above the hem, the covered hair remained inside the outer shell.
  The braid verifier compares clothing, lower body and headwear contacts
  against 309. Contact at the beanie and braid attachment is reviewed visually.
- geometry.json records fit measurements and hashes for the ordinary GLBs.

Reproduce
1. Use tools/selections.cjs with 309 and a destination JSON file. Set
   PLAYWRIGHT_MODULE and CHROMIUM_PATH if needed. The default preview origin
   is http://127.0.0.1:9251.
2. In Blender 5.2 background mode run tools/build.py with the 309 selection
   file as the argument after --.
3. Run tools/selections.cjs with 310. Run tools/verify.py in Blender with
   both receipts after --. To rebuild the sheets, use tools/review.cjs
   with 309 and 310 and CAPTURE_DIR set, then tools/compare_sheets.py.
