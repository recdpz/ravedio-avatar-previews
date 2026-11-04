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
