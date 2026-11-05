from pathlib import Path
import json,copy,shutil,re
P=Path(__file__).parent;W=P/'pass4';R=P.parent/'floating138/mobile-preview';OLD=R/'258';D=R/'259'
for folder in ['components','references','source','assemblies']:(D/folder).mkdir(parents=True,exist_ok=True)
def rebase(x):
 if isinstance(x,dict):return {('../258/'+k if k.startswith('components/') else k):rebase(v) for k,v in x.items()}
 if isinstance(x,list):return [rebase(v) for v in x]
 if isinstance(x,str) and x.startswith('components/'):return '../258/'+x
 return x
c=rebase(json.loads((OLD/'catalogue258.json').read_text()));c.pop('before257',None);c['before258']={k:copy.deepcopy(c[k]) for k in ['builds','fits','sprouts','pashminaVariants','pashminaHairFamilies','braidLengths','ombre','colors']}
notes={'taper':'Shorter rounded side banks; upper sweep retained. Curved directional fade detail uses214 as the reference.','sidepart':'Crop: crown-to-front flow with slight diagonal drift, varied rounded fringe clumps and shorter sides.','curly-top':'Retained curly crown with the same curved directional side treatment as Taper.'}
for st,r in json.loads((W/'hair259.json').read_text()).items():
 target='components/'+Path(r['path']).name;c['builds']['Masculine']['hair'][st].update(path=target,note=notes[st]);shutil.copy2(r['path'],D/target)
c['builds']['Masculine']['hair']['sidepart']['label']='Crop'
for name in ['fits','sprouts']:
 for key,row in json.loads((W/f'{name}259.json').read_text()).items():
  if name=='fits':style,hat=key.split('|');c['fits']['Masculine-'+style][hat]['hair']=row['hair'];path=row['hair']
  else:c['sprouts'][key]=row;path=row['path']
  shutil.copy2(W/path,D/path)
(D/'catalogue259.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf8',newline='\n')
s=(OLD/'viewer258.js').read_text().replace('258','259').replace('before257','before258').replace('hairShade259','hairShade258');(D/'viewer259.js').write_text(s,encoding='utf8',newline='\n')
s=(OLD/'index.html').read_text().replace('258','259').replace('Compare257','Compare258').replace('Previous257','Previous258').replace('href="../257/"','href="../258/"');s=re.sub('<h1>.*?</h1><p>.*?</p>','<h1>Shorter Taper · Crop</h1><p>Shorter Taper side locks with curved directional fade detail, plus a new forward-styled Crop. Compare258 shows the previous cuts; Crop replaces Side part.</p>',s,count=1)
s=re.sub(r'<a href="references/black-[^"]+">[^<]+</a>','',s);s=s.replace('<a href="references/artifact-comparison259.jpg">Flagged reflection before and after</a>','<a href="references/direction214-comparison259.jpg">214 directional reference</a>');s=s.replace('<figcaption>Side part</figcaption>','<figcaption>Crop</figcaption>').replace('Side part rotation check','Crop rotation check').replace('Side part before and after','Side part → Crop').replace('Side part with headgear','Crop with headgear').replace('Before and after / small portraits / covered fits / Black','Before and after / small portraits / covered fits').replace('<a href="references/small259.jpg">','<a href="references/colors259.jpg">Hair colors</a><a href="references/small259.jpg">')
(D/'index.html').write_text(s,encoding='utf8',newline='\n');print('PACKAGE259_READY')
