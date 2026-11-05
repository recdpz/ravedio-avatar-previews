from pathlib import Path
import json,shutil,re
P=Path(__file__).parent;R=P.parent/'floating138/mobile-preview';D=R/'245';OLD=R/'244'
for folder in ['','components','references','assemblies','source']:(D/folder).mkdir(exist_ok=True)
def remap(x):
 if isinstance(x,dict):return {k:remap(v) for k,v in x.items()}
 if isinstance(x,list):return [remap(v) for v in x]
 if isinstance(x,str) and x.startswith('components/'):return '../244/'+x
 return x
c=remap(json.loads((OLD/'catalogue244.json').read_text()));fits=json.loads((P/'fits245.json').read_text())
c['previousPashminaTops']=c['pashminaTops'];c['previousPashminaFits']={k:dict(v['pashmina']) for k,v in c['fits'].items()};c['pashminaTops']={}
for build,tops in fits.items():
 c['pashminaTops'][build]={}
 for top,item in tops.items():shutil.copy2(P/item['component'],D/item['component']);c['pashminaTops'][build][top]=item['component']
 for key,pairs in c['fits'].items():
  if key.startswith(build+'-'):pairs['pashmina']['headgear']=c['pashminaTops'][build]['open' if build=='Feminine' else 'tank']
(D/'catalogue245.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf8',newline='\n')
(D/'viewer245.js').write_text((OLD/'viewer244.js').read_text().replace('244','245'),encoding='utf8',newline='\n')
html=(OLD/'index.html').read_text().replace('244','245').replace('Compare243','Compare244').replace('Previous243','Previous244').replace('href="../243/"','href="../244/"').replace('Matched Blender crops:243','Matched Blender crops:244')
html=re.sub(r'(<h1>Pashmina fit</h1>)<p>.*?</p>',r'\1<p>A simple overlap in the same high position, with the knot-like tuck removed. Clean neck edges and outward-falling ends stay in place. Compare244 keeps the same outfit and view.</p>',html,count=1)
html=re.sub(r'<summary>Higher knot.*?</summary>','<summary>Plain crossing - same placement</summary>',html,count=1)
(D/'index.html').write_text(html,encoding='utf8',newline='\n')
for name in ['cross245.py','verify245.py','package245.py','browser245.cjs','close245.cjs']:shutil.copy2(P/name,D/'source'/name)
print('PACKAGED245',sum(len(v) for v in fits.values()),'plain crossing fits')
