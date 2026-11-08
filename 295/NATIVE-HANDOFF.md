# Revision 295 native rendering handoff

Use these two fixtures in the Development avatar labs on iOS and Android.

| Fixture ID | Build and selection | What to compare |
| --- | --- | --- |
| r295-curls-pashmina | Feminine, Curls, pashmina, button-up, pants, soft hooded eyes and lashes, clear Reading glasses, HOT | Lower hood overlap, visible eyes through the lenses, cloth texture, hair exits |
| r295-flow-cap | Masculine, Flow, cap, hoodie, pants, rounded bean eyes, short beard, dark Wayfarer glasses, HOT | Rear cap strap, dark lenses and readable smile and beard |

Each fixture includes its ordinary GLB components in the same coordinates, a
packed Blender scene, and front color and linear depth pairs for Fair and Brown
skin at 48, 64, 120 and 512 pixels. The side and back fit references use 512 px.
The manifest pins the light rigs, environment,
camera, material extensions, triangle counts, material counts, texture sizes and
file hashes. The browser checks use the same selected fits and framing. Use the
manifest appearance overrides when loading the standalone source components.

## Staging for iOS and Android

1. Transfer the ZIP and its SHA-256 receipt. Extract it to a new revision folder
   and run python verify_archive.py <path-to-zip> with Python 3. Keep the existing
   native lab fixtures available as controls. The Development labs are on
   mobile branch codex/native-avatar-render-proof. Their staging and device
   commands are documented in docs/handoffs/native-avatar-lab.md and the
   tools/avatar-proof/prepare_native.py script on that branch.
2. Adapt the lab resource manifest to the two fixture IDs and component slots
   in this package. Keep lenses and frames separate. The package manifest
   describes these assets and requires a mapping into the lab's older resource
   schema. Register both fixed assemblies with the same fixtures and resource
   hashes in Swift and Kotlin. Seed the message rows by lab fixture ID. Use a
   fresh cache revision derived from the manifest, renderer and crop settings.
   The existing typed profile bytes and production profile mappings remain
   governed by their own contract.
3. Capture the 512 px native 3D view and the actual chat rows at 48/64 px. Capture
   both skin tones. Verify the hood edge, hat strap, glasses sorting, HOT,
   eyes and smile. Compare the 120 px image as an intermediate readability
   check. Use the same camera framing and appearance overrides on both platforms.
   Keep the older taper fixture for a separate fade/vertex-alpha check.
4. After visual comparison, run the existing repeat, all-unique, and burst
   workloads in actual message rows on a physical iPhone and Android phone.
   Record cold and warm misses, decoded and disk hits, visible completion
   latency, frame times, and sampled process/GPU peaks, with device, OS, app
   commit, input hashes and build mode. Run locally on connected devices.

## Materials and depth

GLBs use the shared Y-up, +Z-forward frame. Keep world transforms, vertex normals,
UVs, vertex color and alpha. Keep the geometry and skin palette for each version
together when generating new color/depth layers. The original material factors
are included in the component inventory. The Blender scenes apply the selected
black frame finish and lens sidedness from the viewer. The reference scenes
also apply the selected skin and ink colors. The ordinary GLB bytes remain the
source of geometry and material data.

The two lenses use alpha blending at opacity .075 and .84, respectively. They
have IOR 1 and zero transmission. They require correct transparent rendering
order and edge coverage. Use the full reference colors to judge transparency.
A single nearest-opaque depth sample cannot reproduce the lens blend. The EXR
stores geometric depth at the specified .5 alpha threshold. It is not a lens
layer or a refraction map.

Blender AgX, Cycles lighting, denoising, shadow/reflection transport and the
studio environment are recorded in the packed reference. GLB does not carry
that full render pipeline. Compare each renderer to the fixed reference using
the same framing. Appearance and performance on physical phones are pending.
