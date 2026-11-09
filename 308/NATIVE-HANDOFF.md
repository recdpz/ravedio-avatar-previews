# Ravedio 308 mobile rendering handoff

Source artwork is 308 at `7298fc4`. The packages use the current preview's
resolved components and preserve their authored coordinates, fitted variants
and material roles. Use the established Development avatar lab on both
platforms. The mobile comparison baseline is `codex/native-avatar-render-proof`
at `d3066eec374cfa05fdba235adf66eca02332b5ed`. Keep the revision 298 lab pack
and results as the historical control.

## Which archive to use

- **Ravedio308-native-fixtures.zip** contains four self-contained test
  assemblies, packed Blender scenes, matched color and linear depth, browser
  comparisons and a 64-row seed with 16 distinct looks.
- **Ravedio308-catalogue-delta.zip** contains the assets that resolve
  differently between the 298 and 308 art catalogues, including the current
  pashmina variants, ponytail and bandana fits, restored Box Braids, the
  garment-specific Twin Braids lengths, jersey and alternate print textures.
  It layers onto the baseline art catalogue. Unchanged geometry outside the
  four fixtures comes from the existing art catalogue rather than this delta.

Check the downloaded ZIP against its adjacent SHA-256 receipt and run the
included `python3 verify_mobile.py /path/to/archive.zip`. Extract into a fresh
directory. The verifier checks every file, GLB binding, fixture, and depth
pair in the archive.

## Fixed comparison assemblies

| ID | Look | Check |
| --- | --- | --- |
| `r308-curls-pashmina` | Curls, pashmina, button-up, clear Reading glasses, HOT | 298 look rerendered with the current scarf and hair fit |
| `r308-flow-cap` | Flow, cap, hoodie, short beard, dark Wayfarers, HOT | Same feature selection as the 298 masculine control |
| `r308-twin-jersey-pashmina` | Twin Braids, pashmina, original jersey | Braid path around the scarf edge, readable jersey, side and chest fit |
| `r308-ponytail-beanie-jersey` | Ombré Ponytail, beanie, white jersey | Tail/crown join, curved tail, dyed jersey and printed contrast |

## Stage and compare

1. Read `mobile-stage.json` for ordered roles, exact asset hashes, skin
   palette, camera and material settings. Add these four IDs to the
   Development fixture registry on each platform. Include `hairLengths` as
   an independent role where listed. The white jersey needs the listed
   texture overrides on the listed raw glTF material indices. Some jersey
   materials share a display name. Use the indices to bind each one.
2. Capture the rotating native profile and visible chat rows with the same
   skin and framing. Front references use all four skin tones at 48, 64, 120
   and 512 px. Use the side, rear and jersey body diagnostics for fit and
   print. Compare the Blender color and browser comparison for the same
   assembly before tuning lighting, antialiasing or rendering settings.
3. Compare cold and warm runs with the 16 distinct appearances and the
   repeated seed. Then expand using the selector delta plus the unchanged
   baseline art. Generate many genuinely different valid appearances and
   measure first-visible latency, frame times, cache hits, memory and
   thermal state in the actual iOS and Android apps. Record devices and
   exact fixture, asset and app revisions. Treat the seed as a visual and
   initial cold-load check.
4. Keep material and attachment roles independent when preparing optimized
   copies. Regenerate color and depth together for any new geometry or
   camera. Compare those derivatives against this full-quality control
   before deciding the shipping catalogue and renderer.

The artwork files use ordinary glTF with +Y up and +Z forward. Both stage
levels point to the same full-quality control. The Cycles scenes use AgX;
the browser uses the fixed ACES viewer lighting. The glasses lenses use
alpha blend and front faces with depth writes off. They use IOR 1 and
zero transmission. The EXR contains geometric Z at alpha threshold .5.
Use the color images to assess transparent lens appearance and ordering.

The selector delta keys are build, hair, headwear, top and baked hair
finish. Apply the listed role changes over the 298 art selector. Entries
for `sprout` apply only when that detail is selected. Groom replacements
are keyed separately by build and groom. Retain the dye bindings and
material distinctions in `appearance.json`. The fixture IDs and selector
labels are Development art identifiers. Product profile and wire mapping
remain a separate workstream.
