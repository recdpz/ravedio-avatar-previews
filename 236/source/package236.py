"""Small236 review retaining235 catalogue inputs by relative reference."""
from pathlib import Path
import json,shutil,re
P=Path(__file__).parent;R=P.parent/'floating138/mobile-preview';D=R/'236';OLD=R/'235'
D.mkdir(exist_ok=True)
for name in ['components','references','assemblies','source']:(D/name).mkdir(exist_ok=True)
def remap(obj):
    if isinstance(obj,dict):return {k:remap(v) for k,v in obj.items()}
    if isinstance(obj,list):return [remap(v) for v in obj]
    if isinstance(obj,str) and obj.startswith('components/'):return '../235/'+obj
    return obj
c=remap(json.loads((OLD/'catalogue235.json').read_text()))
fits=json.loads((P/'fits236.json').read_text());c['pashminaTops']={};c['previousPashminaFits']={}
for build,tops in fits.items():
    c['pashminaTops'][build]={}
    for top,item in tops.items():
        path=item['component'];shutil.copy2(P/path,D/path);c['pashminaTops'][build][top]=path
    default='open' if build=='Feminine' else 'tank'
    for key,pairs in c['fits'].items():
        if key.startswith(build+'-'):
            c['previousPashminaFits'][key]=dict(pairs['pashmina'])
            pairs['pashmina']['headgear']=c['pashminaTops'][build][default]
if (P/'hair236.json').exists():
    hair=json.loads((P/'hair236.json').read_text())
    for key,item in hair.items():
        if item.get('path'):
            shutil.copy2(P/item['path'],D/item['path']);c['fits'][key]['pashmina']['hair']=item['path']
(D/'catalogue236.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf8',newline='\n')
js=(OLD/'viewer235.js').read_text().replace('235','236')
js=js.replace("fetch('./face-palette209.json')","fetch('../235/face-palette209.json')")
js=js.replace("let showLashes=true;","let showLashes=true,previousPashmina=false;")
needle="if(s.glasses!=='none'){"
insert="if(s.headwear==='pashmina'){if(previousPashmina)Object.assign(p,catalogue.previousPashminaFits[b+'-'+s.hair]);else p.headgear=catalogue.pashminaTops[b][s.top];}"
assert needle in js;js=js.replace(needle,insert+needle,1)
js=js.replace("function state(){return {revision:236,","function state(){return {revision:236,previousPashmina,")
js=js.replace("$('show-lashes').onchange=", "$('previous').onchange=()=>{previousPashmina=$('previous').checked;load()};\n$('show-lashes').onchange=",1)
js=js.replace("headwear:'none',glasses:","headwear:'pashmina',glasses:",1)
js=js.replace("mode='face'","mode='body'",1)
(D/'viewer236.js').write_text(js,encoding='utf8',newline='\n')
html=(OLD/'index.html').read_text();prefix=html.split('<details open>')[0]
prefix=prefix.replace('235','236').replace('<h1>Hair and headwear</h1>','<h1>Pashmina fit</h1>')
prefix=re.sub(r'<p>Revised masculine hairstyles.*?</p>','<p>Shoulder-seated folds, a continuous gathered nape, and two crossing ends. Switch builds, tops and angles to inspect the fit.</p>',prefix,count=1)
prefix=prefix.replace('<div class="checks">','<div class="checks"><label><input id="previous" type="checkbox">Compare235 pashmina</label>',1)
prefix=prefix.replace('.checks{display:flex;gap:', '.checks{display:flex;flex-wrap:wrap;gap:')
prefix=prefix.replace('id="face" aria-pressed="true"','id="face" aria-pressed="false"').replace('id="body" aria-pressed="false"','id="body" aria-pressed="true"')
gallery='<details open><summary>Final export references · seven angles</summary>'
for build in ['Feminine','Masculine']:
    gallery+='<h3>'+build+'</h3><div class="shape-grid">'
    for angle,label in [('front','Front'),('threequarter','Three-quarter'),('profile','Left side'),('rightprofile','Right side'),('rear','Back'),('top','Above'),('underside','Underneath')]:
        gallery+=f'<figure><img src="references/{build}-pashmina236-{angle}.png" alt="{build} {label}" loading="lazy"><figcaption>{label}</figcaption></figure>'
    gallery+='</div>'
gallery+='</details><details><summary>Matched face references</summary><div class="shape-grid">'+''.join(f'<figure><img id="compare-{eye}" alt="{eye} face reference"><figcaption>{label}</figcaption></figure>' for eye,label in [('original','Original'),('almond','Almond'),('tapered','Tapered oval'),('hooded','Soft hooded'),('bean','Rounded bean'),('squint','Curved squint')])+'</div></details>'
tail=html[html.index('<script type="importmap">'):].replace('viewer235.js','viewer236.js')
(D/'index.html').write_text(prefix+gallery+'<nav><a href="handoff236.json">Rendering handoff</a><a href="../235/">Previous235</a></nav><p class="small">Fixed3D lighting. Shared coordinates and separate feature/color controls. This is an artwork correction; native rendering and phone performance remain separate.</p></main>'+tail,encoding='utf8',newline='\n')
for name in ['scarf236.py','verify236.py','package236.py']:
    if (P/name).exists():shutil.copy2(P/name,D/'source'/name)
print('Packaged236 viewer and',sum(len(v) for v in fits.values()),'top-specific pashmina fits')
