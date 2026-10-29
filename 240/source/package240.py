from pathlib import Path
import json,shutil,re,hashlib
P=Path(__file__).parent;R=P.parent/'floating138/mobile-preview';D=R/'240';OLD=R/'239'
for folder in ['','components','references','assemblies','source']:(D/folder).mkdir(exist_ok=True)
def remap(x):
 if isinstance(x,dict):return {k:remap(v) for k,v in x.items()}
 if isinstance(x,list):return [remap(v) for v in x]
 if isinstance(x,str) and x.startswith('components/'):return '../239/'+x
 return x
c=remap(json.loads((OLD/'catalogue239.json').read_text()));fits=json.loads((P/'fits240.json').read_text())
c['previousPashminaTops']=c['pashminaTops'];c['previousPashminaFits']={k:dict(v['pashmina']) for k,v in c['fits'].items()};c['pashminaTops']={}
for build,tops in fits.items():
 c['pashminaTops'][build]={}
 for top,item in tops.items():shutil.copy2(P/item['component'],D/item['component']);c['pashminaTops'][build][top]=item['component']
 for key,pairs in c['fits'].items():
  if key.startswith(build+'-'):pairs['pashmina']['headgear']=c['pashminaTops'][build]['open' if build=='Feminine' else 'tank']
(D/'catalogue240.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf8',newline='\n')
(D/'viewer240.js').write_text((OLD/'viewer239.js').read_text().replace('239','240'),encoding='utf8',newline='\n')
html=(OLD/'index.html').read_text().replace('239','240').replace('Compare238 pashmina','Compare239 pashmina')
html=re.sub(r'(<h1>Pashmina fit</h1>)<p>.*?</p>',r'\1<p>Narrower hanging ends reveal more of the tops. The approved hood, neck wrap and joins stay unchanged. Compare239 keeps the same outfit and view.</p>',html,count=1)
html=html.replace('Inner corners - close comparison','Narrower ends - matched comparison').replace('Matched Blender crops:238 on the left,240 on the right.','Matched Blender crops:239 on the left,240 on the right.').replace('<a href="../238/">Previous238</a>','<a href="../239/">Previous239</a>')
(D/'index.html').write_text(html,encoding='utf8',newline='\n')
for name in ['narrow240.py','verify240.py','package240.py','browser240.cjs','close240.cjs']:
 if (P/name).exists():shutil.copy2(P/name,D/'source'/name)
hair={k:dict(path=v['pashmina']['hair'],sha256=hashlib.sha256((D/v['pashmina']['hair']).resolve().read_bytes()).hexdigest(),validation='Exact239 covered hair; upper cloth and hair contact unchanged. Free-end width change only.') for k,v in c['fits'].items()}
(P/'hair240.json').write_text(json.dumps(hair,indent=2)+'\n',encoding='utf8')
print('PACKAGED240',sum(len(v) for v in fits.values()),'narrower end fits')
