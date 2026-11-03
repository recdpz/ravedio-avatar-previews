from pathlib import Path
import json,shutil,re
P=Path(__file__).parent;R=P.parent/'floating138/mobile-preview';D=R/'251';OLD=R/'250'
for n in ['','components','references','assemblies','source']:(D/n).mkdir(exist_ok=True)
def remap(x):
 if isinstance(x,dict):return {k:remap(v) for k,v in x.items()}
 if isinstance(x,list):return [remap(v) for v in x]
 if isinstance(x,str) and x.startswith('components/'):return '../250/'+x
 return x
c=remap(json.loads((OLD/'catalogue250.json').read_text()));hair=json.loads((P/'hair251.json').read_text());fh=json.loads((P/'female-hats251.json').read_text());fits=json.loads((P/'fits251.json').read_text());hoods=json.loads((P/'pony-hoods251.json').read_text())
c['before250']={k:c[k] for k in ['builds','fits','sprouts','pashminaVariants','pashminaHairFamilies']};c=json.loads(json.dumps(c))
for k in list(c):
 if k.startswith('previous'):del c[k]
for style,record in hair.items():c['builds']['Masculine']['hair'][style].update(path=record['path'],note='Rebuilt on the retained head; clean bounded roots and authored headwear fit.')
c['builds']['Feminine']['hair']['twin-braids'].update(path=fh['braidRoots'],note='Full plaits rest against the selected top; the original roots remain independently fitted.')
for key,record in fits.items():
 b,style,hat=next((b,style,hat) for b in c['builds'] for style in c['builds'][b]['hair'] for hat in c['headwear'] if b+'-'+style+'-'+hat==key)
 c['fits'][b+'-'+style][hat]={k:record[k] for k in ['hair','headgear']};c['sprouts'][b+'-'+style+'--'+hat]=record['sprout']
c['pashminaVariants']['Feminine']['ponytail']=hoods
c['braidLengths']={mode:{top:rec['path'] for top,rec in values.items()} for mode,values in fh['braidLengths'].items()}
c['colors']['hair']=[['highlights','Highlights',None] if x[0]=='brown' else x for x in c['colors']['hair']]
c['highlights']={}
# Copy only current reachable components, without duplicating unchanged prior work.
def scan(x):
 if isinstance(x,dict):
  for v in x.values():scan(v)
 elif isinstance(x,list):
  for v in x:scan(v)
 elif isinstance(x,str) and x.startswith('components/') and x.endswith('.glb'):
  f=P/x;assert f.exists(),f;shutil.copy2(f,D/x)
scan(c)
(D/'catalogue251.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf8')
js=(OLD/'viewer250.js').read_text().replace('250','251')
js=js.replace("headwear:'pashmina'","headwear:'none'")
a=js.index('function paths(');b=js.index('\nfunction component(',a)
js=js[:a]+'''function paths(s=choices(),b=build){const c=catalogue.builds[b],p={base:s.top==='shirtless'?c.shirtlessBase:c.base,hair:c.hair[s.hair].path,eyes:c.eyes[s.eyes].path,nose:c.noses[s.nose].path,mouth:c.mouths[s.mouth].path,groom:c.grooms[s.groom].path,top:c.tops[s.top].path,bottom:c.bottoms[s.bottom].path};if(b==='Feminine'&&showLashes)p.lashes=c.lashes[s.eyes].path;if(s.headwear!=='none')Object.assign(p,catalogue.fits[b+'-'+s.hair][s.headwear]);if(s.headwear==='pashmina')p.headgear=catalogue.pashminaVariants[b][catalogue.pashminaHairFamilies[b][s.hair]][s.top];if(b==='Feminine'&&s.hair==='twin-braids')p.hairLengths=catalogue.braidLengths[s.headwear==='pashmina'?'pashmina':'normal'][s.top];
 if(previousPashmina){const old=catalogue.before250;p.hair=old.builds[b].hair[s.hair].path;delete p.hairLengths;if(s.headwear!=='none')Object.assign(p,old.fits[b+'-'+s.hair][s.headwear]);if(s.headwear==='pashmina')p.headgear=old.pashminaVariants[b][old.pashminaHairFamilies[b][s.hair]][s.top];}
 if(s.hairColor==='highlights'&&!previousPashmina)for(const k of ['hair','hairLengths'])if(p[k]&&catalogue.highlights[p[k]])p[k]=catalogue.highlights[p[k]];
 if(s.glasses!=='none'){if(s.glasses==='rectangular')Object.assign(p,c.rectangular);else {p.glasses=catalogue.glasses[s.glasses].path;p.lenses=catalogue.glasses[s.glasses].lenses;}}if(s.detail!=='none')p.extra=s.detail==='hot'?c.hot:s.detail==='sprout'?(previousPashmina?catalogue.before250.sprouts:catalogue.sprouts)[b+'-'+s.hair+'--'+s.headwear].path:catalogue.details[s.detail].path;return Object.fromEntries(Object.entries(p).filter(([k,v])=>v))}
''' +js[b:]
js=js.replace("const hair=pick('hair',s.hairColor)","const hair=s.hairColor==='highlights'?new THREE.Color('#68402C'):pick('hair',s.hairColor)")
js=js.replace("(slot==='hair'||slot==='groom')&&hair", "(slot==='hair'||slot==='hairLengths'||slot==='groom')&&hair&&!(s.hairColor==='highlights'&&slot!=='groom'&&!previousPashmina)")
js=js.replace("' Ponytail is gathered low under this headwear.'", "' Ponytail has a covered fit for this headwear.'")
js=js.replace("+(build==='Feminine'&&s.hair==='ponytail'", "+(build==='Feminine'&&s.hair==='space-buns'&&s.headwear!=='none'&&s.headwear!=='ears'?' Buns are concealed beneath the normal hat shape.':'')+(build==='Feminine'&&s.hair==='ponytail'&&s.headwear==='pashmina'?' Ponytail is folded and tucked inside the hood.':'')+(build==='Feminine'&&s.hair==='ponytail'")
(D/'viewer251.js').write_text(js,encoding='utf8',newline='\n')
html=(OLD/'index.html').read_text().replace('250','251').replace('Compare249 pashmina','Compare250 hair and headwear').replace('Previous249','Previous250').replace('href="../249/"','href="../250/"')
html=re.sub(r'<h1>.*?</h1><p>.*?</p>', '<h1>Hair and headwear</h1><p>Rebuilt masculine cuts, resting twin braids and authored covered fits. Closed hats conceal space buns; the pashmina tucks the ponytail inside. Select each feature independently, rotate and zoom. Compare250 restores the previous hair and headwear together.</p>',html,count=1)
a=html.index('<details open><summary>Hairstyle continuity');b=html.index('<details><summary>Matched face references',a)
html=html[:a]+'''<details open><summary>Final exported hair - all angles</summary><div id="hair-proof" class="shape-grid"></div></details><details open><summary>Covered fits and contact checks</summary><img src="references/fits-review251.jpg" alt="Final hat and hairstyle assemblies" loading="lazy" style="width:100%"></details>'''+html[b:]
html=html.replace('Every current hairstyle has an authored fit for each headwear choice. Covered styles use contextual crown or gathered-hair variants.', 'Hats use authored covered fits. Space buns are concealed under closed hats; ears retain the buns. Twin-braid lengths change with the selected top.')
html=html.replace('<nav><a href="handoff251.json">','<nav><a href="technical251.json">Asset counts</a><a href="handoff251.json">')
html=html.replace('</main><script type="importmap">','</main><script>const proof=document.getElementById("hair-proof");for(const style of ["taper","buzz","curly-top","afro","flow","locs","middle-part"]){const f=document.createElement("figure");f.innerHTML=`<a href="references/Masculine-${style}-export251.jpg"><img src="references/Masculine-${style}-export251.jpg" alt="${style}, seven exported angles" loading="lazy"></a><figcaption>${style.replaceAll("-"," ")}</figcaption>`;proof.append(f)}</script><script type="importmap">')
(D/'index.html').write_text(html,encoding='utf8',newline='\n')
print('PACKAGE251',len(fits),'headwear pairs')
