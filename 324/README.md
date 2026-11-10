# Simple chat icons

Eight looks rendered from the revision 322 catalogue for a 24 px sender
icon review. Both columns use the same fitted meshes, facial features,
skin choices, 15° angle, and cool-white background. The icon uses a
slightly tighter frame and broad directional shading. The softer facial
lighting keeps the face and beard separate on deep skin, and the beanie
has a lighter knit crown above the cuff.

The comparison includes tan space buns and box braids and three deep-skin
headwear looks to check whether the silhouettes read independently of skin
tone. Fine jersey art, eyelash shapes, and braid texture are easier to
see in the enlarged view.

Run `render.py` in Blender 5.2 with `-- WORK TOOLS OUTPUT`, where WORK contains
`native321` and `native322` and TOOLS is mobile's `tools/avatar-proof`.
Run `bake.py OUTPUT TOOLS` with NumPy and Pillow to produce the 24, 48,
72, and 120 px portraits. Serve OUTPUT at `324/files` with this preview.
