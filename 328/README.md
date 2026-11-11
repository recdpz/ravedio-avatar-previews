# Feminine Bob

Revision 328 uses the original jaw-length Bob from revision 322. It reshapes
the part and the lower sweep, staggers the ends and keeps the rear contour
close to the nape. Closed hats retain their fitted crown. The pashmina uses
the same covered hair placement with a slight adjustment to the exposed ends.

The catalogue ID and label are Bob. The eight revised GLBs are bound to all
128 Bob fit rows across the default and ombre finishes.

Run tools/build_bob.py in Blender 5.2.0 with BASE322 and OUTPUT328 after
`--`. Run ../327/tools/verify_lob.py with the same arguments for scalp
clearance and fitted clothing and headwear checks. Run
../327/tools/render_lob.py with BASE322, OUTPUT328, the packed 321 studio
directory, and the mobile avatar-proof tools directory. Run
../327/tools/package_lob.py BASE322 OUTPUT328 with Pillow.

Mount OUTPUT328 at 328/files. The output includes the resolved catalogue,
editable Blender scene, angle comparisons and a source update ZIP for an
extracted revision 322 catalogue.
