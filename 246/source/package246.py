from pathlib import Path
import json,shutil,re
P=Path(__file__).parent;R=P.parent/'floating138/mobile-preview';D=R/'246';OLD=R/'245'
for folder in ['','components','references','assemblies','source']:(D/folder).mkdir(exist_ok=True)
def remap(x):
 if isinstance(x,dict):return {k:remap(v) for k,v in x.items()}
 if isinstance(x,list):return [remap(v) for v in x]
 if isinstance(x,str) and x.startswith('components/'):return '../245/'+x
 return x
c=remap(json.loads((OLD/'catalogue245.json').read_text()));fits=json.loads((P/'fits246.json').read_text())
c['previousPashminaTops']=c['pashminaTops'];c['previousPashminaFits']={k:dict(v['pashmina']) for k,v in c['fits'].items()};c['pashminaTops']={}
for build,tops in fits.items():
 c['pashminaTops'][build]={}
 for top,item in tops.items():shutil.copy2(P/item['component'],D/item['component']);c['pashminaTops'][build][top]=item['component']
 for key,pairs in c['fits'].items():
  if key.startswith(build+'-'):pairs['pashmina']['headgear']=c['pashminaTops'][build]['open' if build=='Feminine' else 'tank']
(D/'catalogue246.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf8',newline='\n')
(D/'viewer246.js').write_text((OLD/'viewer245.js').read_text().replace('245','246'),encoding='utf8',newline='\n')
html=(OLD/'index.html').read_text().replace('245','246').replace('Compare244','Compare245').replace('Previous244','Previous245').replace('href="../244/"','href="../245/"').replace('Matched Blender crops:244','Matched Blender crops:245')
html=re.sub(r'(<h1>Pashmina fit</h1>)<p>.*?</p>',r'\1<p>Cleaner upper fabric strips with consistent width and smoother edges, at the same high placement. The hanging ends and neck wrap stay fixed. Compare245 keeps the same outfit and view.</p>',html,count=1)
html=html.replace('Plain crossing - same placement','Upper fabric strips - matched comparison')
(D/'index.html').write_text(html,encoding='utf8',newline='\n')
for name in ['ribbons246.py','verify246.py','package246.py','browser246.cjs','close246.cjs']:shutil.copy2(P/name,D/'source'/name)
print('PACKAGED246',sum(len(v) for v in fits.values()),'rebuilt ribbon fits')
