Ravedio 277 | Wispy fringe with an outward arc

The wisps now follow individual curved paths in three dimensions. Each
lifts away from the forehead, crests, then turns back close to the skin.
The roots join a softer, irregular crown edge. The visible ends are thin,
rounded, and staggered. Closed hats use a shallower lift under their rims.
The Space Buns entries reuse the exact 276 exports.

Review
The first render pass showed a good outward curve and overly regular
spacing. Later passes staggered the ends and softened the root edge.
Eight-angle browser checks cover every headwear choice. The exported
Default and Ombre poses match, and pashmina clearance passes for all
eight top variants. The bare-fringe check measures the return depth
and tip clearance on all nine exported wisps.

Reproduce
Prepare the 270 generated cache and 274 and 276 assets. Run Blender 5.2
in background mode with --python 277/tools/refine_fringe.py. Run
275/tools/verify_assets.py -- 277 and 277/tools/verify_fringe.py with
Blender. Run 275/tools/review.cjs with REVIEW_REVISION=277 and
CAPTURE_DIR set while the local artwork server is available.
