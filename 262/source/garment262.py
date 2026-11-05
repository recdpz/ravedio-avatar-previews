import sys,json,math,hashlib
from pathlib import Path
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue262');from common262 import *
from mathutils.bvhtree import BVHTree
P=Path('E:/Ravedio-Avatar/catalogue262');W=P/'pass1';(W/'sources').mkdir(exist_ok=True);(W/'components').mkdir(exist_ok=True);out={}
def freeze(s):return {k:v for k,v in u.object_geometry(s).items() if s.objects[k].get('component159')!='top'}
def check262(s,before):
 after=u.object_geometry(s);assert all(after.get(k)==v for k,v in before.items())
for b,top in [('Feminine','triangle'),('Feminine','sweatshirt'),('Masculine','sweatshirt')]:
 s=load262(b,top);frozen=freeze(s);rows=[]
 if top=='triangle':
  body=tree([next(o for o in s.objects if 'rounded torso' in o.name.lower())])
  for o in s.objects:
   if o.type!='MESH' or 'clean triangle214' not in o.name:continue
   inv=o.matrix_world.inverted();count=0;maximum=0
   for v in o.data.vertices:
    p=o.matrix_world@v.co;w=1-smooth((p.z-1.14)/.055);edge=min(1.2,abs(abs(p.x)-.139)/.12);dz=-.010*edge**2*w
    if abs(dz)<1e-7:continue
    h,n,_,_=body.ray_cast(Vector((p.x,-1,p.z)),Vector((0,1,0)),2);newh,newn,_,_=body.ray_cast(Vector((p.x,-1,p.z+dz)),Vector((0,1,0)),2)
    if h is None or newh is None:continue
    offset=max(.001,min(.009,(p-h).dot(n)));q=newh+newn*offset;maximum=max(maximum,(q-p).length);v.co=inv@q;count+=1
   clean_normals(o);rows.append({'name':o.name,'vertices':count,'max_shift':maximum})
 else:
  main=next(o for o in s.objects if o.type=='MESH' and 'Clothing / tailored203' in o.name);support=tree([main])
  for o in s.objects:
   if o.type!='MESH' or not any(t in o.name for t in ['rounded resting hood215','smooth back seam215']):continue
   inv=o.matrix_world.inverted();count=0;maximum=0
   for v in o.data.vertices:
    p=o.matrix_world@v.co;weight=smooth((p.y-.10)/.12)*smooth((1.47-p.z)/.17)
    if weight<=0:continue
    hit=support.ray_cast(Vector((p.x,1,p.z)),Vector((0,-1,0)),2)[0]
    if hit is None:continue
    excess=max(0,p.y-hit.y-.012);delta=min(.08,excess*.65)*weight;q=p.copy();q.y-=delta;q.z-=.004*smooth(delta/.06);v.co=inv@q;count+=int(delta>1e-7);maximum=max(maximum,delta)
   clean_normals(o);rows.append({'name':o.name,'vertices':count,'max_rear_seating':maximum})
 check262(s,frozen);u.bake(s);bpy.ops.outliner.orphans_purge(do_recursive=True);bpy.ops.file.pack_all();key=b+'-'+top;src=W/'sources'/f'{key}-top262.blend';target=W/'components'/f'fix262-{key}-top.glb';bpy.ops.wm.save_as_mainfile(filepath=str(src),compress=True);ex.export(s,target,'top');out[key]={'source':str(src),'path':target.name,'changes':rows,'protected_non_top_geometry_exact':True};print('GARMENT_REPAIR262',key,rows,flush=True)
(W/'garments262.json').write_text(json.dumps(out,indent=2));c=json.loads((W/'catalogue261.json').read_text())
for key,row in out.items():b,top=key.split('-',1);c['builds'][b]['tops'][top]['path']=row['path']
(W/'catalogue261.json').write_text(json.dumps(c,indent=2));print('GARMENT_REPAIR262_COMPLETE')
