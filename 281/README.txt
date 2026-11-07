Ravedio 281 | Fringe silhouette study

A is a soft brow fringe with fuller coverage and small gaps in the edge.
B is an airy curtain shape with an open center and longer diagonal pieces.
Both use the same avatar, hair color, clothing, viewer lighting and camera
as the 280 comparison. The 120-pixel images use the chat portrait camera.

The rotatable study pages are bare-head looks for selecting a direction.
They load through the existing review viewer and use ordinary GLB geometry.

Reproduce
Prepare the local 270 asset cache. Run Blender 5.2 in background mode with
--python 281/tools/build_studies.py. Serve the artwork root and run
281/tools/capture.cjs with Playwright and Chromium to regenerate the images.
