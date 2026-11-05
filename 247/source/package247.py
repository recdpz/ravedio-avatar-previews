from pathlib import Path
import json,shutil,re
P=Path(__file__).parent;R=P.parent/'floating138/mobile-preview';D=R/'247';OLD=R/'246'
for folder in ['','components','references','assemblies','source']:(D/folder).mkdir(exist_ok=True)
def remap(x):
 if isinstance(x,dict):return {k:remap(v) for k,v in x.items()}
 if isinstance(x,list):return [remap(v) for v in x]
 if isinstance(x,str) and x.startswith('components/'):return '../246/'+x
 return x
c=remap(json.loads((OLD/'catalogue246.json').read_text()));fits=json.loads((P/'fits247.json').read_text())
c['previousPashminaTops']=c['pashminaTops'];c['previousPashminaFits']={k:dict(v['pashmina']) for k,v in c['fits'].items()};c['pashminaTops']={}
for build,tops in fits.items():
 c['pashminaTops'][build]={}
 for top,item in tops.items():shutil.copy2(P/item['component'],D/item['component']);c['pashminaTops'][build][top]=item['component']
 for key,pairs in c['fits'].items():
  if key.startswith(build+'-'):pairs['pashmina']['headgear']=c['pashminaTops'][build]['open' if build=='Feminine' else 'tank']
(D/'catalogue247.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf8',newline='\n')
(D/'viewer247.js').write_text((OLD/'viewer246.js').read_text().replace('246','247'),encoding='utf8',newline='\n')
html=(OLD/'index.html').read_text().replace('246','247').replace('Compare245','Compare246').replace('Previous245','Previous246').replace('href="../245/"','href="../246/"').replace('Matched Blender crops:245','Matched Blender crops:246')
html=re.sub(r'(<h1>Pashmina fit</h1>)<p>.*?</p>',r'\1<p>Cleaner small upper joins beneath the chin, flowing into the accepted246 crossing. The main strips, placement and hanging ends stay fixed. Compare246 keeps the same outfit and view.</p>',html,count=1)
html=html.replace('Upper fabric strips - matched comparison','Upper neck joins - matched comparison')
(D/'index.html').write_text(html,encoding='utf8',newline='\n')
for name in ['roots247.py','verify247.py','package247.py','browser247.cjs','close247.cjs']:shutil.copy2(P/name,D/'source'/name)
print('PACKAGED247',sum(len(v) for v in fits.values()),'upper-join fits')
