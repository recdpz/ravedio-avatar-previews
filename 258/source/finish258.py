from pathlib import Path
import json,struct,hashlib,shutil,subprocess,io,ast
import numpy as np
from PIL import Image,ImageOps,ImageDraw
P=Path(__file__).parent;R=P.parent/'floating138/mobile-preview';D=R/'258';BASE='444304044f001b0de9acd46509de3fd2e928c524';STYLES=['taper','sidepart','curly-top']
def save(name,obj): (D/name).write_text(json.dumps(obj,indent=2)+'\n',encoding='utf8',newline='\n')
def load(f): return json.loads(Path(f).read_text(encoding='utf-8-sig'))
browser=load(P/'browser258.json');extra=load(P/'extra-angles258.json');black=load(P/'black258.json')
assert len(browser['checks'])==137 and not browser['errors'] and not browser['http']
assert extra['additionalExportedViews']==90 and not extra['errors']
assert len(black['checks'])==29 and not black['errors'] and not black['http']
assert len(list((P/'browser-final').glob('final-*.png')))==266
assert len(list((P/'browser-final').glob('black-*.png')))==46
assert len(load(D/'depth258.json')['pairs'])==30
c=load(D/'catalogue258.json');assert next(row[2] for row in c['colors']['hair'] if row[0]=='black')=='#303030'
def paste(im,f,x,y,w,h):
 pic=Image.open(f).convert('RGBA');bg=Image.new('RGBA',pic.size,'#29394c');bg.alpha_composite(pic);pic=ImageOps.contain(bg.convert('RGB'),(w,h));im.paste(pic,(x+(w-pic.width)//2,y))
for st in STYLES:
 for src,dst in [(f'{st}-final-review258.jpg',f'{st}-angles258.jpg'),(f'{st}-covered-review258.jpg',f'{st}-covered258.jpg')]:shutil.copy2(P/src,D/'references'/dst)
 im=Image.new('RGB',(1200,620),'#29394c');draw=ImageDraw.Draw(im)
 for row,kind in enumerate(['before','none']):
  for col,angle in enumerate(['front','profile','rear','top']):
   paste(im,P/'browser-final'/f'final-{st}-{kind}-{angle}.png',col*300,row*310,300,285)
   draw.text((col*300+5,row*310+288),('257 before' if row==0 else '258 current')+' / '+angle,fill='white')
 im.save(D/'references'/f'{st}-comparison258.jpg',quality=94)
im=Image.new('RGB',(800,525),'#29394c');draw=ImageDraw.Draw(im)
for i,(st,color,skin) in enumerate((st,color,skin) for st in STYLES for color in ['default','ombre'] for skin in ['0','3']):
 f=P/'browser-final'/f'final-{st}-{color}-skin{skin}-small120.png';assert Image.open(f).size==(120,120);x=i%4*200;y=i//4*175;paste(im,f,x+40,y,120,120);draw.text((x+8,y+128),st+' '+color+' skin'+skin,fill='white')
im.save(D/'references/small258.jpg',quality=95)
for build in ['Masculine','Feminine']:
 names=[r['hair'] for r in black['checks'] if r.get('build')==build];assert len(names)==8
 im=Image.new('RGB',(1200,640),'#29394c');draw=ImageDraw.Draw(im)
 for i,hair in enumerate(names):
  x=i%4*300;y=i//4*320;paste(im,P/'browser-final'/f'black-{build}-{hair}-threequarter.png',x,y,300,260);paste(im,P/'browser-final'/f'black-{build}-{hair}-front120.png',x+180,y+180,120,120);draw.text((x+8,y+302),hair+' / Black #303030',fill='white')
 im.save(D/'references'/f'black-{build}258.jpg',quality=94)
im=Image.new('RGB',(800,400),'#29394c');draw=ImageDraw.Draw(im)
for i,(label,name) in enumerate([('257 / #28233A','old'),('258 / #303030','new')]):paste(im,P/'browser-final'/f'black-comparison-{name}.png',i*400,0,400,370);draw.text((i*400+10,378),label+' / identical hair geometry and lighting',fill='white')
im.save(D/'references/black-comparison258.jpg',quality=95)
grooms=[r for r in black['checks'] if 'groom' in r];im=Image.new('RGB',(1200,900),'#29394c');draw=ImageDraw.Draw(im)
for i,row in enumerate(grooms):
 x=i%4*300;y=i//4*300;paste(im,P/'browser-final'/f"black-groom-{row['groom']}-skin{row['skin']}.png",x,y,300,272);draw.text((x+8,y+276),row['groom']+' / skin'+row['skin'],fill='white')
im.save(D/'references/black-facial-hair258.jpg',quality=94)
def glb(f):
 raw=f.read_bytes();n=struct.unpack_from('<I',raw,12)[0];return json.loads(raw[20:20+n]),raw[28+n:]
def array(g,b,i):
 a=g['accessors'][i];v=g['bufferViews'][a['bufferView']];dt={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']];width={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];step=np.dtype(dt).itemsize
 return np.ndarray((a['count'],width),dtype=dt,buffer=b,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',width*step),step)).copy()
def positions(f):
 g,b=glb(f);return {m['name']:np.vstack([array(g,b,p['attributes']['POSITION']) for p in m['primitives']]) for m in g['meshes']}
oldpos=positions(R/'257/components/Masculine-taper-hair257.glb');newpos=positions(D/'components/Masculine-taper-hair258.glb');sidepos=positions(D/'components/Masculine-sidepart-hair258.glb')
def height(pos):return max(float(v[:,1].max()) for v in pos.values())
oldcurly=positions(R/'257/components/Masculine-curly-top-hair257.glb');newcurly=positions(D/'components/Masculine-curly-top-hair258.glb');kept=[name for name in oldcurly if not name.startswith('Hair257 /')]
assert kept and all(name in newcurly and np.array_equal(oldcurly[name],newcurly[name]) for name in kept)
shape=dict(old_taper_max_y=height(oldpos),new_taper_max_y=height(newpos),new_sidepart_max_y=height(sidepos),taper_top_lower_by=height(oldpos)-height(newpos),curly_crown_exact_preserved_meshes=kept,rear_lock_method='Resample shorter centerline with original rounded cross sections and parallel transport; no radius pinching',tip_method='Opaque cores plus terminal alpha from t=0.86. No257 per-vertex tip shrink.',fade_surface='Smooth density-based lift0.0025+0.008*density; cosine ripples removed',sidepart='Opposite sweep; restrained forward curve and wave; recessed root foundation shaded0.8')
assert shape['taper_top_lower_by']>.03
tech=[]
for f in sorted((D/'components').glob('*.glb')):
 raw=f.read_bytes();g,b=glb(f);used={p['material'] for m in g['meshes'] for p in m['primitives']};assert not set(g.get('extensionsUsed',[]))&{'KHR_draco_mesh_compression','EXT_meshopt_compression','KHR_mesh_quantization'};textures=[]
 for img in g.get('images',[]):
  v=g['bufferViews'][img['bufferView']];blob=b[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']];pic=Image.open(io.BytesIO(blob));textures.append(dict(size=[pic.width,pic.height],bytes=len(blob)))
 trans=[g['materials'][i]['name'] for i in used if set(g['materials'][i].get('extensions',{}))&{'KHR_materials_transmission','KHR_materials_volume'}];assert not trans
 for m in g['meshes']:
  for p in m['primitives']:
   for attr in ['POSITION','NORMAL']:
    v=array(g,b,p['attributes'][attr]);assert np.isfinite(v).all()
   normals=array(g,b,p['attributes']['NORMAL']);assert np.max(np.abs(np.linalg.norm(normals,axis=1)-1))<.001
 tech.append(dict(path=f.relative_to(D).as_posix(),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),triangles=sum(g['accessors'][p['indices']]['count']//3 for m in g['meshes'] for p in m['primitives']),materials=len(used),primitives=sum(len(m['primitives']) for m in g['meshes']),textures=textures,alpha_modes=sorted({g['materials'][i].get('alphaMode','OPAQUE') for i in used}),transmission=trans,compressed=False,quantized=False))
assert len(tech)==72
refs=set()
def scan(x):
 if isinstance(x,dict):
  for v in x.values():scan(v)
 elif isinstance(x,list):
  for v in x:scan(v)
 elif isinstance(x,str) and x.endswith('.glb'):refs.add((D/x).resolve())
scan(c);assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()==BASE
blobs={line.split('\t',1)[1]:line.split()[2] for line in subprocess.check_output(['git','ls-tree','-r','HEAD'],cwd=R,text=True).splitlines()};deps=[]
for f in sorted(refs):
 assert f.exists() and f.is_relative_to(R.resolve()),f
 if f.is_relative_to(D.resolve()):continue
 raw=f.read_bytes();key=f.relative_to(R).as_posix();assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==blobs[key],key;deps.append(dict(path=key,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
assemblies=load(P/'assemblies258.json')
for row in assemblies.values():shutil.copy2(row['source'],D/row['packed_path'])
settings=load(P/'pass4/settings.json');settings.pop('tip_thinning',None);settings.pop('tip_start',None);settings.update(terminal_geometry_shrink=False,tip_alpha_start=.86,black='#303030',black_before='#28233A',fade_roughness=.56,fade_specular=.18,fade_coat=0)
review=dict(revision=258,status='Candidate pending owner review',source_iterations='Pass1 bare rear rejected; pass2 rounded nape/relaxed opposite sweep; export trial transform mismatch rejected; pass4 final geometry/material correction',protected='Face/body/wardrobe/skin/headgear/lighting and other hair geometry unchanged; 13 other hairstyles reuse original assets. Black recolor intentionally affects all hair and male facial hair.',exported_visual_views=312,core_views=266,black_views=46,covered_visual_views=168,cloth_hidden_views=6,exact120px_images=28,local_browser_checks=137,black_checks=29,artifact_review='Repeated rear tip dents removed using original rounded cross sections. Rippled fade field removed and short-field reflections softened; flagged white streak absent from final GLB right-profile review. Natural studio highlights retained.',directional_detail='Stronger/wider but fewer fine strokes; readable close up and recedes at120px instead of becoming dots or stripes.',limits='Artwork/export checks only. Native alpha composition and phone performance are not qualified by browser results.')
handoff=dict(revision=258,baseline_commit=BASE,changed_styles=STYLES,geometry=shape,colors='Black changed globally from purple-biased#28233A to neutral#303030. Hair shade multipliers0.88(direction marks),0.8(recessed roots),0.82(groom) preserved. Ombré geometry, alpha, normals, indices, UVs and transforms match corresponding base fits.',rendering='Main locks OPAQUE; terminal tips, smooth fade and short directional strokes use BLEND opacity with vertex COLOR_0 alpha. No transmission/refraction in these hair assets. Correct alpha composition required; nearest-opaque baker alone is insufficient.',coordinates='Shared coordinates and independent selectable/recolorable features retained. No per-component recentering.',exports='72 ordinary GLBs:24 hair,24 Ombré,24 seated sprout. Three packed final-GLB assemblies. Other catalogue components unchanged.',references='30 matched120/512 color/32-bit Z pairs from final GLBs:three hairstyles with default skins0/1/3 and Black skins0/3. Camera framing identical. Alpha threshold0.5 recorded; assembled depth is not a full component occlusion bake. Regenerate color and depth together after geometry/camera/version changes.',black_source='Packed sources use canonical Default. assemblies258.json also records a neutralBlack material/vertex-color recipe for reproducible Black references.',lighting='Fixed studio, camera, exposure and color management recorded in assemblies258.json. Blender lighting/tonemapping/shader node behavior does not transfer identically through GLB.',controls='Independent feature controls and rotation/zoom retained. Compare257 restores its shapes and palette. Original raised B remains a bare-Taper comparison.',technical='technical258.json',qualification=review['limits'],profile_contract='No profile bytes, wire contracts or mobile renderer changes.')
for name,obj in [('technical258.json',tech),('assemblies258.json',assemblies),('review258.json',review),('handoff258.json',handoff),('dependencies258.json',dict(baseline_commit=BASE,retained_glbs=deps)),('browser258.json',browser),('black258.json',black),('extra-angles258.json',extra),('ombre258.json',load(P/'ombre258.json')),('fits258.json',load(P/'pass4/fits258.json')),('shape258.json',shape),('selected-settings258.json',settings)]:save(name,obj)
for name in ['core258.py','refine258.py','final258.py','fits258.py','package258.py','ombre258.py','reference258-final.py','browser258.cjs','black258.cjs','extra-angles258.cjs','board258.py','finish258.py']:
 f=P/name
 if f.suffix=='.py':ast.parse(f.read_text(encoding='utf-8-sig'))
 shutil.copy2(f,D/'source'/name)
(D/'README258.txt').write_text('Ravedio258 - Lower Taper / Relaxed Side part\n\nTaper now uses the lower combed outline, with rounded rear locks and a smoother low-glare fade. Curly top shares the corrected fade. Side part has an opposite relaxed diagonal sweep, softer forward curve and restrained wave variation. Black is neutral#303030 across all hair and male facial hair, replacing purple-biased#28233A.\n\nUse Compare257 for the immediate previous shapes and palette. Original raised B remains a bare-Taper comparison. Independent feature/color selection, rotation/zoom and fixed studio remain. All authored hats, four hair colors, all skin tones and hidden covered hair checked.\n\nPackage:72 ordinary GLBs, three packed reference assemblies,30 matched120/512 color/Z pairs, technical/handoff reports. Main locks remain opaque; tips and fade use vertex opacity. Correct native blending and phone performance remain separate qualification work. New258 artwork awaits owner review.\n',encoding='utf8',newline='\n')
index=D/'index.html';s=index.read_text(encoding='utf-8-sig');s=s.replace('<figure><a href="references/curly-top-angles258.jpg">','<figure><a href="references/sidepart-angles258.jpg"><img src="references/sidepart-angles258.jpg" alt="Side part rotation check" loading="lazy"></a><figcaption>Side part</figcaption></figure><figure><a href="references/curly-top-angles258.jpg">');s=s.replace('Selected B comparison / small portraits / covered fits','Before and after / small portraits / covered fits / Black');s=s.replace('B and higher-fade Taper','Taper before and after');s=s.replace('<a href="references/small258.jpg">','<a href="references/sidepart-comparison258.jpg">Side part before and after</a><a href="references/sidepart-covered258.jpg">Side part with headgear</a><a href="references/black-comparison258.jpg">Black before and after</a><a href="references/black-Masculine258.jpg">Black masculine styles</a><a href="references/black-Feminine258.jpg">Black feminine styles</a><a href="references/black-facial-hair258.jpg">Black facial hair</a><a href="references/small258.jpg">');index.write_text(s,encoding='utf8',newline='\n')
print('FINISH258_COMPLETE',len(tech),'newGLBs',len(deps),'retainedGLBs',shape['taper_top_lower_by'],'lower')
