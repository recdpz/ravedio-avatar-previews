from pathlib import Path
import json,shutil
P=Path(__file__).parent;R=P.parent/'floating138/mobile-preview';D=R/'235'
for f in ['components','source','references','assemblies']:(D/f).mkdir(parents=True,exist_ok=True)
cat=json.loads((R/'234/catalogue234.json').read_text(encoding='utf8'))
#234's locally scoped lashes are the only component paths requiring rebasing.
for b,c in cat['builds'].items():
 for group in ['hair','eyes','lashes','noses','mouths','grooms','tops','bottoms']:
  for item in c.get(group,{}).values():
   for k,v in list(item.items()):
    if k in ['path','lenses'] and v and v.startswith('components/'):item[k]='../234/'+v
for style,item in json.loads((P/'hair235.json').read_text()).items():cat['builds']['Masculine']['hair'][style]={'label':{'curly-top':'Curly top','middle-part':'Middle part'}.get(style,style.title()),'path':item['parts']['hair'],'note':'Rebuilt235 candidate; shared approved head, face and body.'}
for style,item in cat['builds']['Masculine']['hair'].items():item['note']={'sidepart':'Styled side part.','taper':'Lifted side sweep with a broader clean fade.','buzz':'Nearly shaved, with a light hair shadow and tidy edges.','curly-top':'Curled crown with short faded sides and back.','afro':'Compact, dense coiled volume.','flow':'Brushed-back layers with curved temples and a soft nape.','locs':'Short rooted locs with rounded ends.','middle-part':'Parted curtains with layered ends.'}[style]
for style,item in cat['builds']['Feminine']['hair'].items():item['note']=''
for style,item in json.loads((P/'groom235.json').read_text()).items():cat['builds']['Masculine']['grooms'][style]['path']=item['path']
cat['details'].pop('gems',None);cat['headwear']['headband']['label']='Bandana'
for k,item in cat['headwear'].items():
 if k!='none':item.pop('path',None);item['fit_source']='Use the explicit hair/headwear fit table'
cat['details']['sprout'].pop('path',None)
cat['colors']['frames']=[['black','Black','#181B22'],['tortoise','Tortoise','#775137'],['silver','Silver','#B9BEC5'],['gold','Gold','#BA9458']]
cat['colors']['lenses']=[['dark','Dark'],['clear','Clear']]
cat['lensDefaults']={k:('clear' if k=='reading' else 'dark') for k in cat['glasses'] if k!='none'}
for key,item in json.loads((P/'lenses235.json').read_text()).items():
 b,style=key.split('-',1)
 if style=='rectangular':cat['builds'][b]['rectangular']['lenses']=item['lenses']
 else:cat['glasses'][style]['lenses']=item['lenses']
cat['fits']=json.loads((P/'fits235.json').read_text());cat['sprouts']=json.loads((P/'sprouts235.json').read_text())
used=set()
def collect(obj):
 if isinstance(obj,dict):
  for v in obj.values():collect(v)
 elif isinstance(obj,list):
  for v in obj:collect(v)
 elif isinstance(obj,str) and obj.startswith('components/') and obj.endswith('.glb'):used.add(obj.split('/',1)[1])
collect(cat)
for name in used:shutil.copy2(P/'components'/name,D/'components'/name)
for f in (D/'components').glob('*.glb'):
 if f.name not in used:assert f.resolve().parent== (D/'components').resolve();f.unlink()
for f in (P/'review2').glob('*.png'):shutil.copy2(f,D/'references'/f.name)
for style in ['taper','buzz','curly-top','afro','flow','locs','middle-part']:
 f=P/'review1'/f'Masculine-{style}-front.png';shutil.copy2(f,D/'references'/f.name)
for f in (P/'fixtures').glob('*.png'):shutil.copy2(f,D/'references'/f.name)
for build in ['Feminine','Masculine']:shutil.copy2(P/'sources'/f'{build}-pashmina-assembly235.blend',D/'assemblies'/f'{build}-pashmina235.blend')
expected={f.name for f in (P/'review2').glob('*.png')}|{f'Masculine-{s}-front.png' for s in ['taper','buzz','curly-top','afro','flow','locs','middle-part']}|{f.name for f in (P/'fixtures').glob('*.png')}
for f in (D/'references').iterdir():
 if f.name not in expected:assert f.resolve().parent==(D/'references').resolve();f.unlink()
(D/'catalogue235.json').write_text(json.dumps(cat,indent=2)+'\n',encoding='utf8');shutil.copy2(R/'234/face-palette209.json',D/'face-palette209.json')
js=(R/'234/viewer234.js').read_text(encoding='utf8').replace('234','235')
js=js.replace("let build='Feminine'","let build='Masculine'")
js=js.replace("bottomColor:'default'","bottomColor:'default',frameColor:'black',lensTint:'dark'")
js=js.replace("['bottomColor','bottom']","['bottomColor','bottom'],['frameColor','frames'],['lensTint','lenses']")
js=js.replace("s[id]='default';return s}","s[id]=id==='frameColor'?'black':id==='lensTint'?(s.glasses==='reading'?'clear':'dark'):'default';if(s.glasses==='reading'&&!raw?.lensTint)s.lensTint='clear';return s}")
js=js.replace("$('skin').value=s.skin;","$('skin').value=s.skin;$('frameColor').disabled=$('lensTint').disabled=s.glasses==='none';")
js=js.replace("$('note').textContent=catalogue.builds[build].hair[s.hair].note;", "$('note').textContent=catalogue.builds[build].hair[s.hair].note+(s.headwear==='headband'?(build==='Feminine'?' Triangular crown scarf, with a contextual covered/gathered fit.':' Folded forehead band tied at the back; curls are held back where needed.'):'')+(build==='Feminine'&&s.hair==='ponytail'&&['beanie','bucket','cowboy','headband'].includes(s.headwear)?' Ponytail is gathered low under this headwear.':'');")
js=js.replace("$('compare-'+k).src=build==='Feminine'?'references/Feminine-'+k+'-export-front.png':'references/Masculine-'+k+'-front.png'","$('compare-'+k).src=build==='Feminine'?'../234/references/Feminine-'+k+'-export-front.png':'../234/references/Masculine-'+k+'-front.png'")
js=js.replace("Object.assign(p,catalogue.fits[b+'-'+s.hair][s.headwear])","Object.assign(p,catalogue.fits[b+'-'+s.hair][s.headwear])")
js=js.replace("catalogue.details[s.detail].path","s.detail==='sprout'?catalogue.sprouts[b+'-'+s.hair+'--'+s.headwear].path:catalogue.details[s.detail].path")
js=js.replace("m.dispose()})}","m.dispose();if(o.userData.ownedGeometry235)o.geometry.dispose()})}")
old="if(slot==='hair'&&hair&&!/tie|band|Skin|metal|elastic/i.test(n)){const lum=m.color.r*.2126+m.color.g*.7152+m.color.b*.0722;m.color.copy(hair).multiplyScalar(Math.max(.45,Math.min(1.3,Math.sqrt(lum/.08))))}"
new="""if((slot==='hair'||slot==='groom')&&hair&&!/tie|band|Skin|metal|elastic/i.test(n)){
 if(!o.userData.colorFixed235){const col=o.geometry.getAttribute('color');if(col){const geom=o.geometry.clone(),out=new Float32Array(col.count*col.itemSize);let mean=0;for(let i=0;i<col.count;i++)mean+=.2126*col.getX(i)+.7152*col.getY(i)+.0722*col.getZ(i);mean/=col.count;for(let i=0;i<col.count;i++){const l=.2126*col.getX(i)+.7152*col.getY(i)+.0722*col.getZ(i),shade=Math.max(.70,Math.min(1.18,Math.sqrt(l/Math.max(.001,mean))));out[i*col.itemSize]=out[i*col.itemSize+1]=out[i*col.itemSize+2]=shade;if(col.itemSize===4)out[i*4+3]=col.getW(i)}geom.setAttribute('color',new THREE.BufferAttribute(out,col.itemSize));o.geometry=geom;o.userData.ownedGeometry235=true}o.userData.colorFixed235=true}
 m.color.copy(hair).multiplyScalar(slot==='groom'?.82:1.0);
 }if(slot==='glasses'){m.color.copy(pick('frames',s.frameColor));m.metalness=['silver','gold'].includes(s.frameColor)?.72:.08;m.roughness=.28;if(s.frameColor==='tortoise'){m.map=tortoiseTexture();if(!o.geometry.getAttribute('uv')){if(!o.userData.ownedGeometry235){o.geometry=o.geometry.clone();o.userData.ownedGeometry235=true}const pos=o.geometry.getAttribute('position'),uv=new Float32Array(pos.count*2);for(let i=0;i<pos.count;i++){uv[i*2]=pos.getX(i)*12;uv[i*2+1]=pos.getY(i)*12}o.geometry.setAttribute('uv',new THREE.BufferAttribute(uv,2))}}}
 if(slot==='lenses'){m.transmission=0;m.ior=1;m.thickness=0;m.transparent=true;m.opacity=s.lensTint==='clear'?.075:.84;m.color.set(s.lensTint==='clear'?'#DCE9EB':'#1C2029');m.roughness=.025;m.depthWrite=false;m.side=THREE.FrontSide;m.needsUpdate=true;o.renderOrder=5;}"""
assert old in js;js=js.replace(old,new)
js=js.replace("async function colors(target,s)","""let tortoise=null;function tortoiseTexture(){if(tortoise)return tortoise;const c=document.createElement('canvas');c.width=c.height=64;const x=c.getContext('2d');x.fillStyle='#A17A49';x.fillRect(0,0,64,64);for(let i=0;i<24;i++){x.fillStyle=i%2?'#2C1A0F':'#694020';x.beginPath();x.ellipse((i*31)%64,(i*17)%64,5+i%7,4+i%5,i,0,Math.PI*2);x.fill()}tortoise=new THREE.CanvasTexture(c);tortoise.colorSpace=THREE.SRGBColorSpace;tortoise.wrapS=tortoise.wrapT=THREE.RepeatWrapping;return tortoise}
async function colors(target,s)""")
cloth="""function clothColor(source,target){const c=document.createElement('canvas'),im=source.image;c.width=im.width;c.height=im.height;const ctx=c.getContext('2d');ctx.drawImage(im,0,0);const d=ctx.getImageData(0,0,c.width,c.height),a=d.data,t=target.clone().convertLinearToSRGB();for(let i=0;i<a.length;i+=4){const l=.2126*a[i]+.7152*a[i+1]+.0722*a[i+2];if(l<140){a[i]=Math.round(t.r*255);a[i+1]=Math.round(t.g*255);a[i+2]=Math.round(t.b*255)}}ctx.putImageData(d,0,0);const out=new THREE.CanvasTexture(c);out.colorSpace=THREE.SRGBColorSpace;out.flipY=source.flipY;out.wrapS=source.wrapS;out.wrapT=source.wrapT;return out}
"""
js=js.replace('let tortoise=null;',cloth+'let tortoise=null;')
js=js.replace("m.dispose();if(o.userData.ownedGeometry235)","{if(m.userData.ownedClothMap235)m.map?.dispose();m.dispose()}if(o.userData.ownedGeometry235)")
js=js.replace("if(slot==='headgear'&&hat&&!/logo|emblem|stitch|metal|lining|pink|white|gold/i.test(n))m.color.copy(hat);","if(slot==='headgear'&&hat&&!/logo|emblem|stitch|metal|lining|pink|white|gold/i.test(n)){if(m.map&&/pashmina|bandana/i.test(n)){m.map=clothColor(m.map,hat);m.userData.ownedClothMap235=true;m.color.setRGB(1,1,1)}else m.color.copy(hat)}")
js=js.replace("'bottomColor'])$(id).onchange", "'bottomColor','frameColor','lensTint'])$(id).onchange")
js=js.replace("menu();load()};\n$('show-lashes')", "if(id==='glasses')choices().lensTint=choices().glasses==='reading'?'clear':'dark';menu();load()};\n$('show-lashes')")
js=js.replace("window.review235={state,inspect,", "window.review235={materials:()=>{const out=[];root?.traverse(o=>{if(o.isMesh)for(const m of Array.isArray(o.material)?o.material:[o.material])out.push({slot:o.userData.slot235,name:m.name,color:m.color.toArray(),opacity:m.opacity,transmission:m.transmission||0})});return out},state,inspect,")
js=js.replace("if(q.get('eyes')", "const requested={...choices()};for(const k of [...Object.keys(fields),'headwear','glasses','detail','hairColor','headgearColor','topColor','bottomColor','frameColor','lensTint'])if(q.has(k))requested[k]=q.get(k);if(q.has('skin'))requested.skin=Number(q.get('skin'));if(q.has('glasses')&&!q.has('lensTint'))requested.lensTint=requested.glasses==='reading'?'clear':'dark';memory[build]=sanitize(build,requested);if(['face','body'].includes(q.get('mode'))){mode=q.get('mode');for(const n of ['face','body'])$(n).setAttribute('aria-pressed',String(n===mode))}if([...$('angle').options].some(o=>o.value===q.get('angle'))){angle=q.get('angle');$('angle').value=angle}orient();if(q.get('eyes')")
(D/'viewer235.js').write_text(js,encoding='utf8')
html=(R/'234/index.html').read_text(encoding='utf8').replace('234','235').replace('Feminine eyelashes','Hair and headwear')
html=html.replace('Fitted lashes for each feminine eye shape. Toggle Lashes to compare. Both builds now use no nose and the regular smile.','Revised masculine hairstyles, fitted headwear for both builds, clipped sprout and independent frame/lens colors. Rotate and zoom to inspect the details.')
html=html.replace('<label>Detail<select id="detail"></select></label>','<label>Frame color<select id="frameColor"></select></label><label>Lens tint<select id="lensTint"></select></label><label>Detail<select id="detail"></select></label>')
html=html.replace('Unavailable hair/headwear pairs are disabled until fitted. Choose no headwear to see every hairstyle. Other combinations are review candidates, not blanket fit approval.','Every current hairstyle has an authored fit for each headwear choice. Covered styles use contextual crown or gathered-hair variants. Clear lenses preserve facial sharpness; all styles default to Dark except Reading.')
html=html.replace('<nav>','<nav><a href="../234/">Before234</a>')
start=html.index('<details open>')
gallery='<details open><summary>Revised masculine hairstyles · Blender references</summary><div class="shape-grid">'+''.join(f'<figure><img src="references/Masculine-{k}-front.png" alt="{label}"><figcaption>{label}</figcaption></figure>' for k,label in [('taper','Taper'),('buzz','Buzz'),('curly-top','Curly top'),('afro','Afro'),('flow','Flow'),('locs','Locs'),('middle-part','Middle part')])+'</div></details><details><summary>Feminine headwear · reopened export references</summary><p class="small">Use Full body to inspect the pashmina wrap and hanging ends. Closed hats use a low pony; the selected224 cap pair is retained exactly.</p><div class="shape-grid">'+''.join(f'<figure><img src="references/Feminine-ponytail--{k}-front.png" alt="{label}"><figcaption>{label}</figcaption></figure>' for k,label in [('cap','Cap'),('beanie','Beanie'),('bucket','Bucket hat'),('cowboy','Cowboy hat'),('headband','Bandana'),('ears','Ears'),('pashmina','Pashmina')])+'</div></details>'
pashmina='<details id="pashmina"><summary>Pashmina · all-angle export review</summary><p class="small">Blender references of the packed final assemblies. The rear gathers into the nape; broad hood folds converge into a loose chest knot and two soft ends. Major body forms support the fabric; smaller garment gaps are bridged. Use the live Full body view to compare tops and hairstyles.</p>'+''.join('<h3>'+build+'</h3><div class="shape-grid">'+''.join(f'<figure><img src="references/{build}-pashmina235-{angle}.png" alt="{build} pashmina {label}" loading="lazy"><figcaption>{label}</figcaption></figure>' for angle,label in [('front','Front'),('threequarter','Three-quarter'),('profile','Side'),('rightprofile','Opposite side'),('rear','Back'),('top','Top'),('underside','Underside')])+'</div>' for build in ['Feminine','Masculine'])+'</details>'
html=html[:start]+gallery+pashmina+html[start:].replace('<details open>','<details>',1)
(D/'index.html').write_text(html,encoding='utf8')
sources=['common235.py','hair235.py','headwear235.py','fits235.py','accessories235.py','scarf_support235.py','scarf_knot235.py','fixtures235.py','groom235.py','lens_defaults235.py','package235.py','audit235.py','finish235.py','undersides235.py','overviews235.py','browser235.cjs','color-check235.cjs','final-smoke235.cjs','triples235.cjs']
for name in sources:shutil.copy2(P/name,D/'source'/name)
for stale in (D/'source').iterdir():
 if stale.name not in sources:stale.unlink()
print('PACKAGED235',len(cat['fits']),len(cat['sprouts']))
