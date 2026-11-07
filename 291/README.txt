Ravedio 291 | Long Bangs

Revision 290 is the approved bare-head reference. The selector uses
290/assets/long.glb directly for the Original finish and shows the cut
as Long Bangs in the existing Feminine side-sweep slot.

Cap, beanie, bucket hat, cowboy hat, bandana and animal ears use fitted
hair geometry in the shared avatar coordinates. The pashmina fit
keeps the fringe visible and tucks the longer layers beneath the hood.
Solid colors use the existing viewer palette. The Ombré exports bake a
chestnut-to-golden gradient into vertex colors on the same geometry.

Review
Open index.html through the local preview server. Headwear review rows
show three-quarter, left profile and back. The color sheet includes
the Original review swatch, eight palette choices and 120 px portraits.
The fitted GLBs and the Ombré versions use the same positions, normals
and indices for each headwear choice. The fit check found zero
hair/headwear and hair/top surface intersections for the checked
combinations, including all eight pashmina top variants.

The browser review covered eight angles for each Original fit, two
angles per Ombré fit, all eight tops with pashmina, and representative
combinations with the sprout and reading glasses. It also checked
changing hairstyles and toggling cloth at a 390 px viewport width.
These are full-resolution artwork exports at 207,576 triangles per
hairstyle. Native-device performance has not been measured here.

Reproduce
From the artwork repo root with the local 270 asset cache, run:
  blender -b --python-exit-code 1 --python 291/tools/build_fits.py
  blender -b --python-exit-code 1 --python 291/tools/verify_fits.py

Serve the artwork root. Set CAPTURE_DIR to a writable scratch folder.
Set PREVIEW_ORIGIN if the server differs from http://127.0.0.1:9251.
With Node and Playwright installed, run:
  node 291/tools/review.cjs

PLAYWRIGHT_MODULE and CHROMIUM_PATH can point to local installations.
With Python and Pillow installed, run:
  python 291/tools/sheets.py <CAPTURE_DIR>
