# Ravedio 314 mobile rendering handoff

Revision 314 is the candidate. Revision 308 is the visual and performance control. Both run through the same Development code and use identical case selections, skin indices and 64 conversation rows. The two builds have separate asset receipts and cache keys. The 3D lab keeps its existing rotation and detail camera. Chat portraits use the approved 15° view, close framing with the top visible, and Cool white `#F1F4FA`.

## Files

- `index.html` compares six looks on all four skin tones at 48 and 64 CSS pixels. It opens on the deepest tone. `deepest-tone.png` is the static contact sheet.
- `references/` contains 48 paired full-scene color and depth renders across the two revisions. Each 384 px transparent color PNG is paired with a camera-space Z EXR from the same render. The plate is composited in linear color for the small previews. The depth describes visible geometry at alpha 0.5, so transparent lenses need the separate lens group in the compositor.
- `native/` contains the four 314 assemblies, seed, per-component digests and baked alpha layers. The name `r308` identifies the existing lab slot and scenario IDs. The embedded art revision is 314.
- `mobile-314.bundle` carries the code commit. The included manifest pins every transfer file. The separate `Ravedio314-catalogue-delta.zip` overlays the verified 308 catalogue.

The native cases are Curls with Pashmina and clear Reading glasses, Flow with Cap and dark Wayfarers, Twin Braids with Jersey and Pashmina, and ombre Ponytail with Beanie and Jersey. Each runs on four skin tones. Bare Twin Braids and Flow with Cap and unobstructed eyes are supplemental Blender comparisons.

## Verify and load the code

Download the ZIP and its SHA-256 sidecar. Check the digest before extracting it. Run the included verifier from the extracted directory with Python 3.11 or later.

```sh
python3 /absolute/path/to/handoff/verify_transfer.py phone /absolute/path/to/Ravedio314-phone-handoff.zip
```

The mobile checkout needs the previously shared 308 baseline commit `7d6c7a7a9c24114bc154ca01c6fc979d978ee2f0`. Run these commands in that mobile repository. The bundle creates a local review branch.

```sh
git bundle verify /absolute/path/to/handoff/mobile-314.bundle
git fetch /absolute/path/to/handoff/mobile-314.bundle refs/heads/codex/avatar-308-development:refs/heads/codex/avatar-314-phone-review
git switch codex/avatar-314-phone-review
```

Stage the candidate with the following environment. Keep it set while building. Use the 308 control first if a baseline capture is still needed. For that build, unset `RAVEDIO_AVATAR_R314_SOURCE` and set `RAVEDIO_AVATAR_R308_SOURCE` to the extracted 308 native fixtures and `RAVEDIO_AVATAR_R308_ALPHA` to the extracted 308 approved chat pack. The checkout also contains the original setup guide at `docs/handoffs/native-avatar-r308.md`.

```sh
unset RAVEDIO_AVATAR_R308_SOURCE RAVEDIO_AVATAR_R308_ALPHA RAVEDIO_AVATAR_R308_CHAT_REVIEW
export RAVEDIO_AVATAR_R314_SOURCE=/absolute/path/to/handoff/native
python3 tools/avatar-proof/prepare_native.py
```

## Build and capture

**Android.** With JDK 21 and the configured SDK, run the following from the repository root. Install the two APKs on the test phone.

```sh
cd apps/android
./gradlew -PavatarLab=true :avatar-lab:testDebugUnitTest --rerun :avatar-lab:assembleDebug :app:assembleDevelopmentDebug
adb install -r avatar-lab/build/outputs/apk/debug/avatar-lab-debug.apk
adb install -r app/build/outputs/apk/development/debug/app-development-debug.apk
adb shell am start -S -n com.ravedio.avatarlab.dev/com.ravedio.avatarlab.AvatarLabActivity --ez r308_alpha_probe true
```

Launch the lab with `--ez r308_probe true` for 3D captures or `--es scenario r308-visual` to rotate. Launch `com.ravedio.app.dev/com.ravedio.app.MainActivity` with `--ez avatar_r308 true --ez avatar_alpha true` for the layered conversation.

**iOS.** On the Mac, run `python3 tools/avatar-proof/native.py ios-build` to stage assets, generate both projects and build the simulator lab. Use Xcode and local signing for the connected iPhone. Run `RavedioAvatarLab` with `--r308-alpha-probe` for portrait captures, `--r308-probe` for 3D captures or `--scenario r308-visual` to rotate. Run `RavedioDevelopment` with `--avatar-r308 --avatar-alpha` for the layered conversation.

On both phones open Developer tools → Samples → Messages and confirm the header shows the staged revision. Use the existing `AvatarMessageIntegrationTest` and `AvatarUsageMeasurements` instructions in the 308 guide. Compare `r308-alpha` to `r308-gpu` in separate launches. Save probe PNGs and JSON per phone, revision and mode before switching builds. The alpha probe should match all 64 expected output digests.

Review 48 and 64 px portraits in both chat themes. On the deepest tone, compare the smile and eyes, including the clear lens catchlight and the deliberate tint on the sunglasses. Rotate the four assemblies to inspect the ponytail gather, beanie cuff and front locks, braid drape and cloth overlap. Capture the first visible portrait, placeholders, cold and warm scroll frame times, peak memory and thermal state on the same phone and viewport. A missing component, new overlap artifact, unreadable facial feature or a repeatable responsiveness regression should have a matching capture before accepting the candidate.

## Catalogue and qualification

Run the verifier against the existing full 308 archive and the 314 delta. It checks the base digest and all changed files and writes the resolved 314 index. In that index, a component comes from the delta archive when present there and otherwise comes from the verified 308 archive. Components retain their assembly transforms and separate material controls.

```sh
python3 /absolute/path/to/handoff/verify_transfer.py catalogue Ravedio308-catalogue-full.zip Ravedio314-catalogue-delta.zip --index catalogue-314.json
```

The overlay changes 416 of 1,792 fit selectors and supplies 74 new ordinary GLBs. It also carries the updated eyes and smile bindings for both builds and the lens material overrides. Its deterministic `catalogue-workload.json` covers 128 distinct looks across all 16 hairstyles and 512 messages at eight arrivals per second. The current lab exercises 16 looks. Feeding the larger seed through the catalogue-backed app path is a separate step for the phone tester before qualifying first-seen churn.

The paired references passed coverage checks with a minimum agreement of 99.9454%. The 314 portrait pack contains 148 cropped color/depth groups and 64 expected pixel hashes. The Android Development APK and lab built locally, and the Kotlin compositor matched all 64 hashes. The physical iOS and Android runs and the Xcode build are pending. The deepest-tone board shows the revised smile more clearly. The dark glasses still intentionally mute the eyes, and the remaining small clear-lens highlight should be checked on the phones.
