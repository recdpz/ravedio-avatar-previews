# Getting the complete 335 artwork on the other computer

The art repository is **recdpz/ravedio-avatar-previews**, separate from
**ravedio/mobile**. The published source and handoff are GitHub **release
attachments**. `git pull` does not download them: the large local `335/files`
directory is deliberately ignored by Git.

The GitHub Pages `/335/` page is not deployed. It returns 404 while hosted
Actions are paused. The release and direct downloads are public and do not need
a GitHub login. Use the instructions below, rather than the Pages preview.

## One setup command after downloading the script

On the Mac or Windows computer, with Python 3.9 or newer:

```sh
curl -fL https://github.com/recdpz/ravedio-avatar-previews/releases/download/avatar-art335-source/get335.py -o get335.py
python3 get335.py ./Ravedio335
```

On Windows, use `python` instead of `python3` if that is the installed command.
No third-party Python packages, `gh`, Git clone or GitHub authentication is needed.
Allow at least 3.7 GB free. The script downloads 1.20 GB, checks pinned SHA-256
values, extracts to a fresh directory, checks all 638 component files, and
resolves the eight worked examples. It refuses to overwrite an unknown existing
installation. Running it again on a completed install re-verifies the files.

Expected output:

```text
Ravedio335/
  INSTALLATION.json
  catalogue/
    catalogue.json                 # 335; 1,792 fitted rows
    assets/                        # 638 ordinary component GLBs
    Ravedio335-Wavy-bob.blend        # packed integrated source
    sources/approved-B334.blend     # approved bob source
    tools/render_review.py         # standalone Blender renderer
    studio.json
    palette.json
    jersey-dyes/
  handoff/
    README.md
    avatar-settings.schema.json
    catalogue-options.json
    complete-mapping.json
    resolve_avatar.py
    named-examples.json
    profile-formats.json
    viewer335.js
    material-rules.json
    material_recipes.mjs
```

`INSTALLATION.json` records successful validation and exact output paths. The
archive's studio render helper accepts `--work PATH_TO_catalogue` and
`--source PATH_TO_PACKED_BLEND` after Blender's `--` separator.

## Direct downloads if a connector cannot fetch release assets

- [Full 335 source catalogue, 1,197,016,866 bytes](https://github.com/recdpz/ravedio-avatar-previews/releases/download/avatar-art335-source/Ravedio335-full-source-catalogue.zip)
- [Named-settings handoff, 204,636 bytes](https://github.com/recdpz/ravedio-avatar-previews/releases/download/avatar-art335-source/Ravedio335-mobile-selection-handoff.zip)
- [Release and SHA-256 sidecars](https://github.com/recdpz/ravedio-avatar-previews/releases/tag/avatar-art335-source)

The catalogue SHA-256 is
`55a9409b199b46e313c2aa67e28b21789805f06292cac1f9933e1c1db15c7bfc`.
Artwork source commit: `f7a01d28eb3784310ace9c38af2f00e6df68af52`.
Selection-code source commit: `32372004794a5fed8ad3df0fc498ba9fe4e22e70`.

These assets are the approved 335 baseline. Later 336/337 hairstyle studies are
separate unapproved comparisons and are not required for the phone tests.
Use the named settings schema for 3D selection. The deployed three-byte profile
still describes the legacy catalogue; the larger format is not finalized.
Keep protocol changes out of this asset test.
