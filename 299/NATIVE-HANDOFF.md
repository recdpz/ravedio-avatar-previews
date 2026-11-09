# Revision 299 native rendering handoff

The two Development fixtures are Curls + Pashmina + Button-up and Flow + Cap +
Hoodie. The 298 archive remains the comparison. Only the Feminine fixture's
hair and headgear GLBs change. The entire Masculine assembly remains a control.

The Feminine collar adopts the fitted headgear published in mobile commit
`d3066eec374cfa05fdba235adf66eca02332b5ed`. The lower curls now follow two
paths. The cheek locks turn forward through the face opening and fall to the
sides of the crossing. The rest turn inward around the nape and shoulders.
The crown, material inputs, and shared glTF coordinates are retained.

## Stage and compare

1. Verify the archive with `python3 verify_archive.py Ravedio299-native.zip 299`.
2. Use the assembly roles and SHA-256 values in `manifest.json`. Start from
   the native proof branch at `d3066eec374cfa05fdba235adf66eca02332b5ed`.
   The two changed components, their previous hashes, and the exact
   Development fixture mapping are also in `source-art.json`.
3. Use `portrait-20.json` for the 20° close portrait on white. Its PNGs are
   transparent and paired with geometric Z from the same render. Composite
   the white display surface after rendering. The prior front framing is
   retained as a separate comparison in `manifest.json`. The supplemental receipt also includes wider Feminine fit views from the front, both profiles, and rear.
4. Rebuild the lightweight portraits with the new asset hashes, camera,
   lighting and cache version. Check transparent lens edges and shadows,
   as well as the neck fold and hair exits. Run the same visual and workload
   checks in iOS and Android Development. The source update does not
   qualify the native renderer or change the profile bytes.

Each role remains an ordinary GLB. Frame and lens roles stay separate. The
alpha thresholds in the manifest are for geometric depth. They do not
describe light transmission through the clear lens.
