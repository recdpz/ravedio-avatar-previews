from pathlib import Path
import json,shutil,re,hashlib
P=Path(__file__).parent;R=P.parent/'floating138/mobile-preview';D=R/'243';OLD=R/'242'
for folder in ['','components','references','assemblies','source']:(D/folder).mkdir(exist_ok=True)
def remap(x):
 if isinstance(x,dict):return {k:remap(v) for k,v in x.items()}
 if isinstance(x,list):return [remap(v) for v in x]
 if isinstance(x,str) and x.startswith('components/'):return '../242/'+x
 return x
c=remap(json.loads((OLD/'catalogue242.json').read_text()));fits=json.loads((P/'fits243.json').read_text())
c['previousPashminaTops']=c['pashminaTops'];c['previousPashminaFits']={k:dict(v['pashmina']) for k,v in c['fits'].items()};c['pashminaTops']={}
for build,tops in fits.items():
 c['pashminaTops'][build]={}
 for top,item in tops.items():shutil.copy2(P/item['component'],D/item['component']);c['pashminaTops'][build][top]=item['component']
 for key,pairs in c['fits'].items():
  if key.startswith(build+'-'):pairs['pashmina']['headgear']=c['pashminaTops'][build]['open' if build=='Feminine' else 'tank']
(D/'catalogue243.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf8',newline='\n')
(D/'viewer243.js').write_text((OLD/'viewer242.js').read_text().replace('242','243'),encoding='utf8',newline='\n')
html=(OLD/'index.html').read_text().replace('242','243').replace('Compare241 pashmina','Compare242 pashmina')
html=re.sub(r'(<h1>Pashmina fit</h1>)<p>.*?</p>',r'\1<p>A higher loose neck knot with outward-fanning ends that settle along the outer chest. Broad end widths and the continuous hood are retained. Compare242 keeps the same outfit and view.</p>',html,count=1)
html=html.replace('Matched Blender crops:241 on the left,243 on the right.','Matched Blender crops:242 on the left,243 on the right.').replace('<a href="../241/">Previous241</a>','<a href="../242/">Previous242</a>')
html=re.sub(r'<summary>Neck joins.*?</summary>','<summary>Higher knot and outward drape - comparison</summary>',html,count=1)
html=html.replace('Matched close views of both hood-to-fold joins','Matched close views of the slimmer chest wrap')
(D/'index.html').write_text(html,encoding='utf8',newline='\n')
for name in ['knot243.py','verify243.py','package243.py','browser243.cjs','close243.cjs']:
 if (P/name).exists():shutil.copy2(P/name,D/'source'/name)
hair={k:dict(path=v['pashmina']['hair'],sha256=hashlib.sha256((D/v['pashmina']['hair']).resolve().read_bytes()).hexdigest(),validation='Exact retained covered-hair component; fresh243 four-angle assembly review recorded separately.') for k,v in c['fits'].items()}
(P/'hair243.json').write_text(json.dumps(hair,indent=2)+'\n',encoding='utf8')
print('PACKAGED243',sum(len(v) for v in fits.values()),'higher loose-knot fits')
