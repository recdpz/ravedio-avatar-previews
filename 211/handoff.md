# Ravedio artwork and rendering handoff Â· 211

This package preserves the accepted 209 baseline and finishes selected catalogue
candidates. It does not select a mobile renderer, assign profile bits, alter
native apps or change the original humanoid Studio. New catalogue candidates
await owner approval; their production intent is not an approval claim.

## Authority and exact selections

The baseline is the composite 209 artwork, not the mobile LOD or the native lab.
`baseline/manifest.json` identifies exact source hashes and four full assemblies:
both builds, Fair and Brown skin, Original eyes, Smile, no nose; feminine Bob,
Tank and Skirt; masculine Side part, Tank, Shorts and accepted 209 Stubble.
The accepted heads, skin palette, bodies, floating arms, wardrobe and fixed
lighting are retained. Original source files are never overwritten.

Each look includes its packed `.blend`, full geometry `.glb`, 120px and 512px PNG,
and exact camera/lighting/color settings JSON. Both sizes use the same camera,
orthographic scale, target and square framing. No source simplification is used.

## Reproduce offline

Use Blender 5.2.0 LTS (the saved producer version) or verify a deliberate upgrade.
All scene dependencies are packed. `reproduce.py` has no project-drive imports:

    blender -b --python reproduce.py -- baseline/Feminine-fair.blend output.png 512

The portable script uses CPU Cycles so it does not require the author's GPU.
Small sampling differences between CPU/GPU are possible; camera/material/light
settings are the same. The scene settings files record the original GPU renders.

## Catalogue work and shared coordinates

`catalogue211.json` records each fit and its exact saved scene. Uncovered hair and
cap-covered hair are distinct exports. The cap uses a real open rear arch and
separate strap; ponytail roots/tie/free lengths are treated independently.
Round frames and lenses are separately selectable. The coral HOT badge and its
geometry lettering follow the actual cheek. Taper fitting retains the selected
153 cartoon design on the current head support.

Blender is Z-up, front -Y. GLBs use standard glTF Y-up, front +Z. Components keep
the same world coordinates/transforms and require no additional centering,
normalization or per-part scale. Never place a component by its individual AABB.
Full assembled reference scenes are provided alongside component exports.

## Material and lighting portability

The original Blender reference uses Cycles, AgX / None look, exposure 0, gamma 1,
sRGB display, a constant colored world and four large disk area lights. Exact
transforms, power, color and dimensions are in the per-look JSON. The world is
procedural and self-contained; there is no missing external HDRI. Saved Blender
scenes are the complete lighting reference.

GLBs preserve standard PBR geometry/materials and the exported material
extensions. They are not a container for the complete Blender render pipeline:

- Disk area lights, floor bounce/contact shadows, Cycles ray tracing and AgX
  display conversion are not baked into these GLBs. Exported geometry excludes
  the studio floor, camera and lights deliberately; use the supplied scene recipe.
- Blender per-object ray-visibility flags do not have standard glTF parity.
  `render-requirements.json` records them. Discarding these flags may change
  colored reflections under the chin or indirect response.
- Procedural, node-based or vertex-color details must be checked against the
  exporter result. The taper uses vertex alpha; retaining that coverage is
  essential. Clearcoat and skin metallic response must not be silently removed.
- Opacity and transmission are different. Clear lenses use alpha 1 with physical
  transmission, thin closed geometry and a restrained IOR; they are not opaque
  gray disks or an alpha-painted imitation. Frames and lenses are separate.
  The native/layered path must preserve eyes behind the lenses, lens highlights
  and depth ordering. An opaque nearest-layer compositor does not qualify this.
- No native/browser match is inferred from a Blender render or a successful GLB
  load. Compare original Blender -> GLB round trip -> native 3D -> portrait.

`asset-statistics.json` lists exact triangles, draw primitives, materials,
embedded texture sizes, extensions, alpha modes, file sizes and hashes for every
GLB. The source package is not a qualified mobile asset budget. Any later reduced
derivative needs matched comparisons; originals remain intact.

## Review gates

Review construction/attachments first, then reopen the final saved scenes and
inspect fresh exported/reimported output. Include front, three-quarter, both
profiles, rear, top, necessary contact/underside views and 32/48/64/128px crops.
Inspect the combined ponytail + cap + hoodie and glasses + hair + cap cases.
Corrections reopen affected checks. `visual-review.json` records actual findings
and remaining qualifications; render counts alone do not accept artwork.

The final renderer decision and actual-app workload/minimum-phone, memory,
latency, thermal and battery qualification remain with the native work.

## Browser material compatibility

The old r128 web preview failed transmission and vertex-alpha display even though
the GLBs encoded both correctly. Review211 vendors MIT-licensed three.js r180 and
its matching GLTFLoader, with hashes/source URLs in vendor/provenance.json. The
fixed web light recipe is converted to the newer renderer's light/color scale.
No alpha-painted lens substitute or geometry modification is used. Web/browser
appearance remains separate from the authoritative Cycles/AgX references.

The asset handoff includes assembly211.json and face-palette209.json. Archive
package-files.json contains exact per-file hashes; packages211.json records ZIP
hashes and sizes. Baseline and catalogue downloads are separate to keep each
transfer bounded.

## Ponytail front correction

The owner rejected the first211 frontal hairline and front locks. They were rebuilt before publication: continuous combed coverage, a softer rounded hairline, physically blended roots and a fuller tail visible beside the face. The exposed hairstyle and covered cap variant have separate exports. No head, face, body, garment, palette or light redesign is included. The matched before/after is ponytail-front-comparison211.png. New styling still awaits owner acceptance.

The catalogue GLB ZIP contains both complete cap/glasses/HOT/hoodie fixture GLBs and independent hair/headwear/frame/lens/HOT/hoodie components. The separate catalogue-scenes ZIP contains all nine packed catalogue scenes. Unzip both into the same folder; shared files are identical. Additional full local assemblies are identified as not included in assembly211.json; they can be exported from the packed scenes. No dependencies on old drive paths are needed to render the packed scenes.

The new Ponytail root union was retopologized from its temporary voxel construction before the final source save. This changes no approved209 reference. topology-comparison211.png shows matched intermediate/final renders, and rooted-topology211.json records a closed manifold result. These are authoring checks, not native-app performance certification.
