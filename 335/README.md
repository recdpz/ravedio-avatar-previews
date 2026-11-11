# Wavy bob catalogue integration

Revision 335 integrates the owner-approved actual B source from revision 334
into the existing Feminine `bob` slot. The uncovered default GLB is copied
byte for byte from the approved asset. The approval, base source and all
other hairstyles are preserved. Profile fields and native app code do not
change.

All 128 bob fit rows are updated: eight headwear choices, eight tops and
default/ombre finishes. Each headwear uses its own contact fit. The beanie
presses hair near its fabric boundary; the bandana retains the triangular
scarf; the pashmina tucks the lower bob inside its existing hood. Hair UVs,
normal maps and gloss are retained. The animal-ear assembly and its sprout
attachment sit 0.020 units lower for contact with this bob only.

The palette has eight distinct looks: Brown, Black, Auburn, Blonde, Platinum,
Pink, Purple and Ombré. Original and Brown are aliases. Solid colors retain
the authored surface maps. Ombré uses embedded vertex colors from brown roots
to warm caramel lower sections; it does not turn every short fringe tip blond.
Default and ombre variants have identical geometry.

The interactive preview retains separate feature selectors. Bob bindings are
resolved by headwear, top and finish after the inherited catalogue maps, so
a shared old source path cannot accidentally select a different covered fit.
The Studio render checks below the viewer have all 512 headwear/color/angle
combinations. Those renders use Tan skin, Rounded bean eyes and a Jersey.

## Local outputs and reproduction

Outputs are in `D:/Ravedio-Avatar-Work/native335`, exposed by `335/files`.
Build with `tools/integrate_bob.py` in Blender 5.2.0, then run
`tools/verify_integration.py`. Use `tools/render_review.py` for the eight-view
palette/headwear grid and `--wardrobe` for the related tops and dark-skin
checks. `--accessories-only` checks glasses and the ear-band sprout.
The renderer is standalone and accepts `--work EXTRACTED_CATALOGUE` and
`--source PACKED_BLEND` after Blender's `--` separator.

With Pillow, run `tools/make_sheets.py` and `tools/package_source.py`.
`tools/make_preview.py` reproduces the feature viewer from revision 309
without changing older previews. Disable Python bytecode output when running
these tools on the nearly full E: drive.

The source package includes the full component catalogue, ordinary GLBs,
the original approved packed scene, the integrated packed scene, lighting and
palette recipes, the standalone render script and SHA-256 manifests. A smaller
delta package is also supplied for an exact revision 330 base.

## Rendering scope

These are source assets, retaining about 440,000 hair triangles per fit.
They are not a phone performance qualification or an optimized app payload.
glTF carries the hair's PBR materials, maps, clearcoat and ombre vertex colors.
Cycles world lighting, color management and the clothing's disabled glossy-ray
visibility remain Blender scene settings; a native renderer must handle its
appearance explicitly. Frames and lenses remain separate unchanged components.

No baked mobile portrait/depth cache is included. Regenerate color and depth
together from catalogue 335, using the same geometry, camera and version.
Do not combine the new bob with depth maps from an earlier catalogue.
