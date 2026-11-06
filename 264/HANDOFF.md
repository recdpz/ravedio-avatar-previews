# Ravedio rendering handoff · 264

This is the completed two-assembly artwork optimization slice. It is ready for native appearance comparison, **not a production renderer approval or a new catalogue**. No GitHub Actions, hosted deployment, mobile/firmware changes, or profile-byte changes were made for this slice.

## Reference and selection

Use 263 as the source of these fixtures. The owner accepted the 263 pants/selector correction with “good” and authorized this optimization next. That acceptance does not certify every historical catalogue feature. Source artwork is preserved byte-for-byte from art commit `0ebb080360831c50186f778315ecde054865882e`, delivered at `dc2d174e5342e6683f727354e4e5711fe2116f3f` in `recdpz/ravedio-avatar-previews`.

Both fixtures use Hoodie, Pants, Cap, HOT sticker, Original eyes, no nose and regular smile. Feminine uses the selected cap-fit Ponytail, eyelashes and clear Reading glasses. Masculine uses the cap-fit Taper and dark Rectangular glasses. Frames are black. Skin indices 0 and 3 provide the four reference looks; all four source skin colors remain selectable. No new hairstyles or accessory designs were introduced here.

The package contains:

- `sources/`: unchanged 263 assembled GLBs and packed Blender scenes.
- `assets/`: final pass-two optimized GLBs and packed re-imported Blender scenes.
- `components/` and `components.json`: 21 independent semantic component GLBs in the same world coordinates. Frames and lenses are separate; base, hair, clothing, cap, eyes, smile, lashes and HOT remain addressable. Sleeve nodes remain distinct within the top.
- `references/`: packed artwork → source GLB re-import → optimized GLB re-import comparisons, 120/512px portraits, eight diagnostic angles, and optimized 32/48/64/120px chat crops. Color and 32-bit linear Z are regenerated together.
- `layers/`: context-lit diagnostic component-group color/Z pairs at 120 and 512px, both builds and light/dark tones. Body/eyes/mouth/lashes form one fixed-fixture layer; other groups remain separate. These are input examples for the existing portrait baker, not a general compositing implementation.
- `studio.json`, `palette.json`, `colors.json`: exact packed-scene lighting, camera, color management and palette inputs. Every reference/layer receipt records its own camera and source geometry hash.
- `verification/`: mesh, component, depth, fit, pixel comparisons and visual contact sheets. `manifest.json` pins every delivered file.

## Optimization and protected features

Pinned meshoptimizer code uses attribute-aware simplification, absolute error controls and locked borders. It selects original vertex positions and retains the surviving UVs, normals and vertex colors exactly. There is no rescaling, centering, compression, quantization, node merging, material merging, hidden-surface removal or component deletion. Eyes, smile, lashes, HOT, glasses/lenses and small attachment details are protected. Uniform triangle sizes are not an objective.

| Fixture | Source triangles | Final triangles | Source GLB bytes | Final GLB bytes | Mesh nodes / primitives / materials |
|---|---:|---:|---:|---:|---:|
| Feminine | 831,762 | 228,164 | 18,191,004 | 4,907,744 | 70 / 79 / 36 |
| Masculine | 1,016,178 | 306,934 | 23,929,556 | 7,857,320 | 55 / 63 / 32 |

The tighter second pass was retained for close-up shading fidelity. The 50–100k discussion was not treated as an acceptance threshold. Draw-call-producing primitives and material counts did **not** decrease. Actual draw calls can exceed primitive count because of depth, transparency and additional engine passes. Smaller files/geometry do not establish native RAM or latency improvements, nor reduce the dimensions of baked portraits.

All scene nodes, transforms and material JSON match the source. Geometric boundary edges match after joining coincident glTF shading-seam vertices. Every surviving complete vertex attribute tuple exists in the source. All four fitted leg meshes are closed, and 9,326 radial samples pass pants/leg clearance checks. Extracted components reassemble with exact attributes and transforms. Source and derivative retain the same texture payloads; these two fixtures have no embedded image textures. See `verification/assets.json` for decoded attribute byte counts and their limitations.

## Cameras, materials and optics

Blender uses right-handed Z-up/front −Y; exported glTF uses Y-up/front +Z. The standard glTF conversion is the only axis conversion. Do not independently fit, center or resize components. Keep the cap-fit hair/headgear combination together; hiding the cap is an inspection operation, not an approved uncovered hairstyle. These bases contain the263 pants-fitted legs; use the original263 catalogue's appropriate base for other bottoms. Independent component selection does not make an authored fit universal.

Reference portraits: orthographic span 1.65, target height 1.88, front camera distance 8. Chat crops: span 1.35, target 1.90. Body diagnostic span 2.7, target 1.28. Exact matrices, sizes and clipping values are in each receipt. The studio floor is camera-invisible only for underside diagnostics; its other ray visibility is preserved. Portrait framing remains identical between source and optimized assets at a given preset.

Packed references use Cycles, 24 samples, seed 42, denoising, AgX/None, exposure 0, gamma 1 and the unchanged studio lights. GLB does not carry the complete Blender studio, AgX transform, denoiser, compositor or Cycles light transport. The web comparison retains 263’s Three.js r180 environment panels, fixed lights, ACES exposure .95 and environment intensity .7. It is an internally matched geometry comparison, **not proof of Blender/native/WebGL color parity**. Do not modify the artwork to compensate for a native renderer mismatch.

Actual lens audit: both fixtures use `alphaMode=BLEND`, IOR 1, alpha approximately .075 for clear Reading lenses and .84 for dark Rectangular lenses. They have clearcoat/specular material extensions and **no KHR_materials_transmission or refraction**. The misleading historic material name “clear non-refracting pane235” is also used on the dark material; inspect the values, not the name. The two recipes are selectable in the local viewer: authored GLB materials and 263 preview materials. Lens/frame colors and materials remain separate. Required glTF material extensions are listed in `verification/assets.json` and in the GLBs.

`materials.json` records all material values/extensions and meshes carrying vertex alpha. Preserve `COLOR_0`, including alpha, for the taper and sculpted hair. Discarding that channel can turn the fade into a solid cap. Preserve authored normals; blanket normal regeneration changes the highlights. The viewer’s optional solid hair colors neutralize RGB vertex shading while retaining its relief variation and alpha; the original authored color is restored exactly when selecting Original.

A nearest-opaque-depth compositor will mishandle these alpha lenses and the taper’s translucent coverage. Depth is geometric ordering, not an optical transfer function. Lens layer Z uses alpha threshold 0; other layer Z uses .5. Layers retain other components in shadow/reflection rays, so colors depend on the full fixture. PNGs are display-referred, straight-alpha outputs; do not assume their colors are linear or composite them as opaque surfaces. Correct edge coverage, alpha color handling, reflections and overlap must be compared against the full reference. These fixtures do not qualify future transmitting/refracting glass. If transmission is introduced, inspect KHR extensions even if alphaMode says OPAQUE.

## Native next step — use existing labs

Read the current `codex/native-avatar-render-proof` branch and its Phase 157 ledger before editing. The read-only remote snapshot checked for this handoff was `36c1fd735f9f06ab575127d2663d7ab6e681095a`. Existing native docs include `docs/handoffs/native-avatar-lab.md`, `native-avatar-viability.md` and `experiments/avatar-proof/lightweight/README.md`. Prior Pixel 7 Pro/iPhone 16 Pro evidence used older artwork and synthetic accessories; it is not a measurement of 264. Do not overwrite frozen 209/Phase156 inputs or those receipts.

1. Stage this package under a separate 264 asset revision in Development-only labs. Verify `manifest.json`. Load the ordinary GLBs first; the offline baker must not be required to decode quantized/compressed formats. Preserve the current production avatar and the authoritative three-byte wire profile contract.
2. Produce the same four looks at 120 and 512px on native iOS and Android. Compare **263 packed reference → 264 optimized re-import → native 3D → lightweight portrait**. Also compare source vs optimized through the same native engine to isolate geometry cost from shading changes. Test clear/dark lenses with frames and eyes visible, cap overlap, ponytail rear opening, fade alpha, HOT, hoodie neckline and pants cuffs. Keep geometry, camera, palette, material policy and asset version in the evidence and cache keys.
3. Use the existing seeded actual-message-row workloads after appearance matches. Separate a cold process/engine, warm engine with a new image, disk hit and decoded hit. Retain existing mixed, all-unique, repeat, churn and burst cases. Only visible feature differences create unique portrait keys; offscreen pants colors must not inflate the portrait-combination count.
4. Measure visible completion latency, loading/decoded/process/GPU peaks, source residency, scrolling/typing with keyboard, map coexistence, background/resume, cancellation and cache invalidation. Include sustained/thermal runs and minimum supported physical iPhone and Android, not only high-end phones. Record actual binaries, device/OS, build mode, input hashes and raw receipts. No render queue may stall text delivery. Keep caches/queues bounded and prioritize visible requests.
5. Renderer/cache/concurrency changes still need the repository’s independent review and appropriate local/device verification. Local results do not waive a failure or equal a release gate. Decide the renderer only after matching appearance and actual-app workload measurements.

## Working without GitHub Actions

No hosted workflows were run or modified. No push or deployment was made. The package is self-contained and needs no CDN or GitHub access at runtime. `python tools/serve.py` serves it locally at `http://127.0.0.1:9264/`. For a trusted local network, run `python tools/serve.py --bind 0.0.0.0` and use that computer’s LAN address on the phone; firewall access may need local configuration. No firewall or existing self-hosted runner configuration was changed.

Transfer the ZIP or this folder to the other computer, verify it, then use the native labs’ existing local build/test commands and connected devices. Use the existing self-hosted work only after its owner confirms readiness and scope. This handoff adds no parallel runner infrastructure and does not require paid Actions to continue development. Physical-device/native rendering and lightweight composition of 264 remain the next verification stage; they were not run on this Windows artwork workstation.

## Reproduce locally

1. Verify delivery: `python tools/verify_package.py` (standard library).
2. Regenerate optimized GLBs: `node tools/optimize.mjs pass2` (pinned simplifier bundled; Node 22 used).
3. Extract components: `python tools/components.py` (standard library).
4. Check source/derivative geometry and component reassembly: `python tools/check_components.py` (NumPy/Pillow).
5. Blender5.2: `blender --background --python tools/render_blender.py` and `blender --background --python tools/bake_layers.py`. Packed scenes include their dependencies; the scripts use package-relative paths. GPU CUDA is used when available, otherwise CPU. Runtime platform/hardware can affect rendering timings and small pixel differences.
6. Check pants clearance: `blender --background --python tools/check_fit_blender.py`. Check paired outputs with `python tools/check_depth.py` (NumPy/OpenEXR). Re-rendered files require a new manifest; do not silently reuse this delivery’s hashes.

The included scripts are build/inspection tools. Do not ship source Blender files, inspection HTML, reference images or these scripts in the native production app. Select the required component assets or baked representations after native qualification.
