# Ravedio 270 phone appearance check

Use these two fixed looks in the existing Development avatar labs on iOS and
Android. The manifest identifies the ordinary GLB inputs, packed Blender scenes,
palette, camera, and paired color/depth outputs. Each look has light and deep
skin references at 48, 64, and 512 pixels. The models share a common coordinate
system. Keep glasses frames and lenses separate.

1. Verify the archive and the component hashes in its manifest. Add these two
   looks under a fresh art/cache revision in the existing lab. Keep the
   committed historical fixtures as comparisons. Select these fixtures by the
   lab's explicit IDs in seeded data.
2. Capture the native 3D view at the stated camera, then capture the same looks
   in the actual native message rows. Verify eye and smile readability on both
   tones, clear and dark lens overlap, the bandana's front edge, and the
   relationship between the two braids and the pashmina. Compare at native
   display size before zooming into artifacts.
3. Run the lab's repeat, all-unique and burst workloads on physical phones.
   Record cold first render, warm misses, cache hits, loading peaks, frame
   timing and visible completion. Include the phone, OS, exact app and fixture
   versions, and the selected renderer settings.

The depth files describe geometric visibility. The clear/tinted lenses use
opacity blending. Compare lens overlap in the full color references and the
native output, since a single depth layer does not carry lens appearance.
Blender AgX/Cycles and native lighting are separate render paths.

The existing native lab branch is `codex/native-avatar-render-proof`. See
`docs/handoffs/native-avatar-lab.md` there for resource staging and the seeded
app workloads. This package contains art references. Physical phone results
are pending.
