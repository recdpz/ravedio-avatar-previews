RAVEDIO ARTWORK AND RENDERING HANDOFF224

SELECTED ASSETS
The two owner-selected feminine looks are packed Blender scenes and static GLBs. Feminine-uncovered uses choices222; Feminine-cap uses choices223 with the red Pulse emblem. Both include the selected button-up and red skirt. The exported shape requires no sliders, morph controls or runtime hair/cloth physics. Underlying bodies, faces,178 arms, wardrobe shapes,151 palette and181 studio remain from their declared sources.

REFERENCE AUTHORITY
The four preserved209 references remain the baseline: both builds in Fair and Brown, Original eyes, Smile, no nose; feminine Bob/Tank/Skirt and masculine Side part/Tank/Shorts/Stubble. These are original source-art composites, not native-lab derivatives.209 has explicit scoped face/stubble acceptance. Owner-selected222/223 parameters are separate decisions; they do not approve the whole later catalogue. baseline-authority224.json identifies exact inputs and checksums.

PACKAGES
1. ravedio-handoff224-assets.zip:25 independent static components, native/round-trip pictures, four-tone portrait sources/crops, browser review and handoff records.
2. ravedio-handoff224-assemblies.zip:seven complete shared-coordinate GLBs under assemblies/. These are redundant assembly examples, not a separate catalogue.
3. ravedio-handoff224-scenes.zip:seven packed/reopened fixture scenes under scenes/, portable reproduction/export tools and requirements. One source per distinct look, never a scene per camera.
4. The preserved ravedio-baseline209.zip is reused from preview211. It supplies the four original .blend/.glb/reference PNG/settings sets under baseline/. Extract into the same working folder to test209. This package is unchanged.

The hosted224 review loads actual exported components and starts at the selected red cap. It includes two selected looks and five developed fit assemblies. Baseline images appear separately. Earlier223 controls remain available for historical tuning; they are not required to render224 assets.

PORTABLE REPRODUCTION
Use Blender5.2.0 LTS or explicitly verify a producer-version upgrade. Dependencies are packed. From the extracted source folder:
  blender -b --threads 4 --python reproduce224.py -- --scene scenes/Feminine-cap.blend --output cap.png --size 512
  blender -b --threads 4 --python reproduce224.py -- --scene scenes/Feminine-cap.blend --output cap120.png --size 120
  blender -b --threads 4 --python reproduce224.py -- --scene scenes/Feminine-hoodie.blend --glb assemblies/Feminine-hoodie.glb --output roundtrip.png --angle profile --size 512
  blender -b --python export224.py -- --scene scenes/Feminine-cap.blend --group hair --output selected-hair.glb
Tools use local files only. CPU rendering is forced by reproduce224.py; sampling can differ slightly from a GPU render. Authored geometry/camera/light/material settings are retained. No geometry reduction is included.

ASSEMBLY AND FIT
assembly224.json maps each look to independent base, hair, eyes, mouth, clothing, cap, frames, lenses, HOT and grooming files as applicable. Parts share original world coordinates and transforms. Never normalize a component by its individual bounds. Covered/uncovered hair are separate authored variants. Do not deform the uncovered ponytail through the cap. Selected covered roots/tie are fitted already. Female cap choices apply only to her selected look; masculine fixtures keep the existing navy Orbit cap.
Frames and lenses are separate. HOT retains its original flame-shaped badge. Both hoodie assemblies retain independent sleeves/cuffs and support inspecting behind the floating arms. Future accessories are not certified by these fixtures.

REVIEW AND LIMITS
First review: native construction, rooted hair flow, cap opening and assembled fit. Second review: fresh reopened sources and actual GLB reimports, front/three-quarter/both profiles/back/top/underside/full body, hidden arm-contact areas and four skin tones. The floor initially obscured underside views; corrected diagnostics disable its camera visibility temporarily and restore it. Saved models/studio are unchanged by that diagnostic.
Source/imported GLB vertex positions compare exactly in world space; selected exports have no active morphs. Lenses are closed manifold geometry with opacity1/transmission1/IOR1.25. Structural checks do not establish artistic acceptance or native-app material parity. Blender-only ray flags, area lights and AgX are not carried by GLB. Source/import pictures deliberately expose differences, including colored chin reflections. Read rendering-requirements224.json.
The32/48/64/128px files are crops/downsamples of512px native sources.120 and512 are independent renders with identical framing. These are readability checks, not physical-pixel-density phone tests.

NEXT NATIVE WORK
Read native-agent-handoff224.txt. Compare faithful source/native/portrait output before real app workload measurements. These full authoring fixtures are heavy: roughly0.73-0.96M triangles and18-21MB per complete GLB. Shared components avoid redundant resource loading but are not a qualified mobile budget. Any reduction needs a separately versioned derivative with matched visual comparisons and preserved sources. This handoff contains no mobile renderer, profile-bit or wire change.
