Ravedio 269 | Selected head proportions

Owner selection
Both builds use the spherical head at 0.8 scale and -8% of its original 0.96
height. The common center moves from (0, 1.88, -0.015) to (0, 1.8032, -0.015).
The head has radius 0.384. It slightly overlaps the top of the torso by design
for a subtle float in the silhouette. There is no visible seam in the reviewed
hoodie and pashmina looks.

Scope
This bakes the fitted 268 subset: six hairstyles across the two builds, four
eye shapes and skin tones, masculine facial hair, both lens and frame styles,
and authored cap and pashmina fits. Existing tops and bottoms are referenced
from their original paths. All 83 new GLBs use ordinary glTF data and shared
coordinates. Head attachments remain independently selectable and recolorable.
Body, arms, pants legs, materials, topology, UVs and vertex color/alpha are
preserved. Original 266 and adjustable 268 are previous checkpoints.

Uncovered Straight and Curls keep their lower horizontal width. Pashmina
and its covered Straight/Curls use the same lower anchor as 268. The three
masculine button-up scarf variants also have a localized front drape adjustment
to keep the two ends visible over the shirt. Other pashmina variants keep
their existing chest and shoulder anchors.

Review
The local viewer at http://127.0.0.1:9251/269/ compares the original sphere with
the selected baked geometry in the same studio. Side-by-side output includes
front, both profiles, three-quarter, rear-quarter, rear, top and underneath.
The 36 same-camera close-ups of baked geometry vs 268 at the selected size
and height averaged less than 0.007 difference per 8-bit channel in every
image. The browser check also exercised 24 alternate scarf/top combinations,
48/64px portraits across all four skin tones and both builds, and shorts to
pants switching. The deliberate button-up scarf fix has a separate before/after
sheet in verification/.

Reference delivery
references/ contains two packed studio scenes and ten paired color and
32-bit linear depth renders. Feminine uses Straight, hoodie, pashmina and
Reading glasses. Masculine uses Taper, short beard, hoodie, cap and Rectangular
glasses. Front references use light and deep tones at 120px and 512px. Side
references use light medium at 512px. The pair receipts pin inputs, camera,
color management and both output hashes. Lens alpha is a separate compositing
concern; the depth pass describes geometric ordering at its stated alpha
threshold. These are artwork references for comparison in the native labs.
Other 263 styles and accessories still need a fit pass before they can use 269.

Reproduce
Run tools/bake_assets.py with Python and NumPy. Run tools/render_references.py
with Blender 5.2 from this checkout to regenerate the packed scenes and render
each color/depth pair together. Run tools/verify_delivery.py to check exact
protected geometry and paired outputs. To capture browser comparisons, use
tools/review.cjs with Playwright, CAPTURE_DIR, and optional CHROMIUM_PATH
and PREVIEW_ORIGIN. The local server must serve the artwork repo root.
