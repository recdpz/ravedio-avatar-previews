# 322 Beard smile legibility

Revision 322 gives the long beard smile a 1.48× vertical stroke and the short beard a 1.25× stroke. The smile rises by 0.0015 model units. Both fits pass an intersection check against their beard and mustache.

Run `tools/build.py` in Blender with BASE321, MOBILE_TOOLS, and OUTPUT322 after `--`. BASE321 includes the 321 source catalogue and its packed art review scene. Run `tools/finish-handoff.py HANDOFF MOBILE_TOOLS OUTPUT_ZIP ART_COMMIT` with Python, Pillow and NumPy. HANDOFF is OUTPUT322/handoff. Mount OUTPUT322 at `322/files`.

The handoff compares revisions 321 and 322 for both beard styles across four skin tones. It includes 16 paired color and depth renders, the exact component GLBs, 48 and 64 px review images, and 120 px images for the native Development chat sample. The sample presents the Blender portraits in native message rows.
