from pathlib import Path
import json,shutil,subprocess,sys
P=Path(__file__).parent;R=P.parent/'floating138/mobile-preview';D=R/'234'
for d in ['components','references','source']:(D/d).mkdir(parents=True,exist_ok=True)
for f in (P/'output/components').glob('*.glb'):shutil.copy2(f,D/'components'/f.name)
for f in (P/'output/renders').glob('*.png'):
 if '-export-' in f.name or '-before-' in f.name or f.name.startswith('Masculine-'):shutil.copy2(f,D/'references'/f.name)
for f in (P/'output/portraits').glob('*.png'):shutil.copy2(f,D/'references'/f.name)
subprocess.run([sys.executable,str(P/'catalogue234.py')],check=True)
old=(R/'227/viewer227.js').read_text(encoding='utf8');studio=old[old.index('const renderer='):old.index('function component(')]
head="import * as THREE from 'three';\nimport {GLTFLoader} from '../227/vendor/loaders/GLTFLoader.js';\nconst $=id=>document.getElementById(id),hero=$('hero'),catalogue=await(await fetch('./catalogue234.json')).json(),palette=await(await fetch('./face-palette209.json')).json();\n"
(D/'viewer234.js').write_text(head+studio+(P/'controls234.js').read_text(encoding='utf8'),encoding='utf8')
html=(R/'233/index.html').read_text(encoding='utf8').replace('233','234')
html=html.replace('<h1>Compare eye shapes</h1>','<h1>Feminine eyelashes</h1>')
start=html.index('<h1>');a=html.index('<p>',start);b=html.index('</p>',a)+4
html=html[:a]+'<p>Fitted lashes for each feminine eye shape. Toggle Lashes to compare. Both builds now use no nose and the regular smile.</p>'+html[b:]
html=html.replace('<label><input id="show-lenses" type="checkbox" checked>Lenses</label>','<label><input id="show-lenses" type="checkbox" checked>Lenses</label><label id="lash-toggle"><input id="show-lashes" type="checkbox" checked>Lashes</label>')
html=html.replace('<div class="checks"><label><input id="before232" type="checkbox">Show previous 232</label></div>','')
html=html.replace('<label>Nose<select id="nose"></select></label>','<select id="nose" hidden aria-label="No nose"></select>').replace('<label>Mouth<select id="mouth"></select></label>','<select id="mouth" hidden aria-label="Regular smile"></select>')
html=html.replace('<h2>Face</h2>','<h2>Face</h2><p class="small">No nose · Regular smile</p>')
start=html.index('<div class="eye-picks"');end=html.index('</div>',start)+6
labels=[('original','Original'),('almond','Almond'),('tapered','Tapered oval'),('hooded','Soft hooded'),('bean','Rounded bean'),('squint','Curved squint')]
html=html[:start]+'<div class="eye-picks" aria-label="Eye shape">'+''.join(f'<button data-eye="{k}" aria-pressed="false">{l}</button>' for k,l in labels)+'</div>'+html[end:]
old_note='The before toggle works for Tapered oval and Rounded bean. Original, Almond, Soft hooded and Curved squint retain their232 versions. Round and Soft square remain removed.'
html=html.replace(old_note,'Lashes are a feminine comparison candidate and use the same fitted eye shapes. Curved squint remains undecided. Round and Soft square remain removed.')
start=html.index('<details');end=html.index('</details>',start)+10
detail='<details open><summary>Matched face references</summary><p class="small">Fixed Blender references in Light warm, with the retained hairstyle and outfit. Feminine references show lashes. Use the live viewer to change skin, features and angles.</p><div class="shape-grid">'+''.join(f'<figure><img id="compare-{k}" alt="{l} face reference"><figcaption>{l}</figcaption></figure>' for k,l in labels)+'</div></details>'
html=html[:start]+detail+html[end:]
html=html.replace('repeat(5,1fr)','repeat(3,1fr)')
html=html.replace('</style>','[hidden]{display:none!important}</style>')
html=html.replace('<nav>','<nav><a href="../233/">Approved eye contours · 233</a>')
(D/'index.html').write_text(html,encoding='utf8')
for name in ['lashes234.py','catalogue234.py','controls234.js','package234.py']:shutil.copy2(P/name,D/'source'/name)
print('PACKAGED234')
