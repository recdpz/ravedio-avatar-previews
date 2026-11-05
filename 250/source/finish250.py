from pathlib import Path
import json,shutil,hashlib,struct,io,subprocess,ast
from PIL import Image
P=Path(__file__).parent;R=P.parent/'floating138/mobile-preview';D=R/'250';assert json.loads((P/'pony-root-pending250.json').read_text())['status']=='complete';fits=json.loads((P/'fits250.json').read_text());proof=json.loads((P/'proof250.json').read_text());tops=json.loads((P/'top-proof250.json').read_text());assemblies=json.loads((P/'assemblies250.json').read_text());depth=json.loads((D/'depth250.json').read_text());boundaries=json.loads((P/'boundary250.json').read_text());assert len(boundaries)==128 and all(x['unchanged'] for x in boundaries);assert len(fits)==112 and len(proof)==16 and len(tops)==22 and len(assemblies)==2 and len(depth['matched_color_and_depth'])==4
for b,x in assemblies.items():assert x['packed'];shutil.copy2(x['source'],D/'assemblies'/f'{b}-pashmina250.blend')
for f in (P/'fixtures').glob('*.png'):shutil.copy2(f,D/'references'/f.name)
for f in (P/'review2').glob('*review250.jpg'):shutil.copy2(f,D/'references'/f.name)
shutil.copy2(P/'review2/fit-comparison250.jpg',D/'references/fit-comparison250.jpg')
for b,style in [('Feminine','straight'),('Feminine','curls'),('Feminine','ponytail'),('Masculine','taper'),('Masculine','afro')]:
 for f in (P/'review2').glob(b+'-'+style+'-new-*.png'):shutil.copy2(f,D/'references'/f.name)
for f in (P/'fixtures').glob('*-skin*-portrait250-front.png'):
 for size in [32,48,64]:Image.open(f).resize((size,size),Image.Resampling.LANCZOS).save(D/'references'/(f.stem+'-'+str(size)+'.png'))
technical=[]
for f in sorted((D/'components').glob('*.glb')):
 raw=f.read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);binary=raw[28+n:];ext=g.get('extensionsUsed',[]);assert not any(x in ext for x in ['KHR_draco_mesh_compression','EXT_meshopt_compression','KHR_mesh_quantization']);tex=[]
 for im in g.get('images',[]):
  assert 'bufferView' in im;v=g['bufferViews'][im['bufferView']];data=binary[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']];image=Image.open(io.BytesIO(data));tex.append(dict(width=image.width,height=image.height,bytes=len(data)))
 for material in g.get('materials',[]):
  sheen=material.get('extensions',{}).get('KHR_materials_sheen',{}).get('sheenColorFactor',[])
  if f.name.endswith('headgear.glb') and sheen:assert max(sheen)<=.12001
 technical.append(dict(path='components/'+f.name,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),triangles=sum(g['accessors'][p['indices']]['count']//3 for m in g['meshes'] for p in m['primitives']),materials=len(g.get('materials',[])),textures=tex,extensions=ext,alpha_modes=sorted({m.get('alphaMode','OPAQUE') for m in g.get('materials',[])})))
assert len(technical)==144,len(technical)
cat=json.loads((D/'catalogue250.json').read_text());retained=set()
def scan(x):
 if isinstance(x,dict):
  for v in x.values():scan(v)
 elif isinstance(x,list):
  for v in x:scan(v)
 elif isinstance(x,str) and x.endswith('.glb'):
  f=(D/x).resolve();assert f.is_relative_to(R.resolve()) and f.exists(),x
  if not f.is_relative_to(D.resolve()):retained.add(f)
scan(cat);tree=subprocess.check_output(['git','ls-tree','-r','HEAD'],cwd=R,text=True);blobs={line.split('\t',1)[1]:line.split()[2] for line in tree.splitlines()};deps=[]
for f in sorted(retained):
 raw=f.read_bytes();key=f.relative_to(R).as_posix();assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==blobs[key],key;deps.append(dict(path=key,sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw)))
review=dict(revision=250,review='self',owner_approval='New250 worn combinations pending',scope='Authored covered-hair packing and restrained hood drape across16 styles',passes=['Source seven-angle silhouettes/contact across16 styles; corrected low ponytail departure and Afro crown penetration before final review.','Fresh final GLBs at seven enlarged angles, matched249 anchor views and cloth-hidden coverage views.','22 wardrobe/accessory stress assemblies plus four skin tones and small portraits; local browser feature/visibility/recolor checks.'],browser='browser250.json',enlarged_browser='close250.json',protected='Accepted front crossings/joins, all body/face/wardrobe, uncovered styles, other headwear, materials, studio and shared coordinates.',limits='Artwork owner-review candidate. Native fidelity, transparency/layer composition and actual-phone performance remain separate.')
handoff=dict(revision=250,baseline_commit='3228f60f6402b0ce0104ce83eb656a975d828ef3',scope=review['scope'],selection='Existing independent selectors. pashminaVariants[build][style][top] chooses the cloth; fits[build-style].pashmina chooses its authored covered hair. Compare249 restores all previous cloth/hair/sprout components together. Cloth hides fabric for inspection.',method='Three broad support allowances: compact, draped and full. Concealed hair is gathered outside the actual head with continuous original locks; exposed styling/material is retained. The original ponytail bundle is rigidly reoriented beneath a raised continuous rear hem. No punched holes, runtime physics, new profile bits or generic replacement curtain.',protection=review['protected'],coordinates='Shared transforms and origins retained. No independent centering/resizing or automatic mesh/material merging across selectable components.',source='Two portable packed assemblies and ordinary uncompressed/unquantized GLBs. Per-top regeneration uses retained249 native sources and fields via source/common250.py; original inputs are unchanged.',rendering='Packed Blender studio, recorded camera/light/exposure and color management are the reference. GLBs do not transfer the studio/HDR, AgX transform, ray-visibility flags or complete shader graph. Native parity requires comparison.',references='assemblies250.json and depth250.json. Color/Z regenerated together from the same final geometry/camera/version. These are assembled reference depth pairs, not native component-layer maps.',transparency='Existing frame/lens separation and clear thin-opacity lenses retained; clear glass is not transmission/refraction. Geometry reduction cannot establish lens correctness; native transparency remains unqualified.',technical='technical250.json',review='review250.json',qualification=review['limits'])
for name,obj in [('boundaries250.json',boundaries),('technical250.json',technical),('fits250.json',fits),('proof250.json',proof),('top-proof250.json',tops),('assemblies250.json',assemblies),('review250.json',review),('handoff250.json',handoff),('dependencies250.json',dict(baseline_commit=handoff['baseline_commit'],retained_glbs=deps))]:(D/name).write_text(json.dumps(obj,indent=2)+'\n',encoding='utf8',newline='\n')
for f in P.glob('*.py'):
 ast.parse(f.read_text(encoding='utf-8-sig'))
 if f.name not in ['debug250.py','tail-probe250.py']:shutil.copy2(f,D/'source'/f.name)
for f in P.glob('*.cjs'):shutil.copy2(f,D/'source'/f.name)
(D/'README250.txt').write_text('Ravedio250 - authored worn hair and pashmina\n\nCovered hair and restrained cloth drape are authored together across16 hairstyles and112 clothing fits. Exposed style/material and original uncovered assets remain preserved. The low ponytail exits beneath the continuous hem. Compare249 restores the previous fit; Cloth reveals the covered hair.\n\nTwo packed final-GLB assemblies, matched120/512 portraits, four-tone small references and matched color/Z pairs are included. Technical counts and retained input hashes are recorded. New artwork awaits owner review. Native fidelity and phone performance remain separate.\n',encoding='utf8')
q=json.loads((P/'progress250.json').read_text());q.update(status='Export review and handoff complete; browser/publication remaining',styles=16,top_fits=112,sprouts=16,packed_assemblies=2,matched_color_depth_pairs=4,retained_glbs=len(deps));(P/'progress250.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf8');print('FINISH250',len(technical),'ordinary GLBs;',len(deps),'unchanged retained components')
