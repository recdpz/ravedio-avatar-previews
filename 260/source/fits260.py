import sys
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue260')
from common260 import *
from fits251 import fit_roots
import accessories235
rows=json.loads((P/'selected260.json').read_text());out={};sprouts={};W=P/'fits';(W/'components').mkdir(parents=True,exist_ok=True)
for key,row in rows.items():
 build,style=key.split('-',1)
 for hat in ['none','cap','beanie','bucket','cowboy','headband','ears','pashmina']:
  bpy.ops.wm.open_mainfile(filepath=row['source']);s=bpy.context.scene;frozen=protect(s);a.setup();c.reset_head(s)
  if hat!='none':
   path=CAT['fits'][key][hat]['headgear']
   if hat=='pashmina':path=CAT['pashminaVariants'][build][CAT['pashminaHairFamilies'][build][style]]['open' if build=='Feminine' else 'tank']
   imported((BASE/path).resolve(),'headgear')
  hbefore={k:v for k,v in u.object_geometry(s).items() if s.objects[k].get('component159')=='headgear'};count=fit_roots(s,hat) if hat!='none' else 0;check(s,frozen);now=u.object_geometry(s);assert all(now.get(k)==v for k,v in hbefore.items())
  if hat!='none':
   u.bake(s)
   for ob in s.objects:
    if ob.type=='MESH' and ob.get('component159')=='hair':clean_normals(ob)
   target=W/'components'/f'{key}-{hat}260-hair.glb';assert not target.exists();ex.export(s,target,'hair');prev258.patch258(target,s);out[key+'|'+hat]=dict(hair='components/'+target.name,changed_vertices=count,headgear_geometry_preserved=True,protected_geometry_preserved=True)
  r=accessories235.sprout();u.bake(s);target=W/'components'/f'{key}-{hat}260-sprout.glb';assert not target.exists();ex.export(s,target,'extra');r['path']='components/'+target.name;sprouts[key+'--'+hat]=r
  (W/'fits260.json').write_text(json.dumps(out,indent=2)+'\n');(W/'sprouts260.json').write_text(json.dumps(sprouts,indent=2)+'\n');print('FIT260',key,hat,count,flush=True)
print('FITS260_COMPLETE',len(out),len(sprouts),flush=True)
