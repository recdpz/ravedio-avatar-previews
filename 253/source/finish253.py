from pathlib import Path
import json,struct,hashlib,io,shutil,math,subprocess,ast
from PIL import Image,ImageDraw,ImageOps
P=Path(__file__).parent;R=P.parent/'floating138/mobile-preview';D=R/'253';c=json.loads((D/'catalogue253.json').read_text());browser=json.loads((P/'browser253.json').read_text());assert not browser['errors'] and not browser['http'];records=json.loads((P/'ombre253.json').read_text());assert len(records)==128
for b,bc in c['builds'].items():
 for st in bc['hair']:
  im=Image.new('RGB',(1000,278),'#29394c');d=ImageDraw.Draw(im)
  for i,angle in enumerate(['front','profile','rear','top']):
   f=P/'browser'/f'{b}-{st}-none-{angle}.png';assert f.exists(),f;pic=Image.open(f).convert('RGBA');bg=Image.new('RGBA',pic.size,'#29394c');bg.alpha_composite(pic);pic=ImageOps.contain(bg.convert('RGB'),(250,250));im.paste(pic,(i*250+(250-pic.width)//2,0));d.text((i*250+8,254),angle,fill='white')
  im.save(D/'references'/f'{b}-{st}-ombre253.jpg',quality=91)
(D/'assemblies').mkdir(exist_ok=True);assemblies=json.loads((P/'assemblies253.json').read_text())
for b,r in assemblies.items():shutil.copy2(r['source'],D/r['packed_path'])
tech=[]
for f in sorted((D/'components').glob('*.glb')):
 raw=f.read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);data=raw[28+n:];used={p['material'] for m in g['meshes'] for p in m['primitives']};ext=g.get('extensionsUsed',[]);assert not set(ext)&{'KHR_draco_mesh_compression','EXT_meshopt_compression','KHR_mesh_quantization'};images=[]
 for image in g.get('images',[]):
  v=g['bufferViews'][image['bufferView']];blob=data[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']];pic=Image.open(io.BytesIO(blob));images.append(dict(size=[pic.width,pic.height],bytes=len(blob)))
 tech.append(dict(path=f.relative_to(D).as_posix(),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),triangles=sum(g['accessors'][p['indices']]['count']//3 for m in g['meshes'] for p in m['primitives']),materials=len(used),primitives=sum(len(m['primitives']) for m in g['meshes']),textures=images,alpha_modes=sorted({g['materials'][i].get('alphaMode','OPAQUE') for i in used}),transmission=[g['materials'][i]['name'] for i in used if g['materials'][i].get('extensions',{}).get('KHR_materials_transmission',{}).get('transmissionFactor',0)>0]))
retained=set()
def scan(x):
 if isinstance(x,dict):
  for v in x.values():scan(v)
 elif isinstance(x,list):
  for v in x:scan(v)
 elif isinstance(x,str) and x.endswith('.glb'):
  f=(D/x).resolve();assert f.exists() and f.is_relative_to(R.resolve()),x
  if not f.is_relative_to(D.resolve()):retained.add(f)
scan(c);tree=subprocess.check_output(['git','ls-tree','-r','HEAD'],cwd=R,text=True);blobs={line.split('\t',1)[1]:line.split()[2] for line in tree.splitlines()};deps=[]
for f in sorted(retained):
 raw=f.read_bytes();key=f.relative_to(R).as_posix();assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==blobs[key],key;deps.append(dict(path=key,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
review=dict(revision=253,review='self',scope='Replace Highlights with Ombré across16 hairstyles, all authored worn variants and both garment-dependent twin-braid length families.',owner_approval='New color awaits review.252 geometry is retained, not newly approved by this change.',passes=['Initial full-color pilot: reduced overly pale coil tips and corrected the ponytail bundle progression.','Second actual-GLB rotation pass across all16 styles, all headwear selections, braid/top cases, four skin tones and other colors.','Ordinary export integrity checks preserve every geometry/normal/index/alpha value, transforms and secondary texture coordinates. Lossless unused-buffer cleanup adds no compression or quantization.'],browser_checks=len(browser['checks']),glb_color_variants=len(records),geometry_changes=False,limits='Artwork color review; native renderer/portrait composition and phone workload qualification remain separate.')
handoff=dict(revision=253,baseline_commit='423249a53ebb5afb2548542d133a99bbe6a7f6db',scope=review['scope'],palette_linear_rgb=dict(root=[.145,.062,.034],middle=[.32,.17,.078],ends=[.50,.32,.16]),selection='Highlights is replaced by ombre/Ombré in the same preview menu position; no profile-byte assignment changes. Resolve canonical hair/hairLengths paths via catalogue253.ombre when selected. Other colors resolve the unchanged canonical252 assets. Compare252 displays its previous Highlights color, with identical geometry.',placement='Long locks retain authored root-to-tip progression. Long curls and braided sections use a continuous fall so individual braid pieces never restart the gradient. Ponytail bundles use surface-growth distance from the scalp attachment. Space-bun outer winding and raised short coils lighten progressively. Faded sides remain root-toned; Buzz is intentionally restrained. Facial hair uses the root color.',preservation='No geometry, normals, indices, alpha, transforms, silhouette, fit, body, face, clothing, skin palette or lighting changes. Primary color UV coordinates and base-color atlas are the only authored changes. Separate ties, frames/lenses and other controls remain independent.',exports='128 ordinary, uncompressed and unquantized baked-color GLBs. Secondary UV coordinates/normal maps are preserved. ombre-gradient253.png is the shared authored color ramp. No custom renderer shader is required.',sources='Two packed reference Blender assemblies preserve fixed studio and camera settings, with embedded textures. Full authoring scripts also reference retained earlier inputs. Fair/light and Brown/dark plus skin1 have matched120/512 color/Z exports in depth253.json; camera/framing is identical across these looks.',rendering='The full Blender studio, exposure/view transform and shader graph are not carried by GLB. Ordinary PBR textures, geometry, alpha and supported material extensions transfer; native and lightweight portrait paths require their own faithful comparison.',depth='Color and32-bit float Z are generated in the same render at the same geometry/camera/version. Assembled references are not component occlusion maps or a transparent-lens solution.',technical='technical253.json',review='review253.json',qualification=review['limits'])
refs=dict(appearance_sources=json.loads((P/'plan253.json').read_text())['references'],interpretation='Gradual darker roots to lighter ends, adapted to the retained stylized hair geometry. No source photos copied.')
for name,obj in [('technical253.json',tech),('assemblies253.json',assemblies),('review253.json',review),('handoff253.json',handoff),('ombre253.json',records),('dependencies253.json',dict(baseline_commit=handoff['baseline_commit'],retained_glbs=deps)),('browser253.json',browser),('references253.json',refs)]:
 (D/name).write_text(json.dumps(obj,indent=2)+'\n',encoding='utf8',newline='\n')
(D/'source').mkdir(exist_ok=True)
for name in ['package253.py','ombre253.py','reference253.py','browser253.cjs','compact253.py','finish253.py']:
 f=P/name
 if f.suffix=='.py':ast.parse(f.read_text(encoding='utf-8-sig'))
 shutil.copy2(f,D/'source'/name)
(D/'README253.txt').write_text('Ravedio253 - Ombré hair\n\nHighlights is replaced by Ombré for all16 hairstyles and their worn variants. Chestnut roots blend through caramel into honey-beige ends; shorter cuts use a restrained transition. Geometry, face/body, other colors, wardrobe and lighting are unchanged from252.\n\n128 ordinary baked-color GLBs, independent selectors, a previous-color comparison, two packed Blender reference scenes, matched120/512 color/Z pairs and technical metadata are included. This is an artwork color review, not native/phone qualification.\n',encoding='utf8',newline='\n')
print('FINISH253',len(tech),'color GLBs;',len(deps),'retained dependencies;',len(browser['checks']),'browser checks')
