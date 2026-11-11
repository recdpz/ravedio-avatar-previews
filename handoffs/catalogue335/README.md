# Catalogue 335: mobile asset-selection handoff

This is an **asset handoff**, not authorization to change firmware, BLE, LoRa,
cloud profile columns, production codecs or migration policy. It publishes the
source artwork through `f7a01d2` and a named rendering-settings interface.

## Profile-format decision

**A larger format was not finalized for this 3D catalogue.** The six-byte
document is an owner-directed proposal, not an implemented/frozen contract.
It has a proposed bit layout, but no complete approved mapping from its numeric
values to today's catalogue 335 options. A five-byte allocation explorer also
exists; it is a design tool, not a wire specification. Do not infer wire IDs
from selector order, JSON ordering, asset hashes or preview revision numbers.

The current inspected firmware/native transport is still **three profile
bytes**. The native avatar consumers interpret those bytes using the **legacy
sprite catalogue**, whose hair, colors, extras and face values differ from the
3D catalogue. Their decoder has no in-band layout-version field. The top two
bits are a type, not a version. A fourth local/cloud byte remains reserved at
zero; it is not a fourth transmitted avatar byte.

`profile-formats.json` records every current field position, default, type and
encoded value, plus the separately labeled six-byte proposal. `legacy_profile3.py`
and `legacy-examples.json` provide current-codec reference vectors and their
actual expected legacy sprite-resource keys. They are not a recommendation to
restore pixel art. In particular, `40 00 00` is a valid avatar in the current
decoder; it is not an avatar-clear operation. All-zero `00 00 00` is the current
canonical none/clear. Flag/social proposals must not change those semantics.

For 3D testing, use **`avatar-settings.schema.json`** and `defaults.json`.
`schemaVersion: 1` versions this named asset interface only. It does not assign
a new profile/wire version. All new-art worked examples explicitly contain
`profileBytes: null`, because no authoritative byte-to-335 mapping exists.
Age, country and social metadata have no renderer field in this schema.

## Complete selection mapping

Extract the full 335 source catalogue, then run:

```
python3 resolve_avatar.py /path/to/catalogue335 settings.json
```

Use `python3 resolve_avatar.py --defaults` to obtain complete defaults for both
builds. The strict resolver rejects unknown IDs, missing/extra fields,
unsupported settings versions and absent fit rows. It does not silently replace
someone's saved appearance. `named-examples.json` contains complete inputs,
expected fit selectors, every component hash/path and material overrides.

`catalogue-options.json` lists all names, labels, palettes, aliases and defaults.
`complete-mapping.json` contains all 1,792 fitted rows and every independently
selected base, bottom, face, groom, glasses and detail binding. The same data
is in the authoritative `catalogue.json` in the full source archive. Hair fits
are selected by build/hair/headwear/top/default-or-ombre; they are not additional
profile choices. Preserve `hairLengths` when supplied. Select the base by
bottom and shirtless/clothed state, rather than reusing one body for every look.

Current restrictions are contextual: eight hairstyles per build; eight tops
and four bottoms for Feminine; six tops and two bottoms for Masculine; only
`groom: none` for Feminine. There are eight headwear choices for every current
hair/top combination. Membership in the fit table remains the authority.
Only no nose and regular smile are supported. Feminine lashes are included
automatically. Detail choices are None, Sprout and HOT; face gems are removed.
Reading glasses default to clear; other glasses default to dark. An explicit
lens choice is retained. Headgear color with no headgear, frame/lens choices
with no glasses, and top color when shirtless are visually inactive.

Original and Brown are the same authored hair pigment. `default` garment and
headwear colors are contextual authored aliases, not universally black.
New solid hair colors recolor the chosen fitted default GLB; ombre selects
the fitted baked-vertex-color GLB. Its beard retains the authored root pigment.

## Material and renderer behavior

Ordinary GLBs contain the original geometry, transforms, PBR values and maps.
Do not independently center/scale components or merge selectable/recolorable
roles. Preserve the separate frame and lens components and their materials.
`material-rules.json`, `material_recipes.mjs` and the exact `viewer335.js`
snapshot specify the remaining overrides. The Python resolver emits a material
plan, including linear RGB pigment values and the packaged jersey dye textures.
The JS helpers reproduce hair-vertex-color neutralization, patterned-cloth dye
and the tortoise frame pattern. Clone materials before applying overrides.

Native engines must implement these rules explicitly. Loading a correct GLB
alone does not reproduce browser texture-dye callbacks, alpha sorting or the
Blender studio. Preserve the selected lens alpha/surface, use zero transmission,
IOR 1 and depth writes off for the current clear-lens treatment. Preserve
normal/roughness maps and ombre vertex colors. Do not replace patterned clothing
with a flat tint. The full archive includes shader maps, dye textures, the
packed approved and integrated Blender scenes, studio/palette settings and a
standalone bob render script. See its README for Blender/Cycles differences.

Regenerate portrait color and depth together from this artwork, camera and
version. Existing older-bob portrait/depth entries are not valid for 335.
Phone memory/responsiveness and visual qualification remain the mobile agent's
work. Source assets are high resolution and are not optimized app payloads.

## Provenance and downloads

The art source commit is `f7a01d2` in `recdpz/ravedio-avatar-previews`.
`artwork-provenance.json` records full commits, catalogue/source hashes, archive
sizes/hashes and the inspected mobile/firmware source pins. The current bob is
the owner-approved actual 334 B, Wavy bob and curtain fringe, integrated into
the existing `Feminine/bob` slot. Its uncovered GLB remains byte-identical.

`release.json` identifies the remotely verified GitHub release and attachments:
the full source catalogue, the smaller exact-330 bob delta, this handoff, and
SHA-256 receipts. Use the full archive when the receiving computer does not
already have the exact 330 base. The handoff ZIP contains all generated schema,
mapping and example files; the small authoring sources are also committed here.

Keep any future profile expansion in a separate reviewed protocol phase.
This handoff does not choose numeric IDs for new art, enable shorter flag/social
payloads, repack name metadata or alter the profile-present flag.
