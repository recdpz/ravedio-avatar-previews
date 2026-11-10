# 321 Rounded Bean

Rounded Bean uses the approved 222° orientation on both builds. The two eye GLBs include the refit catchlights. The feminine build also uses the matched lash GLB.

Run `tools/package.py BASE320 OUTPUT321` with Python 3.11 or newer and mount OUTPUT321 at `321/files`. The package validates the three approved GLB hashes and carries forward the fit rows and the other eye choices from 320.

## Mobile art review

After packaging 321, run `tools/render-handoff.py` in Blender 5.2 with BASE320, OUTPUT321, the mobile avatar-proof tools directory, and the handoff output directory after `--`. BASE320 includes the packed scenes from the 320 reference render. Run `tools/finish-handoff.py HANDOFF MOBILE_TOOLS OUTPUT_ZIP ART_COMMIT` with Python, Pillow, and NumPy to verify the paired renders and generate the ZIP. Use the commit that introduced the approved 321 GLBs as ART_COMMIT. See [the review guide](MOBILE-REVIEW.md) for the device comparison.
