from pathlib import Path
import json,struct,hashlib,shutil,subprocess,ast,io
from PIL import Image,ImageOps,ImageDraw
P=Path(__file__).parent;R=P.parent/'floating138/mobile-preview';D=R/'254';baseline='85af03e053ae9811af309d7e4ef0c170b7ae905f';c=json.loads((D/'catalogue254.json').read_text());browser=json.loads((P/'browser254.json').read_text());assert len(browser['checks'])==96 and not browser['errors'] and not browser['http'];refs=set()
def scan(x):
 if isinstance(x,dict):
  for v in x.values():scan(v)
 elif isinstance(x,list):
  for v in x:scan(v)
 elif isinstance(x,str) and x.endswith('.glb'):refs.add((D/x).resolve())
scan(c)
for f in (D/'components').glob('*.glb'):
 if f.resolve() not in refs:
  assert f.resolve().parent==(D/'components').resolve() and '254' in f.name;f.unlink()
assert len(list((D/'components').glob('*.glb')))==48
for st in ['taper','curly-top']:
 shutil.copy2(P/f'{st}-final-review254.jpg',D/'references'/f'{st}-angles254.jpg');shutil.copy2(P/f'{st}-covered-review254.jpg',D/'references'/f'{st}-covered254.jpg')
 # Exported253 versus254, using identical camera and color.
 im=Image.new('RGB',(1200,620),'#29394c');d=ImageDraw.Draw(im)
 for row,kind in enumerate(['before','none']):
  for col,angle in enumerate(['front','profile','rear','top']):
   f=P/'browser'/f'final-{st}-{kind}-{angle}.png';pic=Image.open(f).convert('RGBA');bg=Image.new('RGBA',pic.size,'#29394c');bg.alpha_composite(pic);pic=ImageOps.contain(bg.convert('RGB'),(300,285));im.paste(pic,(col*300+(300-pic.width)//2,row*310));d.text((col*300+5,row*310+288),('253' if row==0 else '254')+' '+angle,fill='white')
 im.save(D/'references'/f'{st}-comparison254.jpg',quality=94)
tech=[]
for f in sorted((D/'components').glob('*.glb')):
 raw=f.read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);b=raw[28+n:];used={p['material'] for m in g['meshes'] for p in m['primitives']};assert all(g['materials'][i].get('alphaMode','OPAQUE')=='OPAQUE' for i in used);assert not set(g.get('extensionsUsed',[]))&{'KHR_draco_mesh_compression','EXT_meshopt_compression','KHR_mesh_quantization'};textures=[]
 for im in g.get('images',[]):
  v=g['bufferViews'][im['bufferView']];blob=b[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']];pic=Image.open(io.BytesIO(blob));textures.append(dict(size=[pic.width,pic.height],bytes=len(blob)))
 tech.append(dict(path=f.relative_to(D).as_posix(),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),triangles=sum(g['accessors'][p['indices']]['count']//3 for m in g['meshes'] for p in m['primitives']),materials=len(used),primitives=sum(len(m['primitives']) for m in g['meshes']),textures=textures,alpha_modes=['OPAQUE'],transmission=[],compressed=False,quantized=False))
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()==baseline;tree=subprocess.check_output(['git','ls-tree','-r','HEAD'],cwd=R,text=True);blobs={line.split('\t',1)[1]:line.split()[2] for line in tree.splitlines()};deps=[]
for f in sorted(refs):
 assert f.exists() and f.is_relative_to(R.resolve()),f
 if f.is_relative_to(D.resolve()):continue
 raw=f.read_bytes();key=f.relative_to(R).as_posix();assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==blobs[key],key;deps.append(dict(path=key,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
assemblies=json.loads((P/'assemblies254.json').read_text());(D/'assemblies').mkdir(exist_ok=True)
for r in assemblies.values():shutil.copy2(r['source'],D/r['packed_path'])
review=dict(revision=254,review='self',scope='Taper and Curly top: opaque modeled clipped graduation, blended longer terminals and all covered fits.',passes=['Texture/alpha pilots were rejected: broad tinted band, hard cutoff, isolated grain, repeated rim and rear overhang.','Replaced those pilots with10623 dense rooted laid-over fibers and buried crown coverage. Length/thickness reduce toward the lower edge; no translucent side shell. Refined long endpoints and rear bulk.','Fresh exported-model eight-angle checks for both styles, default and Ombré;28 covered-angle views per style, four skin tones, all hair colors and exact small portraits.','Native source and final imported-GLB references; protected body/face/wardrobe and retained catalogue assets are verified unchanged.'],browser_checks=len(browser['checks']),final_review='Candidate judged improved; owner approval still required.',limits='Fidelity art exports; triangle counts are recorded, not a mobile performance qualification.')
handoff=dict(revision=254,baseline_commit=baseline,changed_styles=['taper','curly-top'],geometry='Opaque rooted laid-over clipped hairs replace uniform translucent coverage. Fibers grow along the actual head surface and shorten/thin toward the boundary. Buried crown coverage ends under dense grown hair. Longer lock terminals are shortened and flattened into the upper side groom; rear overhang reduced.',selection='Independent selectors retained. Default/Black/Blonde use canonical GLBs and recolor material factors; Ombré resolves canonical hair paths through catalogue254.ombre. New Ombré preserves vertex/index/normal/UV buffers; only color attributes and material color factors change.',preservation='All body, face, wardrobe, headgear shapes, fixed studio, palettes, other six masculine and eight feminine hairstyles remain253. Side part has opaque sides and Buzz is a uniform close cut; neither has the affected faded-side construction. Sprout clips are reseated on final hair/headgear support.',exports='16 canonical hair GLBs,16 Ombré counterparts and16 seated sprouts. Ordinary uncompressed/unquantized GLBs in common coordinates. Modeled fade uses OPAQUE materials; no alpha fog, cutout shader or runtime physics.',source='Two packed masculine reference scenes, Taper and Curly top, imported from final ordinary GLBs. All dependencies embedded. Feminine reference remains unchanged at ../253/assemblies/Feminine-assembly253.blend. Authoring scripts reference retained earlier working sources; the packed scenes are portable source checkpoints.',rendering='Blender studio lights/environment, exposure/view transform and renderer effects are recorded with the scenes and do not transfer as the same GLB lighting. PBR geometry/maps/materials transfer; compare faithful native output separately.',depth='12 matched120/512 color and32-bit float Z pairs from the same geometry/camera/render. Existing feminine253 references stay valid because geometry/camera/materials are unchanged. These are assembled references, not component occlusion or lens-transmission maps.',technical='technical254.json',qualification=review['limits'],references=json.loads((P/'plan254.json').read_text())['references'])
for name,obj in [('technical254.json',tech),('assemblies254.json',assemblies),('review254.json',review),('handoff254.json',handoff),('dependencies254.json',dict(baseline_commit=baseline,retained_glbs=deps)),('browser254.json',browser),('ombre254.json',json.loads((P/'ombre254.json').read_text())),('fits254.json',json.loads((P/'fits254.json').read_text()))]:
 (D/name).write_text(json.dumps(obj,indent=2)+'\n',encoding='utf8',newline='\n')
(D/'source').mkdir(exist_ok=True)
for name in ['fade254.py','fits254.py','package254.py','ombre254.py','reference254.py','browser254.cjs','small254.cjs','finish254.py']:
 f=P/name
 if f.suffix=='.py':ast.parse(f.read_text(encoding='utf-8-sig'))
 shutil.copy2(f,D/'source'/name)
(D/'README254.txt').write_text('Ravedio254 - Clean tapered sides\n\nTaper and Curly top now use dense modeled opaque clipped hair, with graduated length/thickness and longer locks blending into the upper sides. The former translucent wash is removed. All seven headgear fits and matching Ombré exports are included. Compare253 restores the previous hair. Other models, colors, face/body/wardrobe and studio are preserved.\n\nSource and exported rotation checks, small portraits, two packed Blender assemblies and12 matched color/Z reference pairs are supplied. Ordinary GLBs retain common coordinates and independent controls. New art requires owner review; native/phone qualification remains separate.\n',encoding='utf8',newline='\n')
html=(D/'index.html').read_text();html=html.replace('<h1>Clean tapered sides</h1><p>Directional clipped hair, a graduated side shape and smoother transitions into the longer top.', '<h1>Clean tapered sides</h1><p>Modeled short hairs graduate in length and thickness, with longer locks blended into the upper sides.');(D/'index.html').write_text(html,encoding='utf8',newline='\n')
print('FINISH254',len(tech),'new GLBs;',len(deps),'retained dependencies;',len(browser['checks']),'checks;',sum(x['bytes'] for x in tech),'GLB bytes')
