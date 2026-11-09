Ravedio review 309
==================
Art candidate for the rotating viewer and chat portrait review. Revision 308
remains the pinned phone-test reference.

Facial readability
- Both builds keep their four approved eye shapes, skin palette and regular
  smile. The primary catchlights scale by 1.43 around their own centers.
  The smile tube grows 0.0058 scene units along its normals and uses softer
  specular highlights. These changes are authored in the replacement GLBs.
- Dark lenses use 0.74 opacity instead of 0.84. Clear stays at 0.075 opacity
  with the low-glare 308 portrait settings. Lenses are thin alpha surfaces
  with no transmission or refraction.
- The Blender comparison uses the approved 15-degree yaw, 1.16 span,
  Cool white #F1F4FA and the same lower fill and garment reflection control
  as the 308 phone baseline. The extra fill raises the cheek shadows and
  makes little difference to the eyes or smile at 48 and 64 pixels.
  The additional fill is a comparison only.

Beanie
- A continuous knit shell has a softly rolled hem, subtle ribs and a
  slight rearward lean. The brim clears the eyes and follows the head
  without squeezing the hair or leaving a rigid straight line.
- All 16 hairstyles use their established covered hair; space buns sit
  under the cap. The ponytail retains its original curve and thickness.
  Its beanie-only tail and tie move as one piece to a lower point at the
  nape. The uncovered ponytail uses its original mesh and coordinates.
- The sprout remains independently selectable and its clip follows the
  knit surface. The cuff and crown remain recolorable. The cap is an
  ordinary GLB with two materials, 34,560 triangles and no texture.
- The fit solver checks crown contact and no tail-to-beanie intersection
  in both finishes. The browser review exercises 16 styles across eight
  angles, Ombre and sprout combinations, the ponytail with a hoodie, and
  48/64 px portraits for all four eyes on each build.

Reproduction
- The base artwork source paths are recorded in sources.json. Run
  tools/build.py with Blender 5.2 in background mode. geometry.json
  records the asset sizes and hashes and the selected tail pose.
- tools/review.cjs takes revision numbers (308 309) and reads the local
  preview at PREVIEW_ORIGIN. Set CAPTURE_DIR and, as needed, PLAYWRIGHT_MODULE
  and CHROMIUM_PATH. tools/boards.py assembles the review sheets.
- tools/render_portraits.py takes the packed 308 fixtures directory, the
  mobile avatar-proof tools directory and an output directory after --.
  These are visual comparisons. A native 309 adoption should bake color
  and depth together from the approved geometry and lighting and then
  repeat the iOS and Android checks.
