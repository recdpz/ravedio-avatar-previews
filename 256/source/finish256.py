from pathlib import Path
import json,struct,hashlib,shutil,subprocess,ast,io
from PIL import Image,ImageOps,ImageDraw
P=Path(__file__).parent;R=P.parent/'floating138/mobile-preview';D=R/'256';baseline='511cb1d204bbb74ef1fd61c77e78c2aea3ce452a';c=json.loads((D/'catalogue256.json').read_text());browser=json.loads((P/'browser256.json').read_text());assert len(browser['checks'])==97 and not browser['errors'] and not browser['http'];refs=set()
def scan(x):
 if isinstance(x,dict):
  for v in x.values():scan(v)
 elif isinstance(x,list):
  for v in x:scan(v)
 elif isinstance(x,str) and x.endswith('.glb'):refs.add((D/x).resolve())
scan(c)
for f in (D/'components').glob('*.glb'):
 if f.resolve() not in refs:
  assert f.resolve().parent==(D/'components').resolve() and '256' in f.name;f.unlink()
assert len(list((D/'components').glob('*.glb')))==50
for st in ['taper','curly-top']:
 shutil.copy2(P/f'{st}-final-review256.jpg',D/'references'/f'{st}-angles256.jpg');shutil.copy2(P/f'{st}-covered-review256.jpg',D/'references'/f'{st}-covered256.jpg')
 # Exported253 versus256, using identical camera and color.
 im=Image.new('RGB',(1200,620),'#29394c');d=ImageDraw.Draw(im)
 for row,kind in enumerate(['before','none']):
  for col,angle in enumerate(['front','profile','rear','top']):
   f=P/'browser-verified'/(f'final-selected-B-{angle}.png' if st=='taper' and row==0 else f'final-{st}-{kind}-{angle}.png');pic=Image.open(f).convert('RGBA');bg=Image.new('RGBA',pic.size,'#29394c');bg.alpha_composite(pic);pic=ImageOps.contain(bg.convert('RGB'),(300,285));im.paste(pic,(col*300+(300-pic.width)//2,row*310));d.text((col*300+5,row*310+288),('B original fade' if st=='taper' and row==0 else '254' if row==0 else '256 higher fade')+' '+angle,fill='white')
 im.save(D/'references'/f'{st}-comparison256.jpg',quality=94)
tech=[]
for f in sorted((D/'components').glob('*.glb')):
 raw=f.read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);b=raw[28+n:];used={p['material'] for m in g['meshes'] for p in m['primitives']};assert not set(g.get('extensionsUsed',[]))&{'KHR_draco_mesh_compression','EXT_meshopt_compression','KHR_mesh_quantization'};textures=[]
 for im in g.get('images',[]):
  v=g['bufferViews'][im['bufferView']];blob=b[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']];pic=Image.open(io.BytesIO(blob));textures.append(dict(size=[pic.width,pic.height],bytes=len(blob)))
 tech.append(dict(path=f.relative_to(D).as_posix(),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),triangles=sum(g['accessors'][p['indices']]['count']//3 for m in g['meshes'] for p in m['primitives']),materials=len(used),primitives=sum(len(m['primitives']) for m in g['meshes']),textures=textures,alpha_modes=sorted({g['materials'][i].get('alphaMode','OPAQUE') for i in used}),transmission=[],compressed=False,quantized=False))
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()==baseline;tree=subprocess.check_output(['git','ls-tree','-r','HEAD'],cwd=R,text=True);blobs={line.split('\t',1)[1]:line.split()[2] for line in tree.splitlines()};deps=[]
for f in sorted(refs):
 assert f.exists() and f.is_relative_to(R.resolve()),f
 if f.is_relative_to(D.resolve()):continue
 raw=f.read_bytes();key=f.relative_to(R).as_posix();assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==blobs[key],key;deps.append(dict(path=key,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
assemblies=json.loads((P/'assemblies256.json').read_text());(D/'assemblies').mkdir(exist_ok=True)
for r in assemblies.values():shutil.copy2(r['source'],D/r['packed_path'])
review=dict(revision=256,review='self',owner_direction='Selected recovered B with fuller sides and original separate swept locks; extend the lower fade slightly higher.',scope='Taper and Curly top side fades, all worn fits and colors.',passes=['Reconstructed and preserved the earlier separate-lock drafts after254 was rejected. Owner chose B.','Increased fade span from0.30 to0.38 within the unchanged lower footprint. Taper top positions, normals, UVs, indices and other attributes match selected B exactly.','Corrected exported texture-border sampling only on the fade textures, preserving B long-hair sampling. No source-geometry changes in the export pass.','Fresh actual-GLB eight-angle, color, skin and headgear checks; comparison against B and254; small portraits and additional covered/cloth-hidden views.'],browser_checks=len(browser['checks']),approval='B direction selected; new256 higher fade awaits owner review.',limits='Artwork fidelity exports. Native/phone rendering and performance acceptance remain separate.')
handoff=dict(revision=256,baseline_commit=baseline,selected_basis='../255/drafts/B/source.blend',changed_styles=['taper','curly-top'],geometry='B separate swept locks are preserved exactly in bare Taper. The side fade grows upward by increasing its normalized span0.30 to0.38; its lower boundary and footprint are unchanged. Curly top retains its existing crown and uses the same side treatment. Other models, body/face/clothing, headgear shapes, palettes and fixed studio are retained.',rendering='Side coverage is opacity from a neutral RGB/alpha texture under BLEND, not transmission or refraction. Longer hair is OPAQUE. A nearest-opaque portrait prototype cannot reproduce partial side coverage without alpha compositing or an equivalent faithful baked solution. Do not substitute254 modeled fibers. Ordinary GLBs contain no compression or quantization.',controls='Independent feature/color controls remain. Compare B original fade is available for bare Taper, with a matching Ombré baseline. It is mutually exclusive with Compare254 and clears when choosing an unsupported hair/headgear state. Hair and facial-hair recoloring retain current palette behavior.',exports='16 current hair fits,17 Ombré files including the selected-B baseline, one selected-B default baseline and16 seated sprouts. Hair remains independently addressable in shared coordinates; headgear shapes are unchanged.',source='Two packed reference assemblies imported from final GLBs, twelve matched120/512 color and32-bit float Z pairs. Original selected B and the other recovered snapshots remain separately preserved in255. Each new authored/export pass has its own source, code, settings and renders. Feminine253 sources remain unchanged.',depth='Color and Z share geometry/camera/version and render. Partial-alpha references use the recorded0.5 alpha threshold; these are assembled references, not a complete component-alpha compositing solution. Regenerate component colors and depth together for any changed geometry.',lighting='Blender studio/environment, camera, exposure and view transform are recorded in assemblies256.json. Those renderer effects do not transfer as identical GLB lighting; native appearance still requires direct comparison.',technical='technical256.json',review='review256.json',profile_contract='No profile-byte assignments or product-repository changes.',qualification=review['limits'])
for name,obj in [('technical256.json',tech),('assemblies256.json',assemblies),('review256.json',review),('handoff256.json',handoff),('dependencies256.json',dict(baseline_commit=baseline,retained_glbs=deps)),('browser256.json',browser),('ombre256.json',json.loads((P/'ombre256.json').read_text())),('fits256.json',json.loads((P/'pass2/fits256.json').read_text())),('top-preservation256.json',json.loads((P/'top-preservation256.json').read_text()))]:
 (D/name).write_text(json.dumps(obj,indent=2)+'\n',encoding='utf8',newline='\n')
(D/'source').mkdir(exist_ok=True)
for name in ['build256.py','export256.py','fits256.py','package256.py','ombre256.py','reference256.py','browser256.cjs','extra-angles256.cjs','finish256.py']:
 f=P/name
 if f.suffix=='.py':ast.parse(f.read_text(encoding='utf-8-sig'))
 shutil.copy2(f,D/'source'/name)
shutil.copy2(P/'inputs/settings.json',D/'selected-settings256.json')
(D/'README256.txt').write_text('Ravedio256 - Selected B with higher fade\n\nOwner selected the fuller sides and original separate swept locks of recovered B. Its top shape is preserved; the lower faded area now extends higher, with span0.30 to0.38 and an unchanged lower footprint. The same side treatment is applied to Curly top. All worn fits, current colors and Ombré are included. Compare B original fade directly on bare Taper; Compare254 shows the rejected published version.\n\nOriginal recovered drafts remain separately preserved in255. New passes retain immutable source/GLB/settings/render checkpoints. Two packed reference assemblies and twelve matched color/Z pairs accompany ordinary uncompressed GLBs. Fade opacity needs proper alpha handling; it is not transmission. Native/phone qualification remains separate.\n',encoding='utf8',newline='\n')
print('FINISH256',len(tech),'new GLBs;',len(deps),'retained dependencies;',len(browser['checks']),'checks')
