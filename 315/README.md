# 315 Aero Satin

Revision 315 applies the Aero Satin materials to the source catalogue. The rotatable preview loads the revised ordinary GLBs directly. The PBR changes are embedded in the exports. The browser and Blender each read their lighting from `studio.json`.

- The neutral sky fill and cool edge lights leave more room for the eyes and smile. Skin and hair carry a soft clearcoat. Fade and stubble stay matte.
- Cloth receives material-specific roughness, with small embedded weave, knit or jersey maps where the authored UVs support them. Existing textile, normal and colour images are preserved.
- Glasses have separate clear and dark lens exports with alpha blending. Frames, sprout leaves and clip, HOT ink and sticker, buttons, and hat trim retain independent surfaces.
- Meshes, UVs, original binary buffers, transforms, skin tones, component fits and colour choices are preserved. The catalogue spans all 1,792 fitted rows from 314.

## Rebuild and review

`catalogue-input.json` is the resolved revision 314 selection snapshot. `finish.json` defines the authored PBR surfaces. Run `tools/export.py OUTPUT --source-mount WORK_ASSETS` with Python 3.12. Use an output folder with about 2 GiB available and explicitly allow the existing source asset mount. The exporter writes a digest-keyed GLB directory with `catalogue.json`, `receipt.json`, and the jersey dye maps. Mount it at `315/assets` for the local preview. The local generated catalogue lives at `D:/Ravedio-Avatar-Work/native315/assets`.

`tools/blender.py` builds packed editable reference scenes from the 315 GLBs and the verified 308 base scenes. Pass the 308 fixture directory, its resolved selection JSON, the mobile avatar-proof tools directory, the 315 export directory and the output directory after Blender's `--`. The local sources live at `D:/Ravedio-Avatar-Work/native315/source-scenes`.

`tools/review.cjs` runs against the local preview and compares 16 combinations to 314. It checks the rendered geometry, color and accessory selections, the asset URLs, and the lens switch. It captures eight angles per hairstyle. The export receipt covers all source components and both lens tints. Device rendering and a refreshed phone-test portrait bake are separate from this art revision.
