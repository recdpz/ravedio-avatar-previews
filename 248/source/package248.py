from pathlib import Path
import json,re,shutil
P=Path(__file__).parent;R=P.parent/'floating138/mobile-preview';D=R/'248';OLD=R/'247'
for folder in ['','components','references','assemblies','source']:(D/folder).mkdir(exist_ok=True)
def remap(x):
 if isinstance(x,dict):return {k:remap(v) for k,v in x.items()}
 if isinstance(x,list):return [remap(v) for v in x]
 if isinstance(x,str) and x.startswith('components/'):return '../247/'+x
 return x
c=remap(json.loads((OLD/'catalogue247.json').read_text()));fits=json.loads((P/'fits248.json').read_text());hair=json.loads((P/'hair248.json').read_text())
c['previousPashminaTops']=c['pashminaTops'];c['previousPashminaFits']={k:dict(v['pashmina']) for k,v in c['fits'].items()};c['pashminaVariants']={};c['pashminaHairFamilies']={};c['pashminaTops']={}
for key,item in fits.items():
 build=key.split('-')[0];family=item['family'];top=item['top'];path=item['component'];shutil.copy2(P/path,D/path)
 c['pashminaVariants'].setdefault(build,{}).setdefault(family,{})[top]=path
for key,item in hair.items():
 build=key.split('-')[0];style=item['style'];path=item['component'];shutil.copy2(P/path,D/path)
 c['pashminaHairFamilies'].setdefault(build,{})[style]=item['family'];c['fits'][key]['pashmina']['hair']=path
 default='open' if build=='Feminine' else 'tank';c['fits'][key]['pashmina']['headgear']=c['pashminaVariants'][build][item['family']][default]
for build in c['builds']:
 c['pashminaTops'][build]=c['pashminaVariants'][build]['gathered' if build=='Feminine' else 'compact']
 for style in c['builds'][build]['hair']:
  family=c['pashminaHairFamilies'][build][style]
  for top in c['builds'][build]['tops']:assert (D/c['pashminaVariants'][build][family][top]).is_file()
(D/'catalogue248.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf8',newline='\n')
js=(OLD/'viewer247.js').read_text().replace('247','248')
js=js.replace("else p.headgear=catalogue.pashminaTops[b][s.top];","else p.headgear=catalogue.pashminaVariants[b][catalogue.pashminaHairFamilies[b][s.hair]][s.top];")
js=js.replace('yaw={front:0','yaw={rearquarter:-2.498,front:0')
js=js.replace("['front','threequarter','profile','rightprofile','rear','top','underside']","['front','threequarter','profile','rightprofile','rear','rearquarter','top','underside']")
(D/'viewer248.js').write_text(js,encoding='utf8',newline='\n')
html=(OLD/'index.html').read_text().replace('247','248').replace('Compare246','Compare247').replace('Previous246','Previous247').replace('href="../246/"','href="../247/"').replace('Matched Blender crops:246','Matched Blender crops:247')
html=re.sub(r'(<h1>Pashmina fit</h1>)<p>.*?</p>',r'\1<p>Relaxed rear drape with hairstyle-specific covered arrangements. Long locks emerge beneath the lower fabric edge; the accepted front crossing stays fixed. Compare247 switches cloth and covered hair together for the same outfit and view.</p>',html,count=1)
html=html.replace('Upper neck joins - matched comparison','Rear drape and hair exits - matched comparison').replace('alt="Matched close views of the slimmer chest wrap"','alt="Matched rear views of247 and248 cloth and hair fitting"')
html=html.replace('<select id="angle">','<select id="angle"><option value="rearquarter">Rear three-quarter</option>')
(D/'index.html').write_text(html,encoding='utf8',newline='\n')
print('PACKAGED248',len(fits),'cloth fits;',len(hair),'covered hairstyles')
