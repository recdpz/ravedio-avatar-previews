from pathlib import Path
import json,shutil
P=Path(__file__).parent;R=P.parent/'floating138/mobile-preview';D=R/'238';OLD=R/'237'
for folder in ['','components','references','assemblies','source']:(D/folder).mkdir(exist_ok=True)
def remap(obj):
    if isinstance(obj,dict):return {k:remap(v) for k,v in obj.items()}
    if isinstance(obj,list):return [remap(v) for v in obj]
    if isinstance(obj,str) and obj.startswith('components/'):return '../237/'+obj
    return obj
c=remap(json.loads((OLD/'catalogue237.json').read_text()));fits=json.loads((P/'fits238.json').read_text())
c['previousPashminaTops']=c['pashminaTops'];c['pashminaTops']={};c['previousPashminaFits']={key:dict(pairs['pashmina']) for key,pairs in c['fits'].items()}
for build,tops in fits.items():
    c['pashminaTops'][build]={}
    for top,item in tops.items():
        shutil.copy2(P/item['component'],D/item['component']);c['pashminaTops'][build][top]=item['component']
    for key,pairs in c['fits'].items():
        if key.startswith(build+'-'):pairs['pashmina']['headgear']=c['pashminaTops'][build]['open' if build=='Feminine' else 'tank']
(D/'catalogue238.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf8',newline='\n')
(D/'viewer238.js').write_text((OLD/'viewer237.js').read_text().replace('237','238'),encoding='utf8',newline='\n')
html=(OLD/'index.html').read_text().replace('237','238').replace('Compare236 pashmina','Compare237 pashmina')
html=html.replace('One continuous neck wrap, with slightly narrower crossing ends.','Repaired joins between the hood and neck folds. Compare237 keeps the same outfit and view.')
html=html.replace('<a href="../236/">Previous236</a>','<a href="../237/">Previous237</a>')
html=html.replace('<details open>','<details open><summary>Neck joins · close comparison</summary><p class="small">Matched Blender crops:237 on the left,238 on the right. Same camera and outfit.</p><img src="references/junction-comparison238.png" alt="Matched close views of both hood-to-fold joins" style="width:100%;max-width:900px;border-radius:10px"></details><details open>',1)
(D/'index.html').write_text(html,encoding='utf8',newline='\n')
for name in ['scarf238.py','joined238.py','verify238.py','package238.py','browser238.cjs','close238.cjs']:
    if (P/name).exists():shutil.copy2(P/name,D/'source'/name)
print('PACKAGED238',sum(len(v) for v in fits.values()),'joined wrap fits')
