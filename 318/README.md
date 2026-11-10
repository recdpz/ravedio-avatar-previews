# 318 connected beards

Short and Long Beard now join the mustache to the cheek hair. A small center part and a softer finish help the mustache read as hair. The cheek is shaped around each end, and the lip-facing edge has less relief. The long beard carries more volume through the join than the short beard. Both use the supplied slimmer smile as a matched component.

The source pass checks that the mustache meets the cheek hair and both clear the smile. The preview uses the 317 studio, a matched 15° comparison, and actual 48 and 64 px chat crops. The revised looks also have front, profile, and both three-quarter views on light and deep skin.

## Build

Run `tools/refine.py` in Blender with four arguments after `--`. Supply the 318 output folder, the 317 output folder, the palette from the 308 native fixtures, and the mobile avatar-proof tools folder. Run `tools/compose.py OUTPUT BASELINE` with Pillow. Mount OUTPUT as `318/files`.

`files/source.json` identifies the two groom GLBs and the paired mouth GLB and records their hashes. The packed scenes are `files/blender/short.blend` and `files/blender/long.blend`.
