import sys,json,shutil
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue251')
import verify251 as v
from fits251 import normalise
from common251 import *
import accessories235
cat=json.loads((D/'catalogue251.json').read_text());fits=json.loads((P/'fits251.json').read_text())
for b,bc in cat['builds'].items():
 for style in bc['hair']:
  s,paths=v.assemble(b,style,'beanie');frozen={k:x for k,x in u.object_geometry(s).items() if s.objects[k].get('component159') not in ['headgear','extra']}
  remove(['headgear']);imported((OLD/CAT251['fits'][b+'-'+style]['beanie']['headgear']).resolve(),'headgear')
  for ob in [o for o in s.objects if o.type=='MESH' and o.get('component159')=='headgear']:
   inv=ob.matrix_world.inverted()
   for vert in ob.data.vertices:
    q=ob.matrix_world@vert.co;q.z+=.072*smooth((q.z-2.13)/.24);vert.co=inv@q
   normalise(ob)
  u.bake(s);key=b+'-'+style+'-beanie251';path=P/'components'/f'{key}-headgear.glb';ex.export(s,path,'headgear');hg='components/'+path.name;shutil.copy2(path,D/hg);remove(['extra']);sprout=accessories235.sprout();u.bake(s);sp=P/'components'/f'{key}-sprout.glb';ex.export(s,sp,'extra');sprout['path']='components/'+sp.name;shutil.copy2(sp,D/sprout['path']);remove(['extra']);now=u.object_geometry(s);assert all(now.get(k)==x for k,x in frozen.items());cat['fits'][b+'-'+style]['beanie']['headgear']=hg;cat['sprouts'][b+'-'+style+'--beanie']=sprout;rec=fits.get(b+'-'+style+'-beanie',dict(hair=paths['hair'],protected_exact=True));rec.update(headgear=hg,sprout=sprout,beanie_crown_clearance=.072,cuff_unchanged=True);fits[b+'-'+style+'-beanie']=rec;close251(s,key+'-clearance',['front','profile','rear'],'review2',384);print('BEANIE_CLEAR',b,style,flush=True)
(D/'catalogue251.json').write_text(json.dumps(cat,indent=2)+'\n');(P/'fits251.json').write_text(json.dumps(fits,indent=2)+'\n');proof=json.loads((P/'proof251.json').read_text());proof={k:x for k,x in proof.items() if '-beanie-' not in k};(P/'proof251.json').write_text(json.dumps(proof,indent=2));print('BEANIE_CLEAR_COMPLETE',len(fits),flush=True)
