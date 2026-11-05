from pathlib import Path
import json,copy,shutil,re
P=Path(__file__).parent;R=P.parent/'floating138/mobile-preview';OLD=R/'259';D=R/'260'
for f in ['components','references','source','assemblies']:(D/f).mkdir(parents=True,exist_ok=True)
def rebase(x):
 if isinstance(x,dict):return {('../259/'+k if k.startswith('components/') else k):rebase(v) for k,v in x.items()}
 if isinstance(x,list):return [rebase(v) for v in x]
 if isinstance(x,str) and x.startswith('components/'):return '../259/'+x
 return x
c=rebase(json.loads((OLD/'catalogue259.json').read_text()));c.pop('before258',None);c['before259']={k:copy.deepcopy(c[k]) for k in ['builds','fits','sprouts','pashminaVariants','pashminaHairFamilies','braidLengths','ombre','colors']}
notes={'afro':'Slightly lower crown; width and lower coverage retained.','flow':'Off-center layered Flow: curved face-framing S paths, relaxed ear and nape layers.','locs':'Fuller mature loc sections with compact fiber relief and rounded ends.','middle-part':'Shorter split curtains with layered side and nape lengths, rather than a continuous bowl edge.','straight':'Temple root rings rebuilt as coherent cross-sections; exposed smooth support patch removed.','side-sweep':'Rebuilt upper root cross-sections and smooth front-lock transitions.','box-braids':'Slightly shorter braid fall; roots and ties remain coordinated.'}
for key,row in json.loads((P/'selected260.json').read_text()).items():
 build,style=key.split('-',1);path='components/'+Path(row['path']).name;shutil.copy2(row['path'],D/path);c['builds'][build]['hair'][style].update(path=path,note=notes[style])
for key,row in json.loads((P/'fits/fits260.json').read_text()).items():
 style,hat=key.split('|');c['fits'][style][hat]['hair']=row['hair'];shutil.copy2(P/'fits'/row['hair'],D/row['hair'])
for key,row in json.loads((P/'fits/sprouts260.json').read_text()).items():c['sprouts'][key]=row;shutil.copy2(P/'fits'/row['path'],D/row['path'])
(D/'catalogue260.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf8',newline='\n')
if (P/'fits3/fits260.json').exists():
 for row in json.loads((P/'fits3/fits260.json').read_text()).values():shutil.copy2(P/'fits3'/row['hair'],D/row['hair'])
 for key,row in json.loads((P/'fits3/sprouts260.json').read_text()).items():c['sprouts'][key]=row;shutil.copy2(P/'fits3'/row['path'],D/row['path'])
 (D/'catalogue260.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf8',newline='\n')
if (P/'fits4/fits260.json').exists():
 for row in json.loads((P/'fits4/fits260.json').read_text()).values():shutil.copy2(P/'fits4'/row['hair'],D/row['hair'])
 for key,row in json.loads((P/'fits4/sprouts260.json').read_text()).items():c['sprouts'][key]=row;shutil.copy2(P/'fits4'/row['path'],D/row['path'])
 (D/'catalogue260.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf8',newline='\n')
s=(OLD/'viewer259.js').read_text().replace('259','260').replace('before258','before259');(D/'viewer260.js').write_text(s,encoding='utf8',newline='\n')
s=(OLD/'index.html').read_text().replace('259','260').replace('Compare258','Compare259');s=re.sub('<h1>.*?</h1><p>.*?</p>','<h1>Hairstyle refinements</h1><p>Rebuilt Flow, Locs and Middle part; a slightly lower Afro; repaired Straight and Side sweep roots; shorter Box braids. Compare259 shows the previous hairstyle with the same other selections.</p>',s,count=1)
start=s.index('<details open><summary>Final exported angle checks</summary>');end=s.index('<details',start+10)
gallery='<details open><summary>Exported angle checks and comparisons</summary><div class="shape-grid">'
for key in json.loads((P/'selected260.json').read_text()):
 build,style=key.split('-',1)
 for kind in ['angles','comparison','covered']:
  file=f'references/{key}-{kind}260.jpg';gallery+=f'<figure><a href="{file}"><img src="{file}" alt="{style} {kind}" loading="lazy"></a><figcaption>{style.replace("-"," ")} · {kind}</figcaption></figure>'
gallery+='</div></details>'
s=s[:start]+gallery+s[end:];s=re.sub(r'<nav>.*?</nav>','<nav><a href="README260.txt">Handoff</a><a href="../259/">Previous259</a><a href="references/colors260.jpg">Colors</a><a href="references/small260.jpg">Small portraits</a></nav>',s,flags=re.S)
(D/'index.html').write_text(s,encoding='utf8',newline='\n');print('PACKAGE260_COMPLETE')
