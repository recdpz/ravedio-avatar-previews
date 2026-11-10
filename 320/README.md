# 320 chestnut hair

The shared Brown dye is `#594033` in sRGB. Original (Brown) and Brown resolve the same baked dye in both builds. The exporter covers 240 fitted hair and length paths across 1,792 catalogue rows. It scales the existing variation in solid hair materials, updates the fade dye, and fades the Ombré change out before the caramel lengths. Hair ties, geometry, and authored opacity are preserved. Stubble retains its skin-specific pigment. Short Beard uses the approved 318 fit and Long Beard uses 319. Their matched smile is indexed separately for those two grooms.

The catalogue overlays the 315 assembly index with Aero Gloss hair materials and the 317 beanie and sprout replacements. Deep skin keeps the established skin palette. The review compares the old and new dyes under the same Blender rig, including exact 48 and 64 px crops.

## Rebuild

1. Run `tools/export.py OUTPUT CATALOGUE315 SOURCE317 SOURCE318 SOURCE319` with Python, NumPy and Pillow. Point CATALOGUE315 at the 315 export's assets directory. The resulting `catalogue.json` resolves the full catalogue inside OUTPUT. Unchanged assets are hard-linked where supported.
2. Run `tools/render.py` in Blender with the working asset directory, the mobile avatar-proof tools directory, and the 308 fixture palette path after `--`. The working directory contains `native315` through the named baseline revisions and the `native320` export. Use `--case` to render one comparison.
3. Run `tools/compose.py OUTPUT` with Pillow. Mount OUTPUT as `320/files` to review. The generated `receipt.json` records the catalogue and source replacement counts.
