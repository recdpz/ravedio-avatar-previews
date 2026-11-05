from pathlib import Path
import json,struct,hashlib,math,io
from PIL import Image,ImageDraw
P=Path(__file__).parent;R=P.parent/'floating138/mobile-preview';D=R/'235';cat=json.loads((D/'catalogue235.json').read_text());old=json.loads((R/'234/catalogue234.json').read_text());stats={};protected=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def resolve(p):return (D/p).resolve()
for build,c in cat['builds'].items():
 for field in ['base','shirtlessBase','hot']:
  if field in c:assert resolve(c[field])==(R/'234'/old['builds'][build][field]).resolve();protected.append(build+':'+field)
 for field in ['eyes','mouths','noses','lashes','tops','bottoms']:
  for key,item in c.get(field,{}).items():
   path=item.get('path');before=old['builds'][build][field][key].get('path')
   if path:assert resolve(path)==(R/'234'/before).resolve();protected.append(build+':'+field+':'+key)
 assert len(c['hair'])==8
 for style in c['hair']:
  assert set(cat['fits'][build+'-'+style])=={'cap','beanie','bucket','cowboy','headband','ears','pashmina'}
assert 'gems' not in cat['details'];assert len(cat['colors']['frames'])==4
def walk(obj):
 if isinstance(obj,dict):
  for v in obj.values():walk(v)
 elif isinstance(obj,list):
  for v in obj:walk(v)
 elif isinstance(obj,str) and obj.endswith('.glb'):assert resolve(obj).is_file(),obj
walk(cat)
for path in (D/'components').glob('*.glb'):
 raw=path.read_bytes();n=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+n]);assert len(raw)==struct.unpack_from('<I',raw,8)[0];assert not any('draco' in k.lower() or 'meshopt' in k.lower() or 'quantization' in k.lower() for k in d.get('extensionsUsed',[]))
 tris=sum(d['accessors'][p['indices']]['count']//3 for m in d.get('meshes',[]) for p in m['primitives'] if p.get('mode',4)==4 and 'indices' in p);materials=d.get('materials',[])
 for material in materials:
  sheen=material.get('extensions',{}).get('KHR_materials_sheen')
  if sheen and material.get('name','').startswith('Headwear /') and any(s in material['name'].lower() for s in ['pashmina','bandana']):assert max(sheen.get('sheenColorFactor',[0,0,0]))<=.12001,'Unscaled cloth sheen: '+path.name
 if path.name.endswith('lenses.glb'):
  for m in materials:assert not m.get('extensions',{}).get('KHR_materials_transmission',{}).get('transmissionFactor',0);assert m['alphaMode']=='BLEND'
 dimensions=[]
 for im in d.get('images',[]):
  if 'bufferView' in im:
   bv=d['bufferViews'][im['bufferView']];start=28+n+bv.get('byteOffset',0)
   with Image.open(io.BytesIO(raw[start:start+bv['byteLength']])) as png:dimensions.append(dict(name=im.get('name',''),dimensions=list(png.size)))
 stats[path.name]=dict(bytes=len(raw),sha256=sha(path),triangles=tris,materials=len(materials),textures=len(d.get('images',[])),texture_dimensions=dimensions,extensions=d.get('extensionsUsed',[]))
proof=json.loads((P/'fit-proof235.json').read_text());assert len(proof)==128;assert all(x['protected_exact'] and x['reopened'] for x in proof)
angles=['front','threequarter','profile','rightprofile','rear','top','underside']
for case in proof:
 for angle in angles:
  path=P/'review2'/f"{case['build']}-{case['hair']}--{case['hat']}-{angle}.png"
  assert path.is_file(),path
  with Image.open(path) as im:
   assert im.size==(192,192),path
   assert len(im.convert('RGB').getcolors(192*192) or [])>100,'Empty/occluded reference: '+str(path)
report=dict(revision=235,protected=protected,fit_combinations=112,uncovered_looks=16,export_review_angles=['front','threequarter','profile','rightprofile','rear','top','underside'],sprout_attachments=len(cat['sprouts']),ordinary_uncompressed_glb=True,clear_lenses='BLEND opacity; transmission0, IOR1, single facing pane; no refraction/face blur',native_phone_qualified=False,stats=stats)
(P/'technical235.json').write_text(json.dumps(report,indent=2)+'\n')
for build,c in cat['builds'].items():
 for style in c['hair']:
  sheet=Image.new('RGB',(768,1728),'white');draw=ImageDraw.Draw(sheet)
  for i,hat in enumerate(['none','cap','beanie','bucket','cowboy','headband','ears','pashmina']):
   for j,angle in enumerate(['front','profile','rear','top']):
    f=P/'review2'/f'{build}-{style}--{hat}-{angle}.png';assert f.is_file();sheet.paste(Image.open(f).convert('RGB'),(j*192,i*216+24));draw.text((j*192+3,i*216+5),hat+' '+angle,fill='black')
  sheet.save(P/'review2'/f'{build}-{style}-sheet.jpg',quality=90)
print('AUDIT235',len(stats),'components;128 looks,7 angles; protected assets exact')
