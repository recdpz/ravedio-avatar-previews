import sys,json,math,hashlib
from pathlib import Path
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue262');from common262 import *
from mathutils.bvhtree import BVHTree
P=Path('E:/Ravedio-Avatar/catalogue262');W=P/'pass2';(W/'sources').mkdir(parents=True,exist_ok=True);(W/'components').mkdir(exist_ok=True);out={}
import shutil
for f in (P/'pass1/components').glob('*-base.glb'):shutil.copy2(f,W/'components'/f.name)
def freeze(s):return {k:v for k,v in u.object_geometry(s).items() if s.objects[k].get('component159')!='top'}
def check262(s,before):
 after=u.object_geometry(s);assert all(after.get(k)==v for k,v in before.items())

def separate_sleeve_trim(s):
 report=[]
 for ob in list(s.objects):
  if ob.type!='MESH' or ob.get('component159')!='top' or ob.name.startswith('Sleeve'):continue
  me=ob.data;n=len(me.vertices);parent=list(range(n));same={}
  def root(i):
   while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
   return i
  for v in me.vertices:
   key=tuple(round(x,7) for x in v.co)
   if key in same:parent[root(v.index)]=root(same[key])
   else:same[key]=v.index
  for face in me.polygons:
   first=root(face.vertices[0])
   for vi in face.vertices[1:]:parent[root(vi)]=first
  groups={}
  for face in me.polygons:groups.setdefault(root(face.vertices[0]),[]).append(face.index)
  sleeves=[];core=[]
  for ids in groups.values():
   vis=sorted(set(i for fi in ids for i in me.polygons[fi].vertices));pts=[ob.matrix_world@me.vertices[i].co for i in vis];center=sum(pts,Vector())/len(pts)
   if abs(center.x)>.31 and center.z<1.35 and min(p.z for p in pts)<1.23:sleeves.append(ids)
   else:core.extend(ids)
  if not sleeves:continue
  original_normals=[x.vector.copy() for x in me.corner_normals]
  for group_index,ids in enumerate(([core] if core else [])+sleeves):
   is_sleeve=not(core and group_index==0);used=sorted(set(i for fi in ids for i in me.polygons[fi].vertices));remap={vi:i for i,vi in enumerate(used)};new=bpy.data.meshes.new(ob.name+' role262');new.from_pydata([me.vertices[i].co[:] for i in used],[],[[remap[i] for i in me.polygons[fi].vertices] for fi in ids]);new.update()
   for m in me.materials:new.materials.append(m)
   norm=[]
   for f2,fi in zip(new.polygons,ids):
    old=me.polygons[fi];f2.material_index=old.material_index;f2.use_smooth=old.use_smooth;norm.extend(original_normals[li] for li in old.loop_indices)
   for layer in me.uv_layers:
    uv=new.uv_layers.new(name=layer.name);data=[layer.data[li].uv.copy() for fi in ids for li in me.polygons[fi].loop_indices]
    for dest,val in zip(uv.data,data):dest.uv=val
   for layer in me.color_attributes:
    attr=new.color_attributes.new(name=layer.name,type=layer.data_type,domain=layer.domain);indices=used if layer.domain=='POINT' else [li for fi in ids for li in me.polygons[fi].loop_indices]
    for dest,oldid in zip(attr.data,indices):dest.color=layer.data[oldid].color
   new.normals_split_custom_set(norm);part=ob.copy();part.data=new;part.name=('Sleeve / separated trim262 '+str(group_index)) if is_sleeve else ob.name+' / core262';part['partRole262']='sleeve' if is_sleeve else 'garment';s.collection.objects.link(part)
  report.append({'mesh':ob.name,'separated_sleeve_islands':len(sleeves),'positions_normals_uv_materials_preserved':True});u.delete(ob)
 return report
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
    q=p+Vector((0,newh.y-h.y,dz));maximum=max(maximum,(q-p).length);v.co=inv@q;count+=1
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
 roles=separate_sleeve_trim(s);rows.append({'semantic_parts':roles});check262(s,frozen);u.bake(s);bpy.ops.outliner.orphans_purge(do_recursive=True);bpy.ops.file.pack_all();key=b+'-'+top;src=W/'sources'/f'{key}-top262.blend';target=W/'components'/f'fix262-{key}-top.glb';bpy.ops.wm.save_as_mainfile(filepath=str(src),compress=True);ex.export(s,target,'top');out[key]={'source':str(src),'path':target.name,'changes':rows,'protected_non_top_geometry_exact':True};print('GARMENT_REPAIR262',key,rows,flush=True)
(W/'garments262.json').write_text(json.dumps(out,indent=2));c=json.loads((P/'pass1/catalogue261.json').read_text())
for key,row in out.items():b,top=key.split('-',1);c['builds'][b]['tops'][top]['path']=row['path']
(W/'catalogue261.json').write_text(json.dumps(c,indent=2));print('GARMENT_REPAIR262_COMPLETE')
