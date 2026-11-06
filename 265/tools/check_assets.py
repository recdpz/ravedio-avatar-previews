from pathlib import Path
import runpy,json,numpy as np
from PIL import Image,ImageDraw
r=Path('E:/Ravedio-Avatar/floating138/mobile-preview/265');ns=runpy.run_path(str(r/'tools/build_spheres.py'));decode=ns['decode'];arr=ns['arr'];checks=[]
for build in ('Feminine','Masculine'):
 g,b=decode(r.parent/'264/assets'/f'{build}-optimized264.glb');h,c=decode(r/'assets'/f'{build}-sphere265.glb');assert g['nodes']==h['nodes'] and g['materials']==h['materials'];changed=set(next(x for x in ns['reports'] if x['build']==build)['changed'])
 for n in g['nodes']:
  if 'mesh' not in n:continue
  for p,q in zip(g['meshes'][n['mesh']]['primitives'],h['meshes'][n['mesh']]['primitives']):
   assert p==q
   for k,i in p['attributes'].items():
    a=arr(g,b,i);d=arr(h,c,i);assert np.isfinite(d).all()
    if n['name'] not in changed or k not in ('POSITION','NORMAL'):assert np.array_equal(a,d),(n['name'],k)
    if k=='NORMAL':assert np.max(abs(np.linalg.norm(d,axis=1)-1))<.002
   assert np.array_equal(arr(g,b,p['indices']),arr(h,c,p['indices']))
 checks.append({'build':build,'unchanged_body_clothing_materials_nodes_other_attributes_indices':True,'normals_unit_finite':True})
 for preset in ('full','bare','face'):
  sheet=Image.new('RGB',(384*4,410*4),(22,25,33));draw=ImageDraw.Draw(sheet)
  for i,angle in enumerate(('front','threequarter','profile','rightprofile','rearquarter','rear','top','underside')):
   for j,version in enumerate(('source','optimized')):
    x=(i%2*2+j)*384;y=i//2*410;sheet.paste(Image.open(r/'verification'/f'{build}-{preset}-{angle}-{version}.png').convert('RGB'),(x,y+26));draw.text((x+8,y+6),f'{angle} - '+('oval' if j==0 else 'sphere'),fill='white')
  sheet.save(r/'verification'/f'{build}-{preset}-contact.jpg',quality=90)
(r/'verification/invariants.json').write_text(json.dumps(checks,indent=2),encoding='utf8');print('INVARIANTS_COMPLETE',checks)
