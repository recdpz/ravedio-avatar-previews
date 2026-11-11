# Ravedio avatar previews

Independent art experiments for review. These pages do not publish an Avatar Studio generation or change product/profile contracts.

## Current mobile artwork: 335

The complete model catalogue and rendering handoff are **release attachments**,
not files downloaded by `git pull`. This art repository is separate from
`ravedio/mobile`. The hosted Pages `/335/` preview is not deployed while hosted
Actions are paused. Use the public release downloads for phone testing.

- [Get the full 335 artwork and handoff](handoffs/catalogue335/GETTING-335.md)
- [Public 335 release and downloads](https://github.com/recdpz/ravedio-avatar-previews/releases/tag/avatar-art335-source)
- [Profile format / named asset-selection interface](handoffs/catalogue335/README.md)

Quick setup, using Python 3.9+ with no external packages or GitHub login:

```sh
curl -fL https://github.com/recdpz/ravedio-avatar-previews/releases/download/avatar-art335-source/get335.py -o get335.py
python3 get335.py ./Ravedio335
```

This downloads and verifies the source catalogue, ordinary GLBs, packed Blender
scenes, studio/palette, standalone render script, complete named settings,
fitted mappings and worked examples. It needs at least 3.7 GB of free space.
Start with the resulting `Ravedio335/handoff/README.md`.

## Floating prototype 138

A reference-inspired rounded head and glossy floating body. Main avatars remain unchanged. Blank face is the primary reference direction; dark eyes are optional.

Rendered views were inspected twice. Interactive model runtime checks are recorded separately from geometry and visual review. Model files use standard glTF 2.0, Y-up coordinates.

Three.js r128 and its GLTFLoader are distributed under the MIT license.
