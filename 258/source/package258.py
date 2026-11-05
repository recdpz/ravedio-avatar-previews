from pathlib import Path
import json,copy,shutil,re
P=Path(__file__).parent;W=P/'pass4';R=P.parent/'floating138/mobile-preview';OLD=R/'257';D=R/'258'
for d in [D/'components',D/'references',D/'source',D/'assemblies',P/'browser-final',P/'sources-final']:d.mkdir(parents=True,exist_ok=True)
def rebase(x):
 if isinstance(x,dict):return {('../257/'+k if k.startswith('components/') else k):rebase(v) for k,v in x.items()}
 if isinstance(x,list):return [rebase(v) for v in x]
 if isinstance(x,str) and x.startswith('components/'):return '../257/'+x
 return x
c=rebase(json.loads((OLD/'catalogue257.json').read_text()));c.pop('before256',None);c['before257']={k:copy.deepcopy(c[k]) for k in ['builds','fits','sprouts','pashminaVariants','pashminaHairFamilies','braidLengths','ombre','colors']}
for color in c['colors']['hair']:
 if color[0]=='black':color[2]='#303030'
notes={'taper':'Lower neat combed sweep, rounded back locks and clean faded sides.','sidepart':'Opposite relaxed diagonal sweep with a softer forward curve and restrained wave variation.','curly-top':'Retained curly crown with clearer short directional detail and a smoother low-glare fade.'}
for st,r in json.loads((W/'hair258.json').read_text()).items():
 target='components/'+Path(r['path']).name;c['builds']['Masculine']['hair'][st]['path']=target;c['builds']['Masculine']['hair'][st]['note']=notes[st];shutil.copy2(r['path'],D/target)
for name in ['fits','sprouts']:
 if not (W/f'{name}258.json').exists():continue
 for key,r in json.loads((W/f'{name}258.json').read_text()).items():
  if name=='fits':st,hat=key.split('|');c['fits']['Masculine-'+st][hat]['hair']=r['hair'];path=r['hair']
  else:c['sprouts'][key]=r;path=r['path']
  shutil.copy2(W/path,D/path)
(D/'catalogue258.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf8',newline='\n')
s=(OLD/'viewer257.js').read_text().replace('257','258').replace('before256','before257')
s=s.replace("catalogue.colors[f].find", "(previousPashmina?catalogue.before257.colors:catalogue.colors)[f].find")
s=s.replace("m.color.copy(hair).multiplyScalar(slot==='groom'?.82:1.0)","m.color.copy(hair).multiplyScalar((slot==='groom'?.82:1.0)*(m.userData.hairShade258??1))")
(D/'viewer258.js').write_text(s,encoding='utf8',newline='\n')
s=(OLD/'index.html').read_text().replace('257','258').replace('Compare256','Compare257').replace('Previous256','Previous257').replace('href="../256/"','href="../257/"').replace('#192586','#192566')
s=re.sub('<h1>.*?</h1><p>.*?</p>','<h1>Lower Taper · Relaxed Side part</h1><p>A lower, neatly combed Taper and a distinct opposite Side part sweep. Cleaner rounded back locks, clearer fade direction and neutral Black. Compare257 shows the previous shapes and purple-biased Black.</p>',s,count=1)
s=s.replace('Compare B original fade (bare Taper)','Original raised top (bare Taper)');(D/'index.html').write_text(s,encoding='utf8',newline='\n');print('PACKAGE258_READY')
