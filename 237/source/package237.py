"""237 changes only the pashmina; all other236 component paths are retained."""
from pathlib import Path
import json,shutil
P=Path(__file__).parent;R=P.parent/'floating138/mobile-preview';D=R/'237';OLD=R/'236'
for folder in ['','components','references','assemblies','source']:(D/folder).mkdir(exist_ok=True)
def remap(obj):
    if isinstance(obj,dict):return {k:remap(v) for k,v in obj.items()}
    if isinstance(obj,list):return [remap(v) for v in obj]
    if isinstance(obj,str) and obj.startswith('components/'):return '../236/'+obj
    return obj
c=remap(json.loads((OLD/'catalogue236.json').read_text()));fits=json.loads((P/'fits237.json').read_text())
c['previousPashminaTops']=c['pashminaTops'];c['pashminaTops']={};c['previousPashminaFits']={key:dict(pairs['pashmina']) for key,pairs in c['fits'].items()}
for build,tops in fits.items():
    c['pashminaTops'][build]={}
    for top,item in tops.items():
        shutil.copy2(P/item['component'],D/item['component']);c['pashminaTops'][build][top]=item['component']
    default='open' if build=='Feminine' else 'tank'
    for key,pairs in c['fits'].items():
        if key.startswith(build+'-'):pairs['pashmina']['headgear']=c['pashminaTops'][build][default]
(D/'catalogue237.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf8',newline='\n')
js=(OLD/'viewer236.js').read_text().replace('236','237')
old="if(previousPashmina)Object.assign(p,catalogue.previousPashminaFits[b+'-'+s.hair]);else"
new="if(previousPashmina){Object.assign(p,catalogue.previousPashminaFits[b+'-'+s.hair]);p.headgear=catalogue.previousPashminaTops[b][s.top];}else"
assert old in js;js=js.replace(old,new,1)
(D/'viewer237.js').write_text(js,encoding='utf8',newline='\n')
html=(OLD/'index.html').read_text().replace('236','237').replace('Compare235 pashmina','Compare236 pashmina')
html=html.replace('Shoulder-seated folds, a continuous gathered nape, and two crossing ends.','One continuous neck wrap, with slightly narrower crossing ends.')
html=html.replace('<a href="../235/">Previous235</a>','<a href="../236/">Previous236</a>')
(D/'index.html').write_text(html,encoding='utf8',newline='\n')
for name in ['scarf237.py','verify237.py','package237.py','browser237.cjs','close237.cjs']:
    if (P/name).exists():shutil.copy2(P/name,D/'source'/name)
print('PACKAGED237',sum(len(v) for v in fits.values()),'wrap fits; all hair and other components retained')
