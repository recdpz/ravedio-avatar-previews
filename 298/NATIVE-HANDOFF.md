# Revision 298 native rendering handoff

Use the two authored fixtures in the iOS and Android Development builds.

| Fixture ID | Assembly | Check |
| --- | --- | --- |
| `r298-curls-pashmina` | Feminine, Curls, pashmina, button-up, pants, Soft hooded eyes and lashes, clear Reading glasses, HOT | Hair exits, cloth overlap, visible eyes behind lenses |
| `r298-flow-cap` | Masculine, Flow, cap, hoodie, pants, Rounded bean eyes, short beard, dark Wayfarers, HOT | Cap strap, dark lenses, smile and beard |

The Flow geometry is the byte-identical 295 control. Both fixtures have packed
Blender scenes, independently selectable ordinary GLBs in shared coordinates,
and matched color and linear depth. Front portraits use Fair and Brown skin at
48, 64, 120 and 512 px. Right-side and rear references use Light warm at
512 px. The manifest records the camera, lighting, color management,
appearance overrides, triangle and material counts, texture sizes and hashes.

## Stage on the mobile test host

1. Transfer the ZIP and SHA-256 receipt. Extract to a new folder. Run
   `python3 verify_archive.py /path/to/Ravedio298-native.zip 298` using the
   included verifier. Keep 295 and the older native lab inputs available as
   separate controls.
2. Start from mobile `codex/native-avatar-render-proof` at
   `36c1fd735f9f06ab575127d2663d7ab6e681095a`. Read its
   `docs/handoffs/native-avatar-lab.md`. The bundled `manifest.json` is the
   artwork authority. Use the ordered parts and appearance bindings in `mobile-stage.json` and
   the 16 seeded rows in `fixtures/r298-visual.json`. Add an opt-in fixed
   assembly path on each platform. The current resolvers derive a legacy
   component list from build and omit headwear, lenses, frames, lashes and
   HOT. Assert the resolved roles and hashes against the stage manifest
   before collecting images. Set the requested orthographic span to 1.35
   and aim at y=1.90. Preserve authored transforms and material overrides.
   Include assembly ID, skin, art, renderer, camera and size in cache keys.
3. Capture Blender, rotating native profile, and actual 48/64 px chat rows
   with the same skin and framing on each phone. Use 120 px to inspect eye and
   mouth readability. Check the rear cap strap and pashmina sides before
   starting the workload. Preserve separate frame and lens parts.
4. Pair placeholder and avatar runs on each device for repeats, all-new
   portraits and burst arrivals. Run both cold and warm. Record p50/p95
   first-visible latency, p95/p99 frame times, decoded and disk hits, and
   sampled memory peaks. Capture device, OS, build mode, app commit, fixture
   hashes and thermal state. Run locally on connected phones. Hold the
   renderer decision until the real fixtures pass both visual and device
   review. The art seed contains four distinct appearances. Use it to check
   real fixture cold cost and repeated rows. Keep the existing
   `unique-stress` and `burst` workloads for cache churn and arrivals, and
   report their input catalogue separately. Different senders with the same
   appearance should still reuse the same portrait.

The six-byte profile proposal is a separate workstream. This package uses
fixture IDs in Development only.

## Transparency and reference lighting

The lens overrides use alpha blend at .075 (clear) and .84 (dark), IOR 1,
zero transmission, front faces, and depth writes off. The depth reference is
geometric Z with a .5 alpha threshold. It cannot substitute for the transparent
lens blend. Compare the full reference color for the eyes and lens edges.

The packed Blender scenes carry the Cycles studio and AgX settings. The
browser reference uses the existing fixed viewer lighting and ACES tone
mapping. Ordinary GLB files carry geometry and PBR material inputs.
