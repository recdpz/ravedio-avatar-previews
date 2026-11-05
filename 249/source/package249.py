from pathlib import Path
import json,shutil,re
P=Path(__file__).parent;R=P.parent/'floating138/mobile-preview';D=R/'249';OLD=R/'248'
for name in ['','components','references','source','assemblies']:(D/name).mkdir(exist_ok=True)
def remap(x):
 if isinstance(x,dict):return {k:remap(v) for k,v in x.items()}
 if isinstance(x,list):return [remap(v) for v in x]
 if isinstance(x,str) and x.startswith('components/'):return '../248/'+x
 return x
c=remap(json.loads((OLD/'catalogue248.json').read_text()));fits=json.loads((P/'fits249.json').read_text());assert len(fits)==112,len(fits)
c['previousPashminaFits']={k:dict(v['pashmina']) for k,v in c['fits'].items()};c['previousPashminaVariants']=c['pashminaVariants'];c['previousPashminaHairFamilies']=c['pashminaHairFamilies'];c['previousSprouts']=dict(c['sprouts']);c['pashminaVariants']={};c['pashminaHairFamilies']={}
for b in c['builds']:
 c['pashminaVariants'][b]={};c['pashminaHairFamilies'][b]={}
 for style in c['builds'][b]['hair']:
  c['pashminaHairFamilies'][b][style]=style;c['pashminaVariants'][b][style]={};default='open' if b=='Feminine' else 'tank';reference=fits[b+'-'+style+'-'+default]
  c['fits'][b+'-'+style]['pashmina']['hair']=reference['hair'];c['fits'][b+'-'+style]['pashmina']['headgear']=reference['headgear'];c['sprouts'][b+'-'+style+'--pashmina']=reference['sprout']
  for top in c['builds'][b]['tops']:c['pashminaVariants'][b][style][top]=fits[b+'-'+style+'-'+top]['headgear']
 c['pashminaTops'][b]=c['pashminaVariants'][b]['ponytail' if b=='Feminine' else 'taper']
for f in (P/'components').glob('*.glb'):shutil.copy2(f,D/'components'/f.name)
(D/'catalogue249.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf8',newline='\n')
js=(OLD/'viewer248.js').read_text().replace('248','249')
js=js.replace('p.headgear=catalogue.previousPashminaTops[b][s.top];','p.headgear=catalogue.previousPashminaVariants[b][catalogue.previousPashminaHairFamilies[b][s.hair]][s.top];')
js=js.replace("catalogue.sprouts[b+'-'+s.hair+'--'+s.headwear].path","(previousPashmina&&s.headwear==='pashmina'?catalogue.previousSprouts:catalogue.sprouts)[b+'-'+s.hair+'--'+s.headwear].path")
js=js.replace("if(o.userData.slot249==='lenses')","if(choices().headwear==='pashmina'&&!$('show-cloth').checked&&(o.userData.slot249==='headgear'||(o.userData.slot249==='extra'&&choices().detail==='sprout')))o.visible=false;if(o.userData.slot249==='lenses')")
js=js.replace("$('skin').value=s.skin;","$('skin').value=s.skin;$('show-cloth').parentElement.hidden=s.headwear!=='pashmina';")
js=js.replace('geometry:{},groups:{},transmission:[]','geometry:{},groups:{},visible:{},transmission:[]').replace('const g=o.userData.slot249;out.groups','const g=o.userData.slot249;if(o.visible)out.visible[g]=(out.visible[g]||0)+1;out.groups')
js=js.replace("['show-arms','show-lenses']","['show-arms','show-lenses','show-cloth']")
assert "['show-arms','show-lenses','show-cloth']" in js
(D/'viewer249.js').write_text(js,encoding='utf8',newline='\n')
html=(OLD/'index.html').read_text().replace('248','249').replace('Compare247','Compare248').replace('Previous247','Previous248').replace('href="../247/"','href="../248/"')
html=html.replace('#24934a','#24834a')
html=html.replace('<div class="checks">','<div class="checks"><label><input id="show-cloth" type="checkbox" checked>Cloth</label>',1)
html=re.sub(r'(<h1>Pashmina fit</h1>)<p>.*?</p>',r'\1<p>Intact hairstyles with the hood fitted around their volume. Visible locks retain the original styling and materials; the ponytail and buns use localized lower gathers. Compare248 restores the previous fit. Uncheck Cloth to inspect the actual covered hair.</p>',html,count=1)
html=html.replace('Rear drape and hair exits - matched comparison','Hairstyle continuity - matched comparison').replace('Matched Blender crops:247 on the left,249 on the right. Same camera and outfit.','Matched front views:248 on the left,249 on the right. Same camera and outfit.')
html=html.replace('src="references/junction-comparison249.png"','src="references/identity-comparison249.jpg"').replace('alt="Matched rear views of247 and249 cloth and hair fitting"','alt="Matched248 and249 hairstyle continuity"')
(D/'index.html').write_text(html,encoding='utf8',newline='\n')
print('PACKAGED249',len(fits),'cloth/top fits;16 hairstyle-specific supports; original visible hair retained')
