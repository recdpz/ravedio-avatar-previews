# Feminine Lob

Revision 327 replaces the feminine Bob geometry with a collarbone-length
lob. The lower sections bend toward the jaw before turning outward. Shorter
layers at the back keep the length off the shoulders. The pashmina fit routes
the front ends inside the opening.

The existing catalogue ID is `bob`. The viewer and source catalogue display
`Lob`. There are eight updated GLBs across the default and ombré finishes,
bound to all 128 fitted rows for this style.

Run `tools/build_lob.py` in Blender 5.2.0 with BASE322 and OUTPUT327 after
`--`. Run `tools/verify_lob.py` with the same arguments to check the crown,
scalp, and intersections against the fitted clothing and headwear. Run
`tools/render_lob.py` with BASE322, OUTPUT327, the packed 321 studio directory,
and mobile's avatar-proof tools directory. Then use
`tools/package_lob.py BASE322 OUTPUT327` with Pillow.

Mount OUTPUT327 at `327/files`. It contains the resolved catalogue, the
packed editable Lob scene, the comparison renders and a ZIP update for an
extracted revision 322 full catalogue.
