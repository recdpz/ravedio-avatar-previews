from pathlib import Path
import json,shutil,hashlib,struct,io
from PIL import Image
P=Path(__file__).parent;R=P.parent/'floating138/mobile-preview';D=R/'249'
fits=json.loads((P/'fits249.json').read_text());proof=json.loads((P/'proof249.json').read_text());tops=json.loads((P/'top-proof249.json').read_text());assemblies=json.loads((P/'assemblies249.json').read_text());fields=json.loads((P/'fields-proof249.json').read_text())
assert len(fits)==112 and len(proof)==16 and len(tops)==22 and len(assemblies)==2
depth=json.loads((D/'depth249.json').read_text());assert len(depth['matched_color_and_depth'])==4 and all(x['geometry_revision']==249 for x in depth['matched_color_and_depth'])
assert all(len(x['full_angles'])==len(x['enlarged_angles'])==7 for x in proof.values())
assert all(x['front_crossing_changes']==0 for x in fields)
for b,item in assemblies.items():
 assert item['packed'] and all(x['packed'] for x in item['settings']['images']);shutil.copy2(item['source'],D/'assemblies'/f'{b}-pashmina249.blend')
for f in (P/'fixtures').glob('*.png'):shutil.copy2(f,D/'references'/f.name)
for b in ['Feminine','Masculine']:
 for f in (P/'review2').glob(b+'-*-new-*.png'):shutil.copy2(f,D/'references'/f.name)
for f in (P/'review2').glob('Feminine-*-cloth-hidden-*.png'):shutil.copy2(f,D/'references'/f.name)
for f in (P/'review2').glob('Feminine-*-uncovered-*.png'):shutil.copy2(f,D/'references'/f.name)
for f in (P/'review2').glob('*-review249.jpg'):shutil.copy2(f,D/'references'/f.name)
shutil.copy2(P/'review2/identity-comparison249.jpg',D/'references/identity-comparison249.jpg')
for f in (P/'fixtures').glob('*-skin*-portrait249-front.png'):
 for size in [32,48,64]:Image.open(f).resize((size,size),Image.Resampling.LANCZOS).save(D/'references'/(f.stem+'-'+str(size)+'.png'))
technical=[]
for f in sorted((D/'components').glob('*.glb')):
 raw=f.read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);binary=raw[28+n:];ext=g.get('extensionsUsed',[])
 assert not any(x in ext for x in ['KHR_draco_mesh_compression','EXT_meshopt_compression','KHR_mesh_quantization'])
 tris=sum(g['accessors'][p['indices']]['count']//3 if 'indices' in p else g['accessors'][p['attributes']['POSITION']]['count']//3 for m in g['meshes'] for p in m['primitives']);textures=[]
 for im in g.get('images',[]):
  v=g['bufferViews'][im['bufferView']];data=binary[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']];image=Image.open(io.BytesIO(data));textures.append(dict(width=image.width,height=image.height,bytes=len(data)))
 for mat in g.get('materials',[]):
  sheen=mat.get('extensions',{}).get('KHR_materials_sheen',{}).get('sheenColorFactor')
  if 'Headwear' in mat.get('name','') and sheen:assert max(sheen)<=.12001
 technical.append(dict(path='components/'+f.name,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),triangles=tris,materials=len(g.get('materials',[])),textures=textures,extensions=ext,alpha_modes=sorted({m.get('alphaMode','OPAQUE') for m in g.get('materials',[])})))
assert len(technical)==130,len(technical)
cat=json.loads((D/'catalogue249.json').read_text());original=[]
for b in cat['builds']:
 for style,hair in cat['builds'][b]['hair'].items():
  top='open' if b=='Feminine' else 'tank';fit=fits[b+'-'+style+'-'+top]
  if not fit['localized_gathers']:assert cat['fits'][b+'-'+style]['pashmina']['hair']==hair['path'];original.append(b+'-'+style)
assert len(original)==14
review=dict(revision=249,review='self',owner_approval='New249 fits pending',scope='Restore rooted coverage and original hairstyle identity beneath pashmina',original_components_reused=original,localized_gathers=['Feminine ponytail: original free-tail geometry moved to a low actual-head-supported tie; original pulled scalp re-routed to it with visible forehead preserved.','Feminine space buns: original bun pieces lowered behind the head; front/scalp retained.'],passes=['Source comparisons and enlarged construction iterations corrected lower-edge scalloping, hood corner wings and the ponytail nape connection.','Fresh GLBs:16 styles at seven full and seven enlarged angles, plus uncovered/cloth-hidden/before248 front/profile/rear.','22 wardrobe/accessory stress cases at seven angles; matching four-tone small portraits; browser routes and actual cloth-layer visibility.'],protected='Accepted front crossing regions and all body/face/wardrobe/uncovered/other-headwear inputs remain unchanged.',limits='Artwork candidate only. Native fidelity, layer-composition/transparency and phone performance remain unqualified.')
handoff=dict(revision=249,baseline_commit='9cea4e0637473b9b73e9b9ea1c7fa0c7cdc0559a',previous_artwork='cc3d03d9caf726bc0406338a9a60579dba2b3ab4',scope=review['scope'],url='https://recdpz.github.io/ravedio-avatar-previews/249/',selection='pashminaHairFamilies now maps each style to itself; pashminaVariants[build][style][top] selects its authored hood. fits[build-style].pashmina.hair selects intact or locally gathered hair. No new profile bits or runtime physics.',hair='Fourteen covered hairstyles reuse exact original GLBs. Ponytail and buns preserve original materials and free pieces with localized gathers; no generic replacement curtain or clipped eye-level roots.',coordinates='All components retain their shared transforms and positions. glTF conversion only; no independent centering/resizing.',materials='Ordinary uncompressed/unquantized GLBs. Separate recoloring roles and clear frame/lens materials retained. Cloth uses woven texture and linear sheen weight0.12.',details='Each of16 pashmina sprouts is reseated on the final cloth, retaining its clamp. Compare248 restores old hair/cloth/sprout together. Cloth checkbox exposes the real covered hair.',references='assemblies249.json records cameras, studio, packed sources and identical120/512 framing. depth249.json supplies matching assembled color/Z references; it is not a native component-layer bake.',assemblies={b:'assemblies/'+b+'-pashmina249.blend' for b in assemblies},authoring='Two portable assembled scenes have dependencies packed. The112 per-top ordinary GLBs are portable; regenerating every individual authoring fit uses retained local248 source files and249 source/support recipes.',technical='technical249.json',review='review249.json',qualification=review['limits'])
handoff['renderer_limits']='The component GLBs do not include the Blender studio/HDR, camera/light rig, AgX view transform, ray-visibility flags or complete Blender shader graphs. Reproduce the reference using the packed scenes and recorded settings; native visual parity remains a separate gate.'
review['construction_lessons']=['Exported GLB vertex order is not an authoring grid even when vertex counts match. The low ponytail repair uses a bounded rear-surface extension on the actual head, preserving the crown and visible front.','Front-hanging locks are excluded from the covered bulk support; enclosing them would flare the lower hood corners.']
for name,obj in [('technical249.json',technical),('review249.json',review),('handoff249.json',handoff),('assemblies249.json',assemblies),('fits249.json',fits),('proof249.json',proof),('top-proof249.json',tops),('fields-proof249.json',fields)]:
 (D/name).write_text(json.dumps(obj,indent=2)+'\n',encoding='utf8',newline='\n')
for f in P.glob('*.py'):
 if f.name not in ['start249.py','probe249.py','inspect249.py']:shutil.copy2(f,D/'source'/f.name)
shutil.copy2(P/'browser249.cjs',D/'source/browser249.cjs')
(D/'README249.txt').write_text('Ravedio249 - intact hair beneath pashmina\n\nFourteen styles reuse their exact uncovered hair components. The ponytail and buns use localized lower gathers from their original meshes/materials. The hood fits broad hair volume, while accepted front crossing regions stay fixed.112 authored cloth/top fits;16 reseated sprout clips.\n\nCompare248 restores the prior cloth, hair and sprout. Uncheck Cloth to inspect the covered hair without hiding it beneath fabric. Body, face, wardrobe, uncovered assets, other headwear, palette and fixed studio are retained.\n\nIncludes ordinary GLBs, two packed assembly scenes, matching120/512 portraits, four-tone small references and matching assembly color/depth pairs. New shapes await owner review. Native render parity and real-phone performance are separate gates.\n',encoding='utf8',newline='\n')
print('FINISHED249',len(technical),'ordinary GLBs;',len(original),'exact original hairstyles;112 cloth fits;2 packed assemblies')
