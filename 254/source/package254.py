from pathlib import Path
import json,copy,re,shutil
P=Path('E:/Ravedio-Avatar/catalogue254');R=P.parent/'floating138/mobile-preview';OLD=R/'253';D=R/'254'
def rebase(x):
 if isinstance(x,dict):return {k:rebase(v) for k,v in x.items()}
 if isinstance(x,list):return [rebase(v) for v in x]
 if isinstance(x,str) and x.startswith('components/'):return '../253/'+x
 return x
c=rebase(json.loads((OLD/'catalogue253.json').read_text()));c.pop('before252',None);c['before253']={k:copy.deepcopy(c[k]) for k in ['builds','fits','sprouts','pashminaVariants','pashminaHairFamilies','braidLengths','ombre']}
for st,r in json.loads((P/'hair254.json').read_text()).items():
 if st not in ['taper','curly-top']:continue
 c['builds']['Masculine']['hair'][st]['path']=r['path'];c['builds']['Masculine']['hair'][st]['note']='Clean directional clipped hair, graduated groom thickness and a connected longer top.' if st!='buzz' else 'Near-bald clipped hair with a clean bounded hairline and directional coverage.';shutil.copy2(P/r['path'],D/r['path'])
if (P/'fits254.json').exists():
 for key,r in json.loads((P/'fits254.json').read_text()).items():
  st,hat=key.split('|');c['fits']['Masculine-'+st][hat]['hair']=r['hair'];shutil.copy2(P/r['hair'],D/r['hair'])
if (P/'sprouts254.json').exists():
 for key,r in json.loads((P/'sprouts254.json').read_text()).items():
  c['sprouts'][key]=r;shutil.copy2(P/r['path'],D/r['path'])
(D/'catalogue254.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf8',newline='\n')
s=(OLD/'viewer253.js').read_text().replace('253','254').replace('before252','before253').replace("hairColor:'ombre'","hairColor:'default'");(D/'viewer254.js').write_text(s,encoding='utf8',newline='\n')
s=(OLD/'index.html').read_text().replace('253','254').replace('Compare252','Compare253').replace('Previous252','Previous253').replace('href="../252/"','href="../253/"');s=re.sub('<h1>.*?</h1><p>.*?</p>','<h1>Clean tapered sides</h1><p>Directional clipped hair, a graduated side shape and smoother transitions into the longer top. Compare253 shows the previous construction. Select every feature independently, rotate and zoom.</p>',s,count=1);a=s.index('<details open><summary>');b=s.index('<details><summary>Matched face references',a);s=s[:a]+'<details open><summary>Final exported angle checks</summary><div class="shape-grid">'+''.join('<figure><a href="references/'+st+'-angles254.jpg"><img src="references/'+st+'-angles254.jpg" alt="'+st+' rotation check" loading="lazy"></a><figcaption>'+st.replace('-',' ')+'</figcaption></figure>' for st in ['taper','curly-top'])+'</div></details>'+s[b:];(D/'index.html').write_text(s,encoding='utf8',newline='\n');print('PACKAGE254_READY')
