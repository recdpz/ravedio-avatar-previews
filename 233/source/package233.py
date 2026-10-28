from pathlib import Path
import json,shutil,subprocess,sys
P=Path(__file__).parent;R=P.parent/'floating138/mobile-preview';D=R/'233'
for d in ['components','references','source']:(D/d).mkdir(parents=True,exist_ok=True)
for f in (P/'output/components').glob('*.glb'):shutil.copy2(f,D/'components'/f.name)
for f in (P/'output/renders').glob('*.png'):
 if '-export-' in f.name or '-original-' in f.name:shutil.copy2(f,D/'references'/f.name)
for f in (P/'output/portraits').glob('*.png'):shutil.copy2(f,D/'references'/f.name)
subprocess.run([sys.executable,str(P/'catalogue233.py')],check=True)
old=(R/'227/viewer227.js').read_text(encoding='utf8');studio=old[old.index('const renderer='):old.index('function component(')]
head="import * as THREE from 'three';\nimport {GLTFLoader} from '../227/vendor/loaders/GLTFLoader.js';\nconst $=id=>document.getElementById(id),hero=$('hero'),catalogue=await(await fetch('./catalogue233.json')).json(),palette=await(await fetch('./face-palette209.json')).json();\n"
(D/'viewer233.js').write_text(head+studio+(P/'controls233.js').read_text(encoding='utf8'),encoding='utf8')
html=(R/'228/index.html').read_text(encoding='utf8').replace('228','233')
html=html.replace('<h1>Build your avatar</h1>','<h1>Compare eye shapes</h1>').replace('Choose each feature independently. Your choices are remembered separately for each build.','Tapered oval has a clearer outer taper. Rounded bean has a fuller upper curve and a broader lower bend. Compare either with 232 in the same view.')
buttons='<div class="eye-picks" aria-label="Compare eye shapes">'+''.join(f'<button data-eye="{k}" aria-pressed="false">{label}</button>' for k,label in [('original','Original'),('tapered','Tapered oval'),('hooded','Soft hooded'),('bean','Rounded bean'),('squint','Curved squint')])+'</div>'
html=html.replace('<p id="status"',buttons+'<div class="checks"><label><input id="before232" type="checkbox">Show previous 232</label></div><p id="status"')
html=html.replace('Curved squint is an additional eye candidate with curved upper and lower edges. The existing four eye shapes remain available.','The before toggle works for Tapered oval and Rounded bean. Original, Almond, Soft hooded and Curved squint retain their232 versions. Round and Soft square remain removed.')
start=html.index('<details>');end=html.index('</details>',start)+len('</details>')
compare='<details open><summary>Matched shape comparison</summary><p class="small">Blender references on the retained224 outfit and hair, in Light warm. Select a build above to compare its five front portraits. The live viewer lets you rotate and change skin tone.</p><div class="shape-grid">'+''.join(f'<figure><img id="compare-{k}" alt="{label} eye comparison"><figcaption>{label}</figcaption></figure>' for k,label in [('original','Original'),('tapered','Tapered oval'),('hooded','Soft hooded'),('bean','Rounded bean'),('squint','Curved squint')])+'</div></details>'
html=html[:start]+compare+html[end:]
html=html.replace('</style>','.eye-picks{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0}.eye-picks button{font-size:12px;padding:7px}.shape-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:12px}.shape-grid figure{margin:10px 0}.shape-grid img{width:100%;border-radius:10px}.shape-grid figcaption{font-size:13px}@media(max-width:720px){.shape-grid{grid-template-columns:repeat(2,1fr)}}\n</style>')
html=html.replace('</details>', '<h2>Before · 232</h2><div class="shape-grid" style="grid-template-columns:repeat(2,1fr);max-width:600px"><figure><img id="before-tapered" alt="Tapered oval before232"><figcaption>Tapered oval · before</figcaption></figure><figure><img id="before-bean" alt="Rounded bean before232"><figcaption>Rounded bean · before</figcaption></figure></div><h2>Flat outline check</h2><img src="references/outlines233.svg" alt="Flat outlines of tapered oval and rounded bean before and after" style="width:100%;max-width:800px;border-radius:10px"></details>')
html=html.replace('<nav>','<nav><a href="../232/">Previous 232</a>')
shutil.copy2(P/'output/outlines233.svg',D/'references/outlines233.svg')
(D/'index.html').write_text(html,encoding='utf8')
for name in ['eyes233.py','catalogue233.py','controls233.js','package233.py']:shutil.copy2(P/name,D/'source'/name)
print('PACKAGED233')
