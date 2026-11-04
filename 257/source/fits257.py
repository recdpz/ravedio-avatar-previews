import sys,json
from pathlib import Path
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue257')
from core257 import *
from fits251 import fit_roots
import accessories235
P=Path('E:/Ravedio-Avatar/catalogue257/pass3');D=P.parent.parent/'floating138/mobile-preview/257';OLD=D.parent/'256';CAT=json.loads((OLD/'catalogue256.json').read_text());out={};sprouts={}
for style in ['taper','curly-top']:
 for hat in ['none','cap','beanie','bucket','cowboy','headband','ears','pashmina']:
  bpy.ops.wm.open_mainfile(filepath=str(P/'sources'/f'Masculine-{style}-hair257.blend'));s=bpy.context.scene;frozen=protect(s);a.setup();c.reset_head(s)
  if hat!='none':
   path=CAT['fits']['Masculine-'+style][hat]['headgear']
   if hat=='pashmina':path=CAT['pashminaVariants']['Masculine'][CAT['pashminaHairFamilies']['Masculine'][style]]['tank']
   imported((OLD/path).resolve(),'headgear')
  hbefore={k:v for k,v in u.object_geometry(s).items() if s.objects[k].get('component159')=='headgear'};count=fit_roots(s,hat) if hat!='none' else 0;check(s,frozen);now=u.object_geometry(s);assert all(now.get(k)==v for k,v in hbefore.items())
  key=style+'|'+hat
  if hat!='none':
   u.bake(s);target=P/'components'/f'Masculine-{style}-{hat}257-hair.glb';assert not target.exists();ex.export(s,target,'hair');patch257(target,s);out[key]=dict(hair='components/'+target.name,changed_vertices=count,headgear_geometry_preserved=True,other_geometry_preserved=True)
  r=accessories235.sprout();u.bake(s);target=P/'components'/f'Masculine-{style}-{hat}257-sprout.glb';assert not target.exists();ex.export(s,target,'extra');r['path']='components/'+target.name;sprouts['Masculine-'+style+'--'+hat]=r
  (P/'fits257.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8');(P/'sprouts257.json').write_text(json.dumps(sprouts,indent=2)+'\n',encoding='utf8');print('FIT257',key,count,flush=True)
print('FIT257_COMPLETE',len(out),len(sprouts),flush=True)
