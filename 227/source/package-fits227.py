from pathlib import Path
import json,shutil
P=Path(__file__).parent;O=P/'revision227';R=P.parent/'floating138/mobile-preview';D=R/'227'
fits=json.loads((O/'fit-proof.json').read_text());looks=json.loads((D/'looks227.json').read_text());base=json.loads((R/'224/looks224.json').read_text());config={}
(D/'fit-review').mkdir(exist_ok=True)
for key,record in fits.items():
 for hat,item in record['combinations'].items():
  components=dict(looks[key]['components']);path=item.get('specific_component') or (record['component'] if item['covered_variant'] else None)
  if path:shutil.copy2(O/path,D/path);components['hair']=path
  if hat=='cap':
   donor='Feminine-cap' if key.startswith('Feminine') else 'Masculine-details';components['headgear']='../224/'+base[donor]['components']['headgear'].removeprefix('./')
  else:components['headgear']=looks['Feminine-'+hat]['components']['headgear']
  name=key+'--'+hat
  for f in (O/'fit-review').glob(name+'-*.png'):shutil.copy2(f,D/'fit-review'/f.name)
  config[name]={'label':looks[key]['label']+' + '+hat,'components':components,'build':looks[key]['build'],'note':'Static authored fit. Uncovered hair remains separate. '+record['context']+'. Owner acceptance and native-app qualification pending.','fit':True}
(D/'fits227.json').write_text(json.dumps(config,indent=2)+'\n')
js=(D/'viewer227.js').read_text().replace('looks227.json','fits227.json').replace("key='Feminine-straight'","key='Feminine-straight--cap'")
start=js.index('function reference()');end=js.index('\nasync function load()',start)
js=js[:start]+'''function reference(){const shown=['front','profile','rear','top'].includes(angle)?angle:angle==='rightprofile'?'profile':'front';$('native').src='fit-review/'+key+'-'+shown+'.png';$('native-label').textContent='Blender fit reference: '+shown+' view, Light warm tone. Other live angles remain freely rotatable.';$('case-note').textContent=config[key].note;}'''+js[end:]
js=js.replace("Object.entries(config).map(([id,c])=>new Option(c.label,id))","Object.entries(config).filter(([id,c])=>id.endsWith('--cap')).map(([id,c])=>new Option(c.label.split(' + ')[0],id.split('--')[0]))")
js=js.replace("$('look').value=key","$('look').value=key.split('--')[0]")
js=js.replace("$('look').onchange=()=>{key=$('look').value;load()}","$('look').onchange=()=>{key=$('look').value+'--'+$('headwear').value;load()};$('headwear').onchange=()=>{key=$('look').value+'--'+$('headwear').value;load()}")
js=js.replace('window.review227=',"$('headwear').value=key.split('--')[1];window.review227=")
(D/'fit-viewer227.js').write_text(js)
html=(D/'index.html').read_text().replace('Hair and accessory corrections','Hair and headwear fit review').replace('viewer227.js','fit-viewer227.js').replace('<label>Skin<select', '<label>Headwear<select id="headwear">'+''.join('<option value="'+x+'">'+label+'</option>' for x,label in [('cap','Cap'),('beanie','Beanie'),('bucket','Bucket hat'),('cowboy','Cowboy hat'),('headband','Headband'),('ears','Animal ears'),('pashmina','Pashmina')])+'</select></label><label>Skin<select')
html=html.replace('<details><summary>Earlier rejected draft, matched angle</summary><img id="before" alt="Previous226 construction draft"></details>','')
html=html.replace('<nav>','<nav><a href="index.html">Individual components</a>')
(D/'fits.html').write_text(html)
index=(D/'index.html').read_text();index=index.replace('<nav>','<nav><a href="fits.html">Hair and headwear combinations</a>');(D/'index.html').write_text(index)
print('FIT VIEWER227',len(config))
