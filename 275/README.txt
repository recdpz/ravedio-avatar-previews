Ravedio 275 | Space Buns and Wispy Bangs

Space Buns is now half-up. The existing compact buns and upper crown use
their original placements, while the lower back hair falls to the upper
back in relaxed waves. Wispy Bangs replaces Side Sweep in the same
selector slot with a shoulder-length shape and a thin, irregular fringe.

The triangular bandana and rear knot keep their existing silhouettes.
Closed hats retain their covered bun placements and naturally obscure most
of the fringe. The pashmina tucks the length under the hood and shows the
fringe inside its opening. Each fit is a separate plain GLB in the common
avatar coordinates. Color changes preserve the fitted geometry. Ombré on
Space Buns extends the existing color ramp down the new loose section.

Review
The first pass identified scalp exposure under both crowns. Later passes
closed that transition, removed a rear seam, refined the fringe roots
and kept the pashmina clear of the lower tips. The browser checks both
styles without headwear and with all seven headwear choices from eight
angles. It also checks Ombré, a 120-pixel portrait with clear reading
glasses, mobile selection, and unrelated assemblies against 274.

The export checks compare both color meshes and verify exact positions
and normals on the protected Space Buns crown. All eight pashmina top
variants are tested for surface intersections for both styles. See
verification/ for the angle sheets and validation receipts.

Reproduce
Prepare the 270 generated cache and 274 bandana fits. From the artwork
root, run 275/tools/build_hair.py and 275/tools/verify_assets.py using
Blender 5.2 in background mode. Run 275/tools/review.cjs with Playwright,
the local artwork server, and CAPTURE_DIR set.
