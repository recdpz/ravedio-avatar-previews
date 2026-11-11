# Feminine Bob polish

Revision 329 starts from the approved revision 328 source assets. Seven
existing locks have a little more separation at the side and back. The
changes are confined to the ends below the cheek. The part, hairline and
covered geometry under the pashmina retain their revision 328 fit.

The Bob uses slightly broader specular highlights. Both the default and
ombre finishes use the same material settings, including the pashmina fit.

Run `tools/refine_bob.py` in Blender 5.2.0 with BASE328 and OUTPUT329 after
`--`. Run `../327/tools/verify_lob.py` with the same arguments to verify
scalp and clothing clearance. Run `../327/tools/render_lob.py` with BASE328,
OUTPUT329, the packed 321 studio directory, and the mobile avatar-proof
tools directory. Run `../327/tools/package_lob.py BASE328 OUTPUT329` with
Pillow. Mount OUTPUT329 at `329/files` to load the rotatable preview and
download the packed Blender scene and revision 328 source update.
