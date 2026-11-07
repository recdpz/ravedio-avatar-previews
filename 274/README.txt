Ravedio 274 | Triangular scarf fit

Ponytail and Space Buns use the same triangular crown cut, paisley fabric,
and rear knot as the other feminine bandanas. The ponytail sits lower and
slightly off center so the original tail and elastic clear the cloth. For
Space Buns, narrower side edges leave room for the full buns to sit farther
apart. The fitted placements are selected only with the bandana.

Both hair colors share the same fit. The exported updos retain their shape,
and the crown geometry and normals are identical to the original hair.
Geometry checks confirm that the fitted updos still join the hair at the
scalp and clear both the scarf and the knot. The other 14 bandana fits reuse
the prior files.

Verification
The browser audit loaded all 16 bandana combinations across eight angles,
checked Default and Ombre selection and Sprout placement, and compared nine
bare, cap, and pashmina configurations against 273. Cloth inspection and
bandana color selection passed at mobile width. The two revised looks are
shown in verification/bandana-review.jpg and verification/scarf-angles.jpg.

Reproduce
Prepare the 270 generated asset cache. From the repository root, run
274/tools/fit_updos.py and 274/tools/verify_assets.py with Blender 5.2 in
background mode. Run 274/tools/review.cjs with the local preview server
available and CAPTURE_DIR set.
