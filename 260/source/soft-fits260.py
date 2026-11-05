import sys
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue260')
from common260 import *
from fits251 import fit_roots
import accessories235
rows=json.loads((P/'selected260.json').read_text());out={};sprouts={};W=P/'fits3';(W/'components').mkdir(parents=True,exist_ok=True)
for key,row in rows.items():
 build,style=key.split('-',1)
 for hat in ['cap','beanie','bucket','cowboy']:
  bpy.ops.wm.open_mainfile(filepath=row['source']);s=bpy.context.scene;frozen=protect(s);a.setup();c.reset_head(s);imported((BASE/CAT['fits'][key][hat]['headgear']).resolve(),'headgear');cloth={k:v for k,v in u.object_geometry(s).items() if s.objects[k].get('component159')=='headgear'};n=0
  # Continue the compression gradually below the hat's rim. Ray projection
  # alone ends at the cloth boundary and made a sudden horizontal step.
  for ob in [o for o in s.objects if o.type=='MESH' and o.get('component159')=='hair']:
   inv=ob.matrix_world.inverted()
   for v in ob.data.vertices:
    p=ob.matrix_world@v.co;d=p-a.C;N=d.normalized();hit,_,_,distance=c.HEAD.ray_cast(a.C,N,2)
    if hit is None:continue
    # Preserve the ordering, relief and thickness of overlapping locks. A hard
    # maximum collapses neighboring surfaces onto one radius and creates facets.
    lift=d.length-distance
    if lift>0:
     factor=.065+.935*smooth((2.15-p.z)/.35);target=hit+N*(.0015+lift*factor);v.co=inv@target;n+=1
  check(s,frozen);now=u.object_geometry(s);assert all(now.get(k)==v for k,v in cloth.items());u.bake(s)
  for ob in s.objects:
   if ob.type=='MESH' and ob.get('component159')=='hair':clean_normals(ob)
  target=W/'components'/f'{key}-{hat}260-hair.glb';assert not target.exists();ex.export(s,target,'hair');prev258.patch258(target,s);out[key+'|'+hat]=dict(hair='components/'+target.name,changed_vertices=n,smooth_rim_transition=True,headgear_geometry_preserved=True,protected_geometry_preserved=True)
  r=accessories235.sprout();u.bake(s);target=W/'components'/f'{key}-{hat}260-sprout.glb';assert not target.exists();ex.export(s,target,'extra');r['path']='components/'+target.name;sprouts[key+'--'+hat]=r;(W/'fits260.json').write_text(json.dumps(out,indent=2)+'\n');(W/'sprouts260.json').write_text(json.dumps(sprouts,indent=2)+'\n');print('SOFTFIT260',key,hat,flush=True)
print('SOFTFITS260_COMPLETE',len(out),flush=True)
