# Feminine Bob

Revision 330 starts from revision 329 and reshapes the side and rear locks.
The longer face-framing lock curves out at the cheek and turns back near
the jaw. Shorter locks over longer ones give the nape visible layers.
The part, coverage mesh, material finish and pashmina fit remain at 329.

Run `tools/sculpt_bob.py` in Blender 5.2.0 with BASE329 and OUTPUT330 after
`--`. Run `../327/tools/verify_lob.py` with the same arguments to verify
scalp and clothing clearance. Run `../327/tools/render_lob.py` with BASE329,
OUTPUT330, the packed 321 studio directory, and the mobile avatar-proof
tools directory. Run `../327/tools/package_lob.py BASE329 OUTPUT330` with
Pillow. Mount OUTPUT330 at `330/files` for the rotatable preview, Blender
scene and source update.
