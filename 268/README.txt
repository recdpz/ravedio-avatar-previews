Ravedio268 - larger head reductions and lower height

Adds15%,20%,25%,30% smaller spherical heads, while retaining5/8/10/12% and current size. Default20% with Keep original gap. Shrinking about the center naturally raises the underside; Keep original gap compensates with lift=-50*(1-scale) percent of original0.96 head height. Reference underside stays atY1.4. Negative manual offsets lower the head; the dynamic minimum preserves that underside/torso clearance. Manual maximum remains+3%. Save choices exports actual scale, height mode, world lift and fit recipe as Ravedio268-choices.json.

Source266 ordinary GLBs are reused unchanged; no duplicate model files. Body/clothing geometry, materials, skin palette and lighting remain unchanged. Uniform head parts share center(0,1.88,-0.015). Pashmina and covered long hair share a1.34-1.72 quintic fit; lower chest drape stays anchored. Uncovered Straight/Curls scale height uniformly to avoid horizontal curl compression; lower horizontal width blends between1.4 and1.7 to fit around the torso. All deformed normals use the inverse-transpose Jacobian.

Final review:288 size/body-angle pairs,64 native48/64px pairs across four skin tones,43 variant/reset/mobile checks,108 fit invariant combinations,4 pointer/native-select/save/reset/orbit checks. Body/clothing unchanged; reference underside and true sphere radius checked; finite unit normals, exact drape anchors (horizontal anchors for uncovered long hair) and positive sampled pashmina clearance. Initial excessive hood flare and curl compression were refined before final captures.

This is a proportion exploration for selection, not a new catalogue default. Largest reductions may require further style-specific artistic fitting after selection. Portrait cameras stay matched for comparison; selected geometry/camera/color/depth must be baked together before native adoption. No profile/native/firmware changes or phone performance certification.

Local: http://127.0.0.1:9251/268/
Public: https://recdpz.github.io/ravedio-avatar-previews/268/
Tools: audit.cjs URL; check_fits.cjs URL; check_controls.cjs URL (existing Playwright/Chromium); create_review.py CAPTURE_DIR (Pillow). Intermediate captures stay outside the repo. Publish using tools/prepare-pages.py --externalize-images with separate main/gh-pages.
