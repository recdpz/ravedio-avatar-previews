import sys,json,shutil
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue251')
import verify251 as v
from common251 import *
from fits251 import normalise
s,_=v.assemble('Masculine','afro','beanie');cloth=[o for o in s.objects if o.type=='MESH' and o.get('component159')=='headgear'];limit=max((o.matrix_world@v.co).z for o in cloth for v in o.data.vertices)-.014;n=0
for o in [o for o in s.objects if o.type=='MESH' and o.get('component159')=='hair']:
 inv=o.matrix_world.inverted()
 for vert in o.data.vertices:
  p=o.matrix_world@vert.co
  if p.z>limit:p.z=limit;vert.co=inv@p;n+=1
 normalise(o)
u.bake(s);path=P/'components/Masculine-afro-beanie251-hair.glb';ex.export(s,path,'hair');shutil.copy2(path,D/'components'/path.name);close251(s,'Masculine-afro-beanie-pole-final251',['front','profile','rear','top'],'review2',384);q=json.loads((P/'proof251.json').read_text());q.pop('Masculine-afro-beanie-default-default',None);(P/'proof251.json').write_text(json.dumps(q,indent=2));print('CROWN_POLE_SEATED',n,limit,flush=True)
