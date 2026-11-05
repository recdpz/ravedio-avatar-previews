from pathlib import Path
import json,shutil,re
P=Path(__file__).parent;R=P.parent/'floating138/mobile-preview';D=R/'250';OLD=R/'249'
for x in ['','components','references','assemblies','source']:(D/x).mkdir(exist_ok=True)
def remap(x):
 if isinstance(x,dict):return {k:remap(v) for k,v in x.items()}
 if isinstance(x,list):return [remap(v) for v in x]
 if isinstance(x,str) and x.startswith('components/'):return '../249/'+x
 return x
c=remap(json.loads((OLD/'catalogue249.json').read_text()));fits=json.loads((P/'fits250.json').read_text());assert len(fits)==112
c['previousPashminaFits']={k:dict(v['pashmina']) for k,v in c['fits'].items()};c['previousPashminaVariants']=c['pashminaVariants'];c['previousPashminaHairFamilies']=c['pashminaHairFamilies'];c['previousSprouts']=dict(c['sprouts']);c['pashminaVariants']={};c['pashminaHairFamilies']={}
for b,bc in c['builds'].items():
 c['pashminaVariants'][b]={};c['pashminaHairFamilies'][b]={}
 for style in bc['hair']:
  ref=fits[b+'-'+style+'-'+('open' if b=='Feminine' else 'tank')];c['pashminaHairFamilies'][b][style]=style;c['pashminaVariants'][b][style]={top:fits[b+'-'+style+'-'+top]['headgear'] for top in bc['tops']};c['fits'][b+'-'+style]['pashmina'].update(hair=ref['hair'],headgear=ref['headgear']);c['sprouts'][b+'-'+style+'--pashmina']=ref['sprout']
 c['pashminaTops'][b]=c['pashminaVariants'][b]['ponytail' if b=='Feminine' else 'taper']
for f in (P/'components').glob('*.glb'):shutil.copy2(f,D/'components'/f.name)
(D/'catalogue250.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf8',newline='\n')
js=(OLD/'viewer249.js').read_text().replace('249','250');(D/'viewer250.js').write_text(js,encoding='utf8',newline='\n')
html=(OLD/'index.html').read_text().replace('249','250').replace('Compare248','Compare249').replace('Previous248','Previous249').replace('href="../248/"','href="../249/"').replace('#25034a','#24834a')
html=re.sub(r'(<h1>Pashmina fit</h1>)<p>.*?</p>',r'\1<p>Authored worn hairstyles beneath a restrained draped hood. Concealed bulk gathers outside the actual head; visible locks keep their original styling and texture. The low ponytail exits beneath a continuous rear hem. Compare249 restores the prior fit; Cloth reveals the covered hair.</p>',html,count=1)
html=html.replace('Matched front views:248 on the left,250 on the right. Same camera and outfit.','Matched rear and profile views:249 on the left,250 on the right. Same camera and outfit.').replace('references/identity-comparison250.jpg','references/fit-comparison250.jpg').replace('Matched248 and250 hairstyle continuity','Matched249 and250 worn hair fits')
(D/'index.html').write_text(html,encoding='utf8',newline='\n')
print('PACKAGED250',len(fits),'authored top fits,16 covered styles')
