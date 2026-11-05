from pathlib import Path
import json,shutil,subprocess,sys
P=Path(__file__).parent;R=P.parent/'floating138/mobile-preview';D=R/'232'
for d in ['components','references','source']:(D/d).mkdir(parents=True,exist_ok=True)
for f in (P/'output/components').glob('*.glb'):shutil.copy2(f,D/'components'/f.name)
for f in (P/'output/renders').glob('*.png'):
 if '-export-' in f.name or '-original-' in f.name:shutil.copy2(f,D/'references'/f.name)
for f in (P/'output/portraits').glob('*.png'):shutil.copy2(f,D/'references'/f.name)
subprocess.run([sys.executable,str(P/'catalogue232.py')],check=True)
old=(R/'227/viewer227.js').read_text(encoding='utf8');studio=old[old.index('const renderer='):old.index('function component(')]
head="import * as THREE from 'three';\nimport {GLTFLoader} from '../227/vendor/loaders/GLTFLoader.js';\nconst $=id=>document.getElementById(id),hero=$('hero'),catalogue=await(await fetch('./catalogue232.json')).json(),palette=await(await fetch('./face-palette209.json')).json();\n"
(D/'viewer232.js').write_text(head+studio+(P/'controls232.js').read_text(encoding='utf8'),encoding='utf8')
html=(R/'228/index.html').read_text(encoding='utf8').replace('228','232')
html=html.replace('<h1>Build your avatar</h1>','<h1>Compare eye shapes</h1>').replace('Choose each feature independently. Your choices are remembered separately for each build.','Tapered oval, Soft hooded and Rounded bean are retained. Curved squint has a fuller, more open outline. Switch shapes on either build.')
buttons='<div class="eye-picks" aria-label="Compare eye shapes">'+''.join(f'<button data-eye="{k}" aria-pressed="false">{label}</button>' for k,label in [('original','Original'),('tapered','Tapered oval'),('hooded','Soft hooded'),('bean','Rounded bean'),('squint','Curved squint')])+'</div>'
html=html.replace('<p id="status"',buttons+'<p id="status"')
html=html.replace('Curved squint is an additional eye candidate with curved upper and lower edges. The existing four eye shapes remain available.','Round and Soft square have been removed from this selector. Almond remains available in Eye shape. Curved squint is still under review.')
start=html.index('<details>');end=html.index('</details>',start)+len('</details>')
compare='<details open><summary>Matched shape comparison</summary><p class="small">Blender references on the retained224 outfit and hair, in Light warm. Select a build above to compare its five front portraits. The live viewer lets you rotate and change skin tone.</p><div class="shape-grid">'+''.join(f'<figure><img id="compare-{k}" alt="{label} eye comparison"><figcaption>{label}</figcaption></figure>' for k,label in [('original','Original'),('tapered','Tapered oval'),('hooded','Soft hooded'),('bean','Rounded bean'),('squint','Curved squint')])+'</div></details>'
html=html[:start]+compare+html[end:]
html=html.replace('</style>','.eye-picks{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0}.eye-picks button{font-size:12px;padding:7px}.shape-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:12px}.shape-grid figure{margin:10px 0}.shape-grid img{width:100%;border-radius:10px}.shape-grid figcaption{font-size:13px}@media(max-width:720px){.shape-grid{grid-template-columns:repeat(2,1fr)}}\n</style>')
html=html.replace('</details>', '<div class="squint-history"><p class="small">Previous Curved squint · 228</p><img id="compare-before" alt="Previous curved squint" style="max-width:220px;width:100%;border-radius:10px"></div></details>');html=html.replace('<nav>','<nav><a href="../231/">Previous 231</a><a href="../228/">Earlier shapes · 228</a>')
(D/'index.html').write_text(html,encoding='utf8')
for name in ['eyes232.py','catalogue232.py','controls232.js','package232.py']:shutil.copy2(P/name,D/'source'/name)
print('PACKAGED232')
