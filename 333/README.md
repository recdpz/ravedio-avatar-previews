# Curtain Bob source review

The owner selected Tucked + Brushed from revision 332. That saved look is
the reference on the left of this review.

Revision 333 is a second Bob built with new paths and cross sections.
It has two face-framing curtains, a center part, overlapping side
layers and a continuous shaped back surface. The recessed coverage mesh and the new outer sections
share the existing head coordinates. The new locks use the approved
brushed normal and roughness maps through a Lock flow UV layer.

Run tools/build_curtain_bob.py in Blender 5.2.0 with the packed revision
332 Tucked scene and an output directory after `--`. Run
`tools/make_comparison.py OUTPUT` with Pillow to create the review sheets.
Run tools/verify_source.py in Blender with the same arguments to check
the source and export the ordinary hair GLB. The editable Blender model
and ordinary hair GLB are in the output
directory, mounted locally at `333/files`.

The new cut is under review. Its covered headwear fits and catalogue
bindings remain pending selection.
