from pathlib import Path
import json,copy,shutil,re
P=Path(__file__).parent;W=P/'pass3';R=P.parent/'floating138/mobile-preview';OLD=R/'256';D=R/'257'
for x in [D/'components',D/'references',D/'source',D/'assemblies',P/'browser-verified',P/'sources']:x.mkdir(parents=True,exist_ok=True)
def rebase(x):
 if isinstance(x,dict):return {('../256/'+k if k.startswith('components/') else k):rebase(v) for k,v in x.items()}
 if isinstance(x,list):return [rebase(v) for v in x]
 if isinstance(x,str) and x.startswith('components/'):return '../256/'+x
 return x
c=rebase(json.loads((OLD/'catalogue256.json').read_text()));c.pop('before254',None);c['before256']={k:copy.deepcopy(c[k]) for k in ['builds','fits','sprouts','pashminaVariants','pashminaHairFamilies','braidLengths','ombre']}
for st,r in json.loads((W/'hair257.json').read_text()).items():
 target='components/'+Path(r['path']).name;c['builds']['Masculine']['hair'][st]['path']=target;c['builds']['Masculine']['hair'][st]['note']='B shape with thinned, blended terminal locks and a smooth fade with fine sculpted direction.' if st=='taper' else 'Retained curly crown with the same smooth gradient and short sculpted side detail.';shutil.copy2(r['path'],D/target)
for name in ['fits','sprouts']:
 if not (W/f'{name}257.json').exists():continue
 for key,r in json.loads((W/f'{name}257.json').read_text()).items():
  if name=='fits':st,hat=key.split('|');c['fits']['Masculine-'+st][hat]['hair']=r['hair'];path=r['hair']
  else:c['sprouts'][key]=r;path=r['path']
  shutil.copy2(W/path,D/path)
(D/'catalogue257.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf8',newline='\n')
s=(OLD/'viewer256.js').read_text().replace('256','257').replace('before254','before256');(D/'viewer257.js').write_text(s,encoding='utf8',newline='\n')
s=(OLD/'index.html').read_text().replace('256','257').replace('Compare254','Compare256').replace('Previous254','Previous256').replace('href="../254/"','href="../256/"')
s=re.sub('<h1>.*?</h1><p>.*?</p>','<h1>B shape · Blended taper</h1><p>B’s swept shape with thinner, softly blended lower lock ends. Smooth faded sides and small sculpted directional marks borrow214’s approach. Compare256 shows the previous textured fade.</p>',s,count=1)
(D/'index.html').write_text(s,encoding='utf8',newline='\n');print('PACKAGE257_READY')
