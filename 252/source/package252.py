from pathlib import Path
import json,shutil,re
P=Path('E:/Ravedio-Avatar/catalogue252');R=P.parent/'floating138/mobile-preview';D=R/'252';OLD=R/'251';D.mkdir(exist_ok=True);(D/'components').mkdir(exist_ok=True);(D/'references').mkdir(exist_ok=True)
def remap(x):
 if isinstance(x,dict):return {k:remap(v) for k,v in x.items()}
 if isinstance(x,list):return [remap(v) for v in x]
 if isinstance(x,str) and x.startswith('components/'):return '../251/'+x
 return x
c=remap(json.loads((OLD/'catalogue251.json').read_text()));c['before251']={k:c[k] for k in ['builds','fits','sprouts','pashminaVariants','pashminaHairFamilies','braidLengths']};c=json.loads(json.dumps(c));hair=json.loads((P/'hair252.json').read_text()) if (P/'hair252.json').exists() else {}
for style,rec in hair.items():
 b='Feminine' if style=='straight' else 'Masculine';c['builds'][b]['hair'][style]['path']=rec['path'];shutil.copy2(P/rec['path'],D/rec['path'])
fits=json.loads((P/'fits252.json').read_text()) if (P/'fits252.json').exists() else {}
for key,rec in fits.items():
 for b,bc in c['builds'].items():
  for st in bc['hair']:
   for hat in c['headwear']:
    if key==b+'-'+st+'-'+hat:
     c['fits'][b+'-'+st][hat]['hair']=rec['hair'];shutil.copy2(P/rec['hair'],D/rec['hair']);c['sprouts'][b+'-'+st+'--'+hat]=rec['sprout'];shutil.copy2(P/rec['sprout']['path'],D/rec['sprout']['path'])
notes={'taper':'Close graded sides, no detached hair particles. Retained sculpted sweep.', 'buzz':'Near-bald close cut with a clean, bounded hairline and dense fine surface texture.', 'flow':'Continuous sculpted growth with a shifted part, ear-covering length and softer curved ends.', 'middle-part':'Rooted center-part banks with continuous crown coverage.', 'locs':'Short, consistent loc sections with rounded ends and a gathered root surface.', 'curly-top':'Sculpted broad curls on top; short graduated sides and back.', 'afro':'Compact rounded silhouette with dense irregular coil texture.', 'straight':'Original long locks retained; mismatched exposed temple backing removed.'}
for st,rec in hair.items():c['builds']['Feminine' if st=='straight' else 'Masculine']['hair'][st]['note']=notes[st]
if (P/'bare-sprouts252.json').exists():
 for key,rec in json.loads((P/'bare-sprouts252.json').read_text()).items():c['sprouts'][key]=rec;shutil.copy2(P/rec['path'],D/rec['path'])
c.pop('before250',None);old=json.loads((OLD/'catalogue251.json').read_text());c['before251']['highlights']={('../251/'+k if k.startswith('components/') else k):('../251/'+v if v.startswith('components/') else v) for k,v in old['highlights'].items()};c['highlights']={}
(D/'catalogue252.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf8',newline='\n');js=(OLD/'viewer251.js').read_text().replace('251','252').replace('catalogue.before250','catalogue.before251');js=js.replace("if(s.hairColor==='highlights'&&!previousPashmina)for","if(s.hairColor==='highlights')for").replace("catalogue.highlights[p[k]]","(previousPashmina?catalogue.before251.highlights:catalogue.highlights)[p[k]]").replace("&&slot!=='groom'&&!previousPashmina","&&slot!=='groom'");(D/'viewer252.js').write_text(js,encoding='utf8',newline='\n')
html=(OLD/'index.html').read_text().replace('251','252').replace('Compare250','Compare251').replace('Previous250','Previous251').replace('href="../250/"','href="../251/"');a=html.index('<details open><summary>Final exported hair');b=html.index('<details><summary>Matched face references',a);html=html[:a]+html[b:];html=re.sub(r'<script>const proof=.*?</script>','',html);html=html.replace('Rebuilt masculine cuts, resting twin braids and authored covered fits. Closed hats conceal space buns; the pashmina tucks the ponytail inside.', 'Corrected short cuts, rebuilt sculpted growth and compact curls, consistent short locs, refined Highlights and the straight-hair temple repair.').replace('<details><summary>Matched face references', '<details open><summary>Exported hair: rotation checks</summary><div class="shape-grid">'+''.join('<figure><a href="references/'+st+'-angles252.jpg"><img loading="lazy" src="references/'+st+'-angles252.jpg" alt="'+st+' from seven angles"></a><figcaption>'+st.replace('-', ' ')+'</figcaption></figure>' for st in hair)+'</div></details><details><summary>Matched face references');(D/'index.html').write_text(html,encoding='utf8',newline='\n');print('LOCAL_PILOT252',list(hair))
