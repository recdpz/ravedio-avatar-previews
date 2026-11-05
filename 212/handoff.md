# Candidate 212: torso and accessory fit

212 is an owner-requested artwork candidate based on the frozen 209/211 assembly.
Owner approval remains pending. The exact four 209 reference looks and their
portable packages remain in [211](https://recdpz.github.io/ravedio-avatar-previews/211/).
Do not replace that accepted face/stubble reference with a native derivative.

The owner clarified that the feminine chest should have **less forward
projection and a gentler downward slope**. This candidate fairs and lowers the
existing paired volumes rather than replacing them with new spherical cups.
Its waist boundary is pinned. All eight feminine tops follow the same support
displacement once; straps, details and hidden side/back panels are checked with
arms and sleeves hidden. Masculine anatomy, both heads/faces, the four skin
tones, floating 178 arms, independent sleeves, bottoms and studio lighting stay
outside the edit scope.

The Ponytail has continuous seated pulled-back roots, a rounded forehead
boundary, separately rooted framing pieces and a free backwards-S tail with
a mild lateral fall. Its uncovered and cap-covered roots are separate exports.
The free tail and tie are not shrinkwrapped to the head or deformed around a
solid cap. The cap has a real rear opening/strap, shared bill-to-crown vertices,
a downward curved visor and a restrained cotton finish.

The glasses are rounded rectangles with separate closed lens geometry. Their
curved arms have clearance over the gathered scalp. Geometry and transforms
are identical with and without the cap, verified for both builds. No eye,
face or frame placement is lowered to fit the cap. The HOT badge restores the
original flame-outline parameters, lettering, coral/ink colors and tilt from
`scripts/face_extras.py`, scaled and seated on the current cheek. It is moved
inward enough to keep the lettering clear of the face-framing lock.

## Files and reproduction

`ravedio-candidate212-scenes.zip` contains 17 saved/reopened packed Blender
scenes, a portable `reproduce.py`, settings, source hashes and verification.
It is a candidate source package, not an accepted complete catalogue or a
qualified mobile geometry budget. Sources remain unchanged in their original
locations. The GLB ZIP includes the two combined accessory fixtures and all 25 independent components. Additional assembled GLBs remain in the local authoring handoff. Individual GLBs in this directory are independently selectable;
components retain shared coordinates and transforms. Do not recenter parts by
their individual bounds. Blender is Z-up/front -Y; exported glTF is Y-up/front +Z.

    blender -b --python reproduce.py -- scenes/Feminine-ponytail.blend out.png 512

`asset-statistics.json` reports exact file hashes/sizes, triangles, primitives,
materials, embedded textures and material extensions. All GLBs are self-contained.
`visual-review.json` describes the actual review scope and qualifications.

## Rendering requirements and limits

The packed Blender scenes remain the appearance reference: original Cycles
studio, four area lights, AgX/None look, exposure 0, gamma 1 and the original
world. The interactive browser keeps its fixed prior lighting recipe; it is
not proof of Blender/native visual parity. No lighting selector is introduced.

Glass opacity and transmission are different. Lenses use alpha 1, transmission
1, IOR 1.25 and roughness 0.025 with thin closed geometry. They require glTF
transmission/IOR support and correct eyes-behind-lens ordering, rather than an
opaque or alpha-only lens approximation. Frames and lenses are separate files.
The Taper retains its existing vertex-alpha fade and relevant material data.

GLB does not carry the complete Blender render pipeline. Area-light integration,
AgX display processing, ray-traced bounce/reflections and per-object ray-visibility
flags are not guaranteed by a standard GLB import. Round-trip renders therefore
test geometry/material transfer, not exact shader or lighting parity. Preserve
source assets and compare any mobile derivative using matched framing.

All-angle and small-size checks cover this selected slice, including combined
ponytail/cap/glasses/HOT/hoodie and the masculine taper counterpart. They do not
certify every catalogue cross-product, future headbands/pashminas, native app
workloads or actual phone performance. No profile-byte, firmware, cloud or native
renderer implementation is changed by this package.
