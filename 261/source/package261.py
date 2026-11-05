from pathlib import Path
import json,copy,shutil,re
P=Path('E:/Ravedio-Avatar/catalogue261');R=P.parent/'floating138/mobile-preview';OLD=R/'260';D=R/'261'
for f in ['components','references','source','assemblies']:(D/f).mkdir(parents=True,exist_ok=True)
def rebase(x):
 if isinstance(x,dict):return {('../260/'+k if k.startswith('components/') else k):rebase(v) for k,v in x.items()}
 if isinstance(x,list):return [rebase(v) for v in x]
 if isinstance(x,str) and x.startswith('components/'):return '../260/'+x
 return x
c=rebase(json.loads((OLD/'catalogue260.json').read_text()));c.pop('before259',None);c['before260']={k:copy.deepcopy(c[k]) for k in ['builds','fits','sprouts','pashminaVariants','pashminaHairFamilies','braidLengths','ombre','colors']}
sel=json.loads((P/'selected261.json').read_text())
for key,row in sel.items():
 build,style=key.split('-',1);path='components/'+Path(row['path']).name;shutil.copy2(row['path'],D/path);c['builds'][build]['hair'][style].update(path=path,note='Continuous recessed scalp coverage; stray support edges removed.'+(' Pinched side sections reconstructed without changing the curl path.' if style=='curls' else '')+(' Buried crown junction closes the exposed opening.' if style=='flow' else ''))
(D/'catalogue261.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf8')
s=(OLD/'viewer260.js').read_text().replace('260','261').replace('before259','before260');(D/'viewer261.js').write_text(s,encoding='utf8')
s=(OLD/'index.html').read_text().replace('260','261').replace('Compare259','Compare260');s=re.sub('<h1>.*?</h1><p>.*?</p>','<h1>Hair geometry cleanup</h1><p>All sixteen styles audited. Repaired exposed root edges, crown coverage and pinched sections while retaining the established cuts. Compare260 keeps the other features unchanged.</p>',s,count=1)
start=s.index('<details open><summary>Exported angle checks');end=s.index('<details',start+10)
gallery='<details open><summary>Exported angle checks and comparisons</summary><div class="shape-grid">'
for key in sel:
 for kind in ['angles','comparison','covered']:
  file=f'references/{key}-{kind}261.jpg';gallery+=f'<figure><a href="{file}"><img src="{file}" alt="{key} {kind}" loading="lazy"></a><figcaption>{key} / {kind}</figcaption></figure>'
gallery+='</div></details>';s=s[:start]+gallery+s[end:];s=re.sub(r'<nav>.*?</nav>','<nav><a href="README261.txt">Handoff</a><a href="../260/">Previous260</a><a href="references/colors261.jpg">Colors</a><a href="references/small261.jpg">Small portraits</a></nav>',s,flags=re.S);(D/'index.html').write_text(s,encoding='utf8')
# Temporary old comparison boards keep all local links valid during capture; replaced by final261 outputs before sealing.
for key in sel:
 for kind in ['angles','comparison','covered']:
  src=OLD/'references'/f'{key}-{kind}260.jpg'
  if not src.exists():src=OLD/'references/Feminine-straight-angles260.jpg'
  shutil.copy2(src,D/'references'/f'{key}-{kind}261.jpg')
for kind in ['colors','small']:shutil.copy2(OLD/'references'/f'{kind}260.jpg',D/'references'/f'{kind}261.jpg')
(D/'README261.txt').write_text('Ravedio261 - Hair geometry audit and repairs. Work in progress; final verified handoff follows.\n')
print('PACKAGE261_INITIAL_READY')
