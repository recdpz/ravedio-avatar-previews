from pathlib import Path
import json,struct,hashlib,shutil,subprocess,io,ast
from PIL import Image,ImageOps,ImageDraw
P=Path(__file__).parent;R=P.parent/'floating138/mobile-preview';D=R/'257';baseline='a02e603fc491dc76424a360ecfd6bbd6360054ae';c=json.loads((D/'catalogue257.json').read_text());browser=json.loads((P/'browser257.json').read_text());extra=json.loads((P/'extra-angles257.json').read_text());assert len(browser['checks'])==97 and not browser['errors'] and not browser['http'];assert extra['additionalExportedViews']==60 and not extra['errors'];assert len(list((P/'browser-final').glob('final-*.png')))==180
shape=json.loads((P/'shape257.json').read_text());assert shape['upper_B_shape_preserved'];assert len(json.loads((D/'depth257.json').read_text())['pairs'])==12
refs=set()
def scan(x):
 if isinstance(x,dict):
  for v in x.values():scan(v)
 elif isinstance(x,list):
  for v in x:scan(v)
 elif isinstance(x,str) and x.endswith('.glb'):refs.add((D/x).resolve())
scan(c);assert len(list((D/'components').glob('*.glb')))==48
for st in ['taper','curly-top']:
 shutil.copy2(P/f'{st}-final-review257.jpg',D/'references'/f'{st}-angles257.jpg');shutil.copy2(P/f'{st}-covered-review257.jpg',D/'references'/f'{st}-covered257.jpg')
 im=Image.new('RGB',(1200,620),'#29394c');draw=ImageDraw.Draw(im)
 for row,kind in enumerate(['before','none']):
  for col,angle in enumerate(['front','profile','rear','top']):
   pic=Image.open(P/'browser-final'/f'final-{st}-{kind}-{angle}.png').convert('RGBA');bg=Image.new('RGBA',pic.size,'#29394c');bg.alpha_composite(pic);pic=ImageOps.contain(bg.convert('RGB'),(300,285));im.paste(pic,(col*300+(300-pic.width)//2,row*310));draw.text((col*300+5,row*310+288),('256 textured fade' if row==0 else '257 smooth / blended')+' '+angle,fill='white')
 im.save(D/'references'/f'{st}-comparison257.jpg',quality=94)
im=Image.new('RGB',(800,350),'#29394c');draw=ImageDraw.Draw(im)
for i,(st,color,skin) in enumerate((st,color,skin) for st in ['taper','curly-top'] for color in ['default','ombre'] for skin in ['0','3']):
 pic=Image.open(P/'browser-final'/f'final-{st}-{color}-skin{skin}-small120.png').convert('RGBA');assert pic.size==(120,120);bg=Image.new('RGBA',pic.size,'#29394c');bg.alpha_composite(pic);x=i%4*200;y=i//4*175;im.paste(bg.convert('RGB'),(x+40,y));draw.text((x+8,y+128),st+' '+color+' skin'+skin,fill='white')
im.save(D/'references/small257.jpg',quality=95)
tech=[]
for f in sorted((D/'components').glob('*.glb')):
 raw=f.read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);binary=raw[28+n:];used={p['material'] for m in g['meshes'] for p in m['primitives']};assert not set(g.get('extensionsUsed',[]))&{'KHR_draco_mesh_compression','EXT_meshopt_compression','KHR_mesh_quantization'};textures=[]
 for img in g.get('images',[]):
  v=g['bufferViews'][img['bufferView']];blob=binary[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']];pic=Image.open(io.BytesIO(blob));textures.append(dict(size=[pic.width,pic.height],bytes=len(blob)))
 tech.append(dict(path=f.relative_to(D).as_posix(),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),triangles=sum(g['accessors'][p['indices']]['count']//3 for m in g['meshes'] for p in m['primitives']),materials=len(used),primitives=sum(len(m['primitives']) for m in g['meshes']),textures=textures,alpha_modes=sorted({g['materials'][i].get('alphaMode','OPAQUE') for i in used}),transmission=[],compressed=False,quantized=False))
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()==baseline;tree=subprocess.check_output(['git','ls-tree','-r','HEAD'],cwd=R,text=True);blobs={line.split('\t',1)[1]:line.split()[2] for line in tree.splitlines()};deps=[]
for f in sorted(refs):
 assert f.exists() and f.is_relative_to(R.resolve()),f
 if f.is_relative_to(D.resolve()):continue
 raw=f.read_bytes();key=f.relative_to(R).as_posix();assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==blobs[key],key;deps.append(dict(path=key,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
assemblies=json.loads((P/'assemblies257.json').read_text())
for row in assemblies.values():shutil.copy2(row['source'],D/row['packed_path'])
review=dict(revision=257,scope='Selected B silhouette with214-style terminal thinning and smooth faded sides plus small sculpted direction',owner_status='New257 pending owner review',source_review='Pass1 regular dash pattern rejected; pass2 strokes refined; exported alpha-overlap issue fixed in pass3 by retaining opaque cores and using alpha only on terminal sections',protected='Upper B lock positions verified exact; only terminal geometry changes. Shared coordinates, face, body, clothing, other hairstyles, headgear and palettes unchanged.',exported_visual_views=180,covered_visual_views=112,cloth_hidden_views=4,exact120px_images=8,local_browser_checks=97,extra_angle_checks=extra,limits='Artwork candidate. Native renderer/portrait alpha composition and phone performance remain unqualified.')
handoff=dict(revision=257,baseline_commit=baseline,selected_basis='../256/',changed_styles=['taper','curly-top'],geometry='B upper lock shape remains exact. Only terminal portions thin and settle into the fade. Smooth fitted side field uses vertex alpha; small flattened 3D directional marks shorten and fade toward skin. No grain coverage atlas.',rendering='Long-hair cores remain OPAQUE to preserve overlap. Only terminal sections and faded sides use BLEND opacity; there is no transmission/refraction. Preserve vertex COLOR_0 alpha and material separation. A nearest-opaque portrait approach needs faithful alpha composition or a matched bake.',coordinates='Components retain their shared coordinates and independent feature/color selection; no per-part recentering.',colors='Current hair colors and Ombré retained. New Ombré files preserve vertex opacity, geometry, normals, indices, UVs and transforms.',source='Two packed final-GLB reference assemblies; twelve matched120/512 color and32-bit Z pairs. Each source iteration is separately frozen locally.',depth='Color/Z pairs use identical geometry/camera/version; recorded alpha threshold0.5. These assembled references are not a complete component-occlusion bake. Regenerate both when geometry changes.',lighting='Fixed studio/camera/exposure/view transform recorded in assemblies257.json. Blender lighting/color-management effects do not transfer identically through GLB.',exports='48 new ordinary uncompressed GLBs:16 hair fits,16 Ombré variants and16 seated sprout fits. Other catalogue assets are reused unchanged.',controls='Compare256 shows the preceding textured fade and unthinned tips. Compare B original fade remains available for bare Taper.',technical='technical257.json',review='review257.json',qualification=review['limits'],profile_contract='No profile bytes or product repositories changed.')
for name,obj in [('technical257.json',tech),('assemblies257.json',assemblies),('review257.json',review),('handoff257.json',handoff),('dependencies257.json',dict(baseline_commit=baseline,retained_glbs=deps)),('browser257.json',browser),('extra-angles257.json',extra),('ombre257.json',json.loads((P/'ombre257.json').read_text())),('fits257.json',json.loads((P/'pass3/fits257.json').read_text())),('shape257.json',shape),('selected-settings257.json',json.loads((P/'pass3/settings.json').read_text()))]:
 (D/name).write_text(json.dumps(obj,indent=2)+'\n',encoding='utf8',newline='\n')
for name in ['build257.py','refine257.py','core257.py','fits257.py','package257.py','ombre257.py','reference257.py','shape257.py','browser257.cjs','extra-angles257.cjs','finish257.py']:
 f=P/name
 if f.suffix=='.py':ast.parse(f.read_text(encoding='utf-8-sig'))
 shutil.copy2(f,D/'source'/name)
(D/'README257.txt').write_text('Ravedio257 - B shape, blended taper\n\nB upper silhouette and part are preserved. Terminal locks thin and blend into smooth faded sides, with fine sculpted hair-direction marks using214 as a reference. Fade height remains256. Curly top uses the same side treatment. Compare256 directly in the rotatable review; independent feature/color controls and fixed lighting remain.\n\nAll headgear/color fits received final exported all-angle checks, including hidden hair under the pashmina and exact120px portraits. Packed reference assemblies and matched color/Z pairs accompany ordinary uncompressed GLBs. Partial opacity still requires correct native alpha composition; phone qualification remains separate.\n',encoding='utf8',newline='\n')
print('FINISH257_COMPLETE',len(tech),'new GLBs;',len(deps),'exact retained dependencies')
