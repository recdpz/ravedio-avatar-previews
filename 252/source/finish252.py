from pathlib import Path
import json,struct,hashlib,io,shutil,math,subprocess,ast
from PIL import Image,ImageDraw,ImageOps
P=Path(__file__).parent;R=P.parent/'floating138/mobile-preview';D=R/'252'
for n in ['references','assemblies','source']:(D/n).mkdir(exist_ok=True)
def dump(name,obj):(D/name).write_text(json.dumps(obj,indent=2)+'\n',encoding='utf8',newline='\n')
def board(entries,path,cols=4,cell=280):
 im=Image.new('RGB',(cols*cell,math.ceil(len(entries)/cols)*(cell+24)),'#29394c');d=ImageDraw.Draw(im)
 for i,(file,label) in enumerate(entries):
  if not file.exists():continue
  pic=Image.open(file).convert('RGBA');bg=Image.new('RGBA',pic.size,'#29394c');bg.alpha_composite(pic);pic=ImageOps.contain(bg.convert('RGB'),(cell,cell));x=i%cols*cell;y=i//cols*(cell+24);im.paste(pic,(x+(cell-pic.width)//2,y));d.text((x+6,y+cell+3),label,fill='white')
 im.save(path,quality=91)
styles=list(json.loads((P/'hair252.json').read_text()));angles=['front','threequarter','profile','rightprofile','rear','top','underside']
for st in styles:
 b='Feminine' if st=='straight' else 'Masculine';board([(P/'browser'/f'{b}-{st}-none-{a}.png',a) for a in angles],D/'references'/f'{st}-angles252.jpg')
if not (P/'browser252.json').exists():print('PREPARED_GALLERY252');raise SystemExit(0)
checks=json.loads((P/'browser252.json').read_text());assert not checks['errors'] and not checks['http'];fits=json.loads((P/'fits252.json').read_text());assert len(fits)==56
for st in styles:
 b='Feminine' if st=='straight' else 'Masculine';board([(P/'browser'/f'{b}-{st}-{hat}-{a}.png',hat+' / '+a) for hat in ['cap','beanie','bucket','cowboy','headband','ears','pashmina'] for a in ['front','profile','rear']],D/'references'/f'{st}-fits252.jpg',3,230)
board([(P/'browser'/f'{"Feminine" if st=="straight" else "Masculine"}-{st}-highlights-{a}.png',st+' / '+a) for st in styles for a in ['front','profile']],D/'references/highlights252.jpg',4,240)
assemblies=json.loads((P/'assemblies252.json').read_text())
for b,r in assemblies.items():shutil.copy2(r['source'],D/'assemblies'/f'{b}-assembly252.blend')
for f in (P/'fixtures').glob('*.png'):
 shutil.copy2(f,D/'references'/f.name)
 if '-skin' in f.name:
  for size in [32,48,64]:Image.open(f).resize((size,size),Image.Resampling.LANCZOS).save(D/'references'/(f.stem+'-'+str(size)+'.png'))
technical=[]
for f in sorted((D/'components').glob('*.glb')):
 raw=f.read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);binary=raw[28+n:];ext=g.get('extensionsUsed',[]);assert not set(ext)&{'KHR_draco_mesh_compression','EXT_meshopt_compression','KHR_mesh_quantization'};textures=[]
 for x in g.get('images',[]):
  v=g['bufferViews'][x['bufferView']];data=binary[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']];im=Image.open(io.BytesIO(data));textures.append(dict(dimensions=[im.width,im.height],bytes=len(data)))
 used={p['material'] for m in g['meshes'] for p in m['primitives']};technical.append(dict(path='components/'+f.name,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),triangles=sum(g['accessors'][p['indices']]['count']//3 for m in g['meshes'] for p in m['primitives']),materials=len(used),primitives=sum(len(m['primitives']) for m in g['meshes']),textures=textures,extensions=ext,alpha_modes=sorted({g['materials'][i].get('alphaMode','OPAQUE') for i in used}),transmission=[g['materials'][i].get('name') for i in used if g['materials'][i].get('extensions',{}).get('KHR_materials_transmission',{}).get('transmissionFactor',0)>0]))
c=json.loads((D/'catalogue252.json').read_text());retained=set()
def scan(x):
 if isinstance(x,dict):
  for v in x.values():scan(v)
 elif isinstance(x,list):
  for v in x:scan(v)
 elif isinstance(x,str) and x.endswith('.glb'):
  f=(D/x).resolve();assert f.is_relative_to(R.resolve()) and f.exists(),x
  if not f.is_relative_to(D.resolve()):retained.add(f)
scan(c);tree=subprocess.check_output(['git','ls-tree','-r','HEAD'],cwd=R,text=True);blobs={line.split('\t',1)[1]:line.split()[2] for line in tree.splitlines()};deps=[]
for f in sorted(retained):
 raw=f.read_bytes();key=f.relative_to(R).as_posix();assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==blobs[key],key;deps.append(dict(path=key,sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw)))
review=dict(revision=252,review='self',owner_approval='New hair and Highlights await review;251 masculine artwork was rejected.',scope='Seven masculine cuts, feminine Straight root/temple cleanup,56 covered fits, re-seated sprout clips and refined Highlights across the catalogue.',passes=['Private source angle pilots; rejected sparse/brick loc roots, detached front arches, repeated ring curls, spike tips and floating curl pieces.','Fresh final GLB browser rotation: all eight corrected bare styles, each of their seven headwear fits, recolors and four skin tones.','Texture and root corrections after enlarged browser review: dense close-cut normal/pigment detail, grazing internal Straight faces removed, authored lock UVs and flow-aligned blended Highlights.'],protected='Retained body, face, wardrobe, four skin tones, fixed studio, shared transforms, selected ponytail/cap and accepted pashmina/headgear. Compare251 geometry checks protect anatomy, face and wardrobe.',browser_checks=len(checks['checks']),covered_fits=len(fits),limits='Artwork correction candidate; technical checks are not owner art approval. Native renderer, transparency composition and phone workload performance remain separate qualifications.')
handoff=dict(revision=252,baseline_commit='14e8b86f01c6db22da33b2f9e63775f07dd8f70b',scope=review['scope'],art_status=review['owner_approval'],selection='Independent feature selectors retained. fits[build-style][headwear] chooses authored hair with the retained headgear. Existing per-top pashmina and twin-braid length selectors are retained. Sprout clips are re-seated on changed hair/fits.',coordinates='Common coordinates and transforms unchanged. Do not center, normalize bounds or independently scale components. Bodies, face and clothing are retained byte-for-byte; compare mode verifies their loaded geometry.',geometry='Continuous close-cut surface rather than sparse particles. Flow and Middle part use a shared authored growth field from part to hem, with coherent coverage and curved growth ridges. Locs use short consistent sections. Afro uses compact irregular coil relief; Curly top uses broad sculpted curls and close sides. No runtime physics.',highlights='Ordinary embedded PNG base-color textures follow authored lock flow UVs or a smooth local centerline field for retained legacy components. Brown roots blend into caramel/honey ribbons. Base color uses TEXCOORD_0; previous UV sets are preserved at the next indices and existing maps are updated. Highlights variants keep their own color; skip uniform runtime recolor. Preserve COLOR_0 alpha and tonal shading. Groom uses the brown base. Geometry position buffers are verified unchanged against their canonical sources.',transparency='Only genuinely faded/clipped hair coverage uses BLEND plus vertex alpha. Dense hair is OPAQUE. This is opacity coverage, not transmission or refraction. Clear lenses remain retained thin-opacity panes with no facial blur. Do not infer all transparency behavior from alphaMode alone.',sources='Two packed final-GLB Blender assemblies and matched120/512 front portraits are included, plus four-tone small-size references. Packed scenes contain their dependencies. Full generator regeneration also uses retained earlier authoring inputs referenced by the source scripts; those inputs are not silently replaced by this package.',rendering='Packed Blender camera, fixed studio, exposure and color-management metadata are recorded. GLB transfers geometry, ordinary PBR materials, textures and alpha; it does not carry the complete Blender node graph, studio environment, AgX view transform or ray-visibility behavior. Browser lighting is unchanged. Re-test normal-map secondary UV support in native renderers.',depth='depth252.json regenerates color and Z together from identical geometry/camera/version. These assembled Z references are not a native component occlusion bake or an alpha/lens composition solution.',technical='technical252.json',review='review252.json',qualification=review['limits'])
for name,obj in [('technical252.json',technical),('assemblies252.json',assemblies),('review252.json',review),('handoff252.json',handoff),('dependencies252.json',dict(baseline_commit=handoff['baseline_commit'],retained_glbs=deps)),('fits252.json',fits),('highlights252.json',json.loads((P/'highlights252.json').read_text())),('browser252.json',checks)]:dump(name,obj)
for name in ['common252.py','hair252.py','fits252.py','highlights252.py','package252.py','assemblies252.py','depth252.py','finish252.py','browser252.cjs']:
 f=P/name
 if f.exists():
  if f.suffix=='.py':ast.parse(f.read_text(encoding='utf-8-sig'))
  shutil.copy2(f,D/'source'/name)
(D/'README252.txt').write_text('Ravedio252 - hair corrections\n\nSeven masculine cuts corrected/rebuilt, Straight temple roots cleaned,56 covered fits updated, sprout clips re-seated, and Highlights rebuilt using flow-aligned blended textures. Compare251 and independent feature/color selectors retained.\n\nBody, face, clothing, palette and fixed lighting retained. Packed sources, ordinary GLBs, matched portrait references and technical metadata included. New artwork awaits owner review; native/phone qualification remains separate.\n',encoding='utf8',newline='\n')
print('FINISH252',len(technical),'new GLBs',len(deps),'retained dependencies',len(checks['checks']),'browser checks')
