"""Preserve intact visible hair; settle the hood around a broad hair support."""
import sys
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue249')
from common249 import *
import bmesh
from mathutils import Matrix,kdtree

def normalise(ob):
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()

def gather(s,style,build):
 """Move only the existing gathered pieces, without rebuilding their texture."""
 changed=[]
 if build!='Feminine':return changed
 if style=='ponytail':
  obs=[o for o in s.objects if o.type=='MESH' and ('rounded tail220' in o.name or 'tie220' in o.name)]
  assert len(obs)==6,[o.name for o in obs]
  tie=next(o for o in obs if 'tie220' in o.name);anchor=sum((tie.matrix_world@v.co for v in tie.data.vertices),Vector())/len(tie.data.vertices)
  target=Vector((-.10,.345,1.60));skin=tree([head_object(s)]);hit=skin.ray_cast(Vector((target.x,2,target.z)),Vector((0,-1,0)),4)[0]
  assert hit is not None;target.y=hit.y+.016;rot=Matrix.Rotation(-.50,3,'X')
  # Re-route the original pulled-back scalp to the lower tie. Its visible
  # forehead boundary, mesh, vertex colors and material remain intact.
  cap=next(o for o in s.objects if o.type=='MESH' and 'swept roots220' in o.name);world=[cap.matrix_world@v.co for v in cap.data.vertices];inv=cap.matrix_world.inverted();root_changes=0
  for index,p in enumerate(world):
   # GLB vertex order is not the old authoring grid. Extend the existing
   # lower rear surface geometrically, preserving the crown and face.
   weight=smooth((p.y-.10)/.18)*smooth((2.05-p.z)/.30)*(1-.65*smooth((abs(p.x)-.16)/.25))
   if weight<=1e-8:continue
   oldhit=skin.ray_cast(Vector((p.x,2,p.z)),Vector((0,-1,0)),4)[0]
   if oldhit is None:continue
   q=p.copy();q.z-=.30*weight;q.x=q.x*(1-.12*weight)+target.x*.12*weight
   hit=skin.ray_cast(Vector((q.x,2,q.z)),Vector((0,-1,0)),4)[0]
   if hit is None:continue
   q.y=hit.y+max(.004,min(.028,p.y-oldhit.y))
   cap.data.vertices[index].co=inv@q;root_changes+=1
  for index,p in enumerate(world):
   if p.y<=.10 or p.z>=2.05:assert (cap.matrix_world@cap.data.vertices[index].co-p).length<1e-7
  normalise(cap);changed.append(cap.name+':low gather roots '+str(root_changes))
  for ob in obs:
   inv=ob.matrix_world.inverted()
   for v in ob.data.vertices:v.co=inv@(target+rot@(ob.matrix_world@v.co-anchor))
   changed.append(ob.name)
 elif style=='space-buns':
  for ob in [o for o in s.objects if o.type=='MESH' and o.get('component159')=='hair']:
   bm=bmesh.new();bm.from_mesh(ob.data);bm.verts.ensure_lookup_table();seen=set();inv=ob.matrix_world.inverted()
   for start in bm.verts:
    if start.index in seen:continue
    pending=[start];island=[];seen.add(start.index)
    while pending:
     v=pending.pop();island.append(v)
     for edge in v.link_edges:
      q=edge.other_vert(v)
      if q.index not in seen:seen.add(q.index);pending.append(q)
    center=sum((ob.matrix_world@v.co for v in island),Vector())/len(island)
    if center.z>2.20 and abs(center.x)>.20:
     side=1 if center.x>0 else -1;origin=Vector((side*.35,.13,2.30));target=Vector((side*.28,.32,1.98));rot=Matrix.Rotation(-.62,3,'X')
     for v in island:v.co=inv@(target+rot@(ob.matrix_world@v.co-origin))
     changed.append(ob.name+':bun island '+str(start.index))
   bm.to_mesh(ob.data);bm.free()
 return changed

def broad_support(s,cache_path=None):
 arrays=[]
 for ob in s.objects:
  if ob.type!='MESH' or not (ob.get('component159')=='hair' or ob==head_object(s)):continue
  # Eight millimetre bins remove strand relief from the support envelope.
  ps=np.array([tuple(ob.matrix_world@v.co) for v in ob.data.vertices],dtype='f');ps=ps[ps[:,2]>=1.34]
  if ob.get('component159')=='hair':
   # Face-framing lengths hang in front of the hood opening. Including
   # them in the covered bulk would pull the lower corners into wings.
   ps=ps[~((ps[:,2]<1.95)&(ps[:,1]<-.12))]
  if len(ps):arrays.append(ps)
 ps=np.concatenate(arrays);_,ids=np.unique(np.round(ps/.008).astype('i'),axis=0,return_index=True);ps=ps[ids]
 bm=bmesh.new()
 for p in ps:bm.verts.new(p)
 bmesh.ops.convex_hull(bm,input=list(bm.verts),use_existing_faces=False);bm.verts.ensure_lookup_table();bm.verts.index_update()
 verts=[v.co.copy() for v in bm.verts];faces=[[v.index for v in f.verts] for f in bm.faces]
 if cache_path:
  triangles=[(f[0],f[j],f[j+1]) for f in faces for j in range(1,len(f)-1)]
  np.savez_compressed(cache_path,positions=np.array([tuple(p) for p in verts],dtype='f'),triangles=np.array(triangles,dtype='i'),count=len(ps))
 tr=BVHTree.FromPolygons(verts,faces);bm.free()
 return tr,len(ps)

def move_cloth(s,delta,old):
 ob=next(o for o in s.objects if 'joined hood wrap and ends239' in o.name);n=len(ob.data.vertices)//2
 inv=ob.matrix_world.inverted().to_3x3()
 for i,d in delta.items():
  for j in [i,i+n]:ob.data.vertices[j].co+=inv@d
 normalise(ob)
 for i in range(n):
  if i not in delta:assert (ob.matrix_world@ob.data.vertices[i].co-old[i]).length<1e-7
 bm=bmesh.new();bm.from_mesh(ob.data);assert all(len(e.link_faces)==2 for e in bm.edges);bm.free()
 kd=kdtree.KDTree(n)
 for i,p in enumerate(old[:n]):kd.insert(p,i)
 kd.balance();hems=0
 for seam in s.objects:
  if seam==ob or seam.type!='MESH' or seam.get('component159')!='headgear':continue
  inv=seam.matrix_world.inverted().to_3x3()
  for v in seam.data.vertices:
   p=seam.matrix_world@v.co
   if p.z<1.40:continue
   nearest=kd.find_n(p,4)
   if nearest[0][2]>.020:continue
   weights=[1/max(.0001,x[2])**2 for x in nearest];den=sum(weights)
   d=sum((delta.get(x[1],Vector())*w for x,w in zip(nearest,weights)),Vector())/den
   v.co+=inv@d
  hems+=1
 return hems

def fit_cloth(s,field_key=None,support_override=None):
 ob=next(o for o in s.objects if 'joined hood wrap and ends239' in o.name);n=len(ob.data.vertices)//2
 old=[ob.matrix_world@v.co for v in ob.data.vertices];uv={}
 for f in ob.data.polygons:
  if max(f.vertices)>=n:continue
  for li,i in zip(f.loop_indices,f.vertices):uv[i]=ob.data.uv_layers.active.data[li].uv.copy()
 if support_override:support,count=support_override
 else:
  cache_path=None
  if field_key:(P/'support').mkdir(exist_ok=True);cache_path=P/'support'/f'{field_key}.npz'
  support,count=broad_support(s,cache_path)
 field=np.zeros(n,dtype='f');hood=np.zeros(n,dtype=bool);directions={}
 for i,q in uv.items():
  p=old[i]
  if not (0<=q.x<=1.00001 and 0<=q.y<=1.00001 and p.z>1.40):continue
  weight=smooth(min(q.x,1-q.x)/.040)
  if weight<=1e-6:continue
  # Lower cloth opens laterally at its existing height. A spherical ray
  # would drag the lower edge down a long hairstyle and create a scallop.
  vertical=smooth((p.z-1.92)/.23);origin=Vector((a.C.x,a.C.y,p.z+(a.C.z-p.z)*vertical))
  dv=p-origin;direction=dv.normalized();hit,_,_,dist=support.ray_cast(origin,direction,2)
  if hit is None:continue
  hood[i]=True;directions[i]=direction
  field[i]=max(0,dist+.024-dv.length)*weight
 edges=np.array([(e.vertices[0],e.vertices[1]) for e in ob.data.edges if max(e.vertices)<n]);degree=np.bincount(edges.ravel(),minlength=n)
 for _ in range(240):
  total=np.zeros(n);np.add.at(total,edges[:,0],field[edges[:,1]]);np.add.at(total,edges[:,1],field[edges[:,0]])
  average=total/np.maximum(1,degree);field[hood]=np.maximum(field[hood],.45*field[hood]+.55*average[hood])
 # The old nape narrows almost to the neck. Long hair needs a substantially
 # wider lower edge; judge that new reserve in the actual joint views.
 assert float(field.max())<.40,float(field.max())
 delta={}
 for i in np.flatnonzero(field>1e-8):
  d=directions[i]*float(field[i]);delta[int(i)]=d
 if field_key:
  (P/'fields').mkdir(exist_ok=True);ids=sorted(delta)
  np.savez_compressed(P/'fields'/f'{field_key}.npz',positions=np.array([tuple(p) for p in old[:n]],dtype='f'),ids=np.array(ids,dtype='i'),delta=np.array([tuple(delta[i]) for i in ids],dtype='f'))
 hems=move_cloth(s,delta,old)
 return dict(modified_outer_vertices=len(delta),max_hood_displacement=float(field.max()),support_points=count,paired_thickness=True,closed_surface=True,unchanged_crossing_roots=True,seam_objects=hems)

def build(style,top='open',build='Feminine',export=False):
 s,paths=source(style,top,build,native_cloth=True)
 frozen={k:v for k,v in u.object_geometry(s).items() if s.objects[k].get('component159') not in ['hair','headgear']}
 changed=gather(s,style,build);hair_hash=u.object_geometry(s);result=fit_cloth(s,build+'-'+style if top==('open' if build=='Feminine' else 'tank') else None)
 now=u.object_geometry(s);assert all(now.get(k)==v for k,v in frozen.items())
 assert all(now.get(k)==v for k,v in hair_hash.items() if s.objects[k].get('component159')=='hair')
 result.update(build=build,style=style,top=top,source_hair=str((OLD/paths['hair']).resolve()),localized_gathers=changed,visible_strands_original=True,other_components_exact=True)
 if export:
  u.bake(s);bpy.ops.file.pack_all();src=P/'sources'/f'{build}-{style}-{top}-pashmina249.blend';bpy.ops.wm.save_as_mainfile(filepath=str(src),compress=True);bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;result['source']=str(src)
  path=P/'components'/f'{build}-{style}-{top}-pashmina249-headgear.glb';ex.export(s,path,'headgear');result['headgear']='components/'+path.name
  if changed:
   path=P/'components'/f'{build}-{style}-gather249-hair.glb'
   ex.export(s,path,'hair')
   result['hair']='components/'+path.name
  else:result['hair']=paths['hair'] if paths['hair'].startswith('../') else '../248/'+paths['hair']
  import accessories235
  anchor=accessories235.sprout();path=P/'components'/f'{build}-{style}-pashmina249-sprout.glb';u.bake(s);ex.export(s,path,'extra');result['sprout']={'path':'components/'+path.name,**anchor}
 return s,result

def export_top(style,top,build,reference):
 family=CAT249['pashminaHairFamilies'][build][style];src=FITS248[build+'-'+top+'-'+family]['source']
 bpy.ops.wm.open_mainfile(filepath=src);s=bpy.context.scene
 ob=next(o for o in s.objects if 'joined hood wrap and ends239' in o.name);n=len(ob.data.vertices)//2;old=[ob.matrix_world@v.co for v in ob.data.vertices]
 f=P/'fields'/f'{build}-{style}.npz';field=np.load(f);ids=field['ids'];positions=np.array([tuple(p) for p in old[:n]],dtype='f')
 if len(positions)!=len(field['positions']) or np.max(np.abs(positions[ids]-field['positions'][ids]))>1e-6:
  # Re-solve against the frozen broad support for this hairstyle. There is
  # no need to duplicate a full avatar scene for another garment variant.
  sf=P/'support'/f'{build}-{style}.npz';saved=np.load(sf)
  support=BVHTree.FromPolygons([Vector(p) for p in saved['positions']],saved['triangles'].tolist(),all_triangles=True)
  frozen={k:v for k,v in u.object_geometry(s).items() if s.objects[k].get('component159')!='headgear'}
  solved=fit_cloth(s,build+'-'+style+'-'+top,(support,int(saved['count'])))
  verified=u.object_geometry(s);assert all(verified.get(k)==v for k,v in frozen.items())
  path=P/'components'/f'{build}-{style}-{top}-pashmina249-headgear.glb';ex.export(s,path,'headgear')
  return {**reference,**solved,'top':top,'headgear':'components/'+path.name,'source':src,'field_reuse':False,'support_sha256':hashlib.sha256(sf.read_bytes()).hexdigest(),'source_is_frozen248_with_field':True}
 frozen={k:v for k,v in u.object_geometry(s).items() if s.objects[k].get('component159')!='headgear'}
 delta={int(i):Vector(d) for i,d in zip(ids,field['delta'])};move_cloth(s,delta,old)
 verified=u.object_geometry(s);assert all(verified.get(k)==v for k,v in frozen.items())
 path=P/'components'/f'{build}-{style}-{top}-pashmina249-headgear.glb';ex.export(s,path,'headgear')
 return {**reference,'top':top,'headgear':'components/'+path.name,'source':src,'field_reuse':True,'field_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'source_is_frozen248_with_field':True}

if __name__=='__main__':
 styles=next((x.split('=',1)[1].split(',') for x in sys.argv if x.startswith('--styles=')),None)
 builds=next((x.split('=',1)[1].split(',') for x in sys.argv if x.startswith('--builds=')),['Feminine'])
 records=json.loads((P/'fits249.json').read_text()) if (P/'fits249.json').exists() else {}
 for b in builds:
  for style in (styles or CAT249['builds'][b]['hair']):
   if style not in CAT249['builds'][b]['hair']:continue
   if '--tops-only' in sys.argv:continue
   top='open' if b=='Feminine' else 'tank';s,item=build(style,top,b,'--export' in sys.argv);key=b+'-'+style+'-'+top
   records[key]=item;(P/'fits249.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf8')
   detail(s,key,['front','profile','rear']);print('FIT249',key,item['max_hood_displacement'],flush=True)
 if '--all-tops' in sys.argv:
  for b in builds:
   for style in (styles or CAT249['builds'][b]['hair']):
    if style not in CAT249['builds'][b]['hair']:continue
    default='open' if b=='Feminine' else 'tank';reference=records[b+'-'+style+'-'+default]
    for top in CAT249['builds'][b]['tops']:
     if top==default:continue
     key=b+'-'+style+'-'+top
     if '--resume' in sys.argv and key in records and records[key].get('headgear') and (P/records[key]['headgear']).exists():continue
     records[key]=export_top(style,top,b,reference)
     (P/'fits249.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf8');print('TOP249',key,flush=True)
 print('FIT249_COMPLETE',len(records))
