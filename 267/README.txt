Ravedio267 - head size and floating-gap comparison

Current spherical head from266 versus5%,8%,10%,12% smaller heads. Extra upward lift is independently adjustable0-3% of the original0.96 head height; default1%=0.0096 world units. Current reference always uses100% size and zero lift. Body, clothing, studio and camera are matched.

Head/eyes/mouth/lashes/facial hair/caps/glasses use the same shared pivot(0,1.88,-0.015). Long feminine Straight/Curls blend from body-fitted lower hair(y<=1.46) into the scaled crown(y>=1.86). Pashmina lower wrap/chest drape(y<=1.46) stays in body coordinates and blends to the scaled hood(y>=1.80). Quintic smoothstep and the inverse-transpose Jacobian transport normals smoothly. No runtime physics, independent component centering or surface-normal recomputation from changed tessellation.

This is an interactive proportion exploration, not a new catalogue default or phone performance test. Existing266 ordinary GLBs are reused directly; no duplicate model files. Selected values can be downloaded with Save choices as Ravedio267-choices.json for later baking. No profile bytes or native/firmware changes. If a direction is adopted, final source/export fits and matched color/depth need baking together.

Reviewed288 body/angle/size pairs across nine looks,64 small-portrait pairs across four skin tones, extreme lifts, reset identity and controls at320/390/844px. Actual sphere radius scales correctly; body/clothing bounds and drape lower contacts are unchanged. Reset to100%/zero lift matches the current sphere pixel-for-pixel in the tested bare/pashmina looks.

Local: http://127.0.0.1:9251/267/
GitHub preview: https://recdpz.github.io/ravedio-avatar-previews/267/
Source shapes:266 from2a67abca3f2163624e534c09da617c334a18aa24. Reproduce captures with node tools/audit.cjs URL (existing Playwright/Chromium); create_review.py CAPTURE_DIR (Pillow). Capture intermediates remain outside the repository. Publish through tools/prepare-pages.py --externalize-images; keep full-art main and generated gh-pages separate.
