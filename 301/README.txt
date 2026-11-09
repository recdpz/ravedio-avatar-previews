Ravedio 301 | Color consistency

Original and Brown use the same shared chestnut pigment on both builds.
Earlier fits used different baked browns. Space Buns, Twin Braids and Box
Braids used a darker brown. Ponytail used a lighter, warmer brown, and
some covered Ponytail fits combined both. Taper also used two browns
between its swept locks and fade. The shared base is linear RGB
(0.160, 0.059, 0.030), approximately #6F4530 in sRGB before lighting.

Sculpted locks retain restrained shading. Ponytail's rooted texture stays
in the existing vertex colors. GLB replacement changes only material
pigment and its matching metadata. Geometry, opacity, UVs, hair ties,
braid cuffs and Ombré files are carried forward from 300. Beard pigment
uses a darker shade of the selected hair color. Original stubble keeps
its separate skin-specific readability adjustment.

Explicit wardrobe colors now use the requested swatch. Original
continues to use the authored garment and headwear palettes. Hoodie
cavities and facings take a shaded version of the garment tint. Bandana
and pashmina recoloring preserves the print and small weave variations.
Cowboy leather and headwear stitching retain contrasting trim.

Build and review locally from a complete revision 300 catalogue.
1. Serve the catalogue root and make Playwright available to Node.
   Set ART_REVISION=300 and run node 301/tools/resolve.cjs <before.json>.
2. Run python 301/tools/bake.py <before.json> to generate the ordinary
   GLBs under 301/assets and their path map. To store them off the preview
   drive, make 301/assets a directory junction before running the bake.
3. Set ART_REVISION=301 and run node 301/tools/resolve.cjs <after.json>.
   Run python 301/tools/check.py <before.json> <after.json>.
4. Set CAPTURE_DIR and run node 301/tools/review.cjs. The review checks
   the browser palette selectors and saves matched 300 and 301 views.

Set PREVIEW_ORIGIN for a catalogue root other than http://127.0.0.1:9251.
For check.py, pass that same origin as the optional third argument.
The native packages from earlier revisions contain their previous colors.
