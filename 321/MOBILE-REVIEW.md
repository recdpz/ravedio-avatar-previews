# Revision 321 mobile art review

Revision 321 uses the accepted 222° Rounded Bean eyes. Revision 320 is the comparison. Each uses the same outfit, 15° camera, and Aero Gloss lighting for its look. The framing follows the approved chat crop with the shirt visible and a Cool white plate.

- `fixtures.json` lists the four assemblies, their component hashes, camera, and reference files.
- `components/` contains the exact GLBs needed for both looks. Assets with matching hashes are shared.
- `scenes/` contains the two packed revision 321 Blender scenes.
- `references/` contains matched transparent PNG and camera-space Z EXR renders for all four tones. The depth pass uses alpha 0.5 and describes the assembled view. The Cool white portraits are available at 48, 64, and 120 px.
- `index.html` shows both looks at 48 and 64 px with a skin selector and light or dark chat background.
- `sha256.json` records the digest of every review file. Verify the ZIP against its adjacent SHA-256 sidecar before extracting.

Use Ponytail + Jersey to inspect the lash fit and Flow + Long Beard to check the eye shape with a cap. On iOS and Android, compare the 48 and 64 px portraits on each skin tone and rotate the 3D view to inspect the catchlights and lashes. Record the app build, art revision, and device for each capture.

This is a source art review pack. The existing Development lab is pinned to revision 314. A 321 run requires staging these fixtures and baking the native layers for that lab. The paired depth files here serve as reference for that comparison.
