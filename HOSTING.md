# Avatar preview hosting

The authored catalogue exceeded the Pages deployment size. Large GLB, Blender,
ZIP, PNG and EXR files remain in this repository unchanged. `_config.yml`
excludes those files from the Pages artifact. `asset-host.js` and explicit
download/image links load them from a pinned GitHub raw ref instead.

Each review page loads `asset-host.js` before its viewer. It maps only binary
asset URLs inside this preview repository, including relative URLs resolved
against the document. JSON, JavaScript, CSS and compact JPG/WebP review boards
remain on Pages. Cross-origin images use anonymous CORS so canvas exports can
still read pixels. No credentials or API tokens are sent to the asset host.

Keep the art files, manifests, shared coordinates, materials, palette controls
and snapshots intact. This is delivery packaging, not model optimization.

For the next publication, commit the new art assets first, then pin the loader
and explicit links to that commit, update the exclusion list and current
review manifests, and verify both public asset hashes and browser controls.
Never remove saved sources or silently repoint old revisions to changed art.

Pages now publishes from the generated `gh-pages` branch at `/`. Cloning the full
artwork tree exhausted the hosted runner's disk even though Jekyll excluded those
assets afterward. `main` remains the source/archive authority.

After committing the verified art and UI on `main`, run
`python tools/prepare-pages.py --source main --index ABSENT_ABSOLUTE_INDEX_PATH`.
The script reuses exact Git blobs for UI/text/JPG/vendor files, omits the same
large binary suffixes, and records source and asset commits in
`hosting-source.json`. It uses a separate index and never checks out the branch
or changes the working index. Review and push `gh-pages`; never merge its
generated tree into `main`. Later publications must regenerate this branch.
Verify the Pages job on the exact generated commit, provenance, file hashes,
versioned asset loader, old preview compatibility, and current viewer controls.

Large pushes from Windows stalled/reset in this environment. The same push from
WSL Git succeeded; credentials were passed in process memory only. Avoid logging
credentials or changing global Git settings to work around a transfer failure.
