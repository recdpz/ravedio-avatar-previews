# Bob shapes and textures

This review starts from the selected Tucked scene in revision 331.
It provides three silhouettes and three independently selectable surface
treatments, rendered at eight angles with the same studio camera and lights.

The brushed and sculpted-channel treatments use ordinary packed normal
and roughness textures. Their UVs follow the actual cross-section rings
of each lock from root to tip. The maps are 512 x 1024 and use non-color
sampling. The geometry, texture maps and material construction are saved
in three Blender scenes. Each scene opens with its brushed material set.
The Smooth and Sculpted channels sets are retained as materials with
fake users and identified by their name suffixes.

Run tools/study_bob.py in Blender 5.2.0 with the packed revision 331 Tucked
scene and an output directory after `--`. Run
`tools/make_comparison.py OUTPUT` with Pillow to create the comparison
sheets. Mount OUTPUT at `332/files`.

These are bare-hair review scenes. The full catalogue is still revision
330. This review does not integrate the chosen silhouette into covered
headwear fits or native app assets.

Run `tools/verify_study.py` in Blender with the same base and output
arguments to check scalp clearance, non-hair geometry, packed image sizes
and the normal and roughness maps in ordinary uncompressed GLB exports.
The test exports are temporary. The review scenes remain the deliverable.
