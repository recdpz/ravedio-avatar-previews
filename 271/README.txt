Ravedio 271 | Bandana fit and finish

The folded forehead wrap and triangular crown scarf use new ordinary GLBs.
Both are fitted over the exact uncovered 270 hair meshes. The garment surface
bridges individual curls, locs and braids without pressing them into a new shape.
Twin-braid lengths, palette controls and the approved 20% smaller, -8 head
proportions are retained.

The print is a new antialiased paisley design with woven border details.
The folded band uses a 4096 by 256 atlas. The triangular scarf uses a
1024 by 1024 atlas. The two layouts follow the fabric in their respective UVs.
The browser applies texture filtering at grazing angles. Recoloring uses
the existing headwear palette.

The scarf's ponytail edge is cut to clear the original tie and tail, and
the knot closes low on the other side. Space buns remain exposed on either
side of the scarf. Box braids retain their original volume and scalp rows.
Rear gathers intersect the actual wrap and continue into two supported cloth
ends. Optional Sprout clips were reseated for each new bandana.

Review
http://127.0.0.1:9251/271/
The viewer compares cloth-on and cloth-off with the Cloth checkbox. 270
remains available as a visual comparison. Verification includes all 16 looks
in six browser views, exact default and Ombré hair paths, palette and cloth
controls at mobile width, and sampled non-bandana combinations. The outer
wrap surfaces clear the hair in all 16 fits. The entire exported ponytail
scarf, including the knot and ends, clears the ponytail and its tie.
The exported cloth and tie overlap intentionally at their join.

Rebuild
Run tools/prints.py with Pillow. Build the 270 generated asset cache, then run
Blender 5.2 with --background --python tools/build_bandanas.py. Run
tools/verify_assets.py with NumPy and tools/review.cjs with Playwright.
The 270 phone fixture archive remains a reference for that earlier artwork.
