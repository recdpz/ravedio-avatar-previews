# Bob directions source review

The owner approved B, Wavy bob and curtain fringe, on November 10, 2026.
The approved artwork is the actual revision 334 Blender model and its GLB,
not the ImageGen concept. Checksums and the exact owner statement are in
`../approvals/bob334-waves.json`. B is now the selected bob direction;
revision 332, Tucked + Brushed, remains preserved as the earlier baseline.
Each direction has eight actual Blender renders, an editable source scene
and an ordinary GLB containing its hair component. A and C were not selected.

The three directions are Blowout bob, Wavy bob with curtain fringe, and
Asymmetric bob. The cuts use directly authored continuous coverage surfaces,
overlapping closed styling sections and separate front sweep paths. Their
brushed UV coordinates follow those sections from crown to ends. Geometry
and UVs are built together; the models do not use voxel remeshing, Boolean
cuts or a nearest-surface UV transfer from the older hairstyle.

Run tools/build_directions.py in Blender 5.2.0 with the packed revision 332
Tucked scene and an output directory after `--`. Run tools/verify_sources.py
with the same arguments to check the source and export the GLBs.
Run `tools/make_comparison.py OUTPUT` with Pillow to lay out the comparison
images. Mount OUTPUT at `334/files`.

The concept sheet was made with the built-in image_gen tool. Its exact
prompt is recorded in concept-prompt.txt. The reference image was the
revision 332 Tucked + Brushed avatar. The concept is an artistic target.
The PNGs in review and all three Blender scenes are the modeled results.

The underlying head, face and body geometry is retained in shared
coordinates. Approval freezes B's present bare-hair geometry and finish.
Headwear fits, other hair colors, optimization and catalogue integration
remain implementation work; they have not been qualified by this approval.
The concept sheet is not a Blender render and is not evidence of an exact
3D match. The approved model and its recorded checksums are the artwork
authority; the concept remains a comparison reference.
The modeled hair is still broader and more structured than the generated
reference, particularly in its lower sections. B is approved source artwork;
it is not yet an optimized or integrated mobile catalogue asset.

The local output directory is `D:/Ravedio-Avatar-Work/native334`. The
`334/files` junction points there. Verification reports are source-review.json
and browser-review.json. Checks cover unchanged body/face coordinates,
closed mesh boundaries, finite geometry/UVs, packed textures, ordinary GLB
material exports, all 24 selector combinations and source download links.
