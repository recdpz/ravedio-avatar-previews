Ravedio 273 | Triangular scarf for Ponytail and Space Buns

A broad triangular panel now covers the crown on both styles. The panel
and side ties are one continuous piece of cloth. The free triangle point
rests above the rear knot, and the ponytail point sits beside the original
tail. Space Buns uses a centered taper so both buns stay exposed. The hair
and its Ombré variant are the exact existing meshes.

Geometry checks confirm zero intersections between the exported scarf
surface and either hairstyle, and zero intersections between the entire
exported ponytail scarf assembly and the ponytail or its elastic. Each
knot gathers into the wrap. The men's bandana and the other 14 bandana
dependencies reuse the exact 272 assets.

Review
http://127.0.0.1:9251/273/
Both revised styles were reviewed from the front, sides, rear and above.
The browser audit captures eight angles across all 16 bandana looks and
checks original hair, Ombré hair, Sprout, mobile color controls, and six
sampled non-bandana assemblies. Before/after and angle sheets are in
verification/.

Reproduce
Build the 270 generated asset cache. Run Blender 5.2 with --background
--python tools/build_scarves.py. Then run tools/verify_assets.py and the
Playwright tools/review.cjs script with CAPTURE_DIR set.
