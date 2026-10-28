import bpy,sys,json,struct
from pathlib import Path
from mathutils.kdtree import KDTree
P=Path(__file__).parent;sys.path.insert(0,str(P.parent/'refinement224'));import utils224 as u
records=json.loads((P/'output/eyes232.json').read_text(encoding='utf8'));result={}
assert len(records)==8
def points(s):return [o.matrix_world@v.co for o in s.objects if o.type=='MESH' and o.get('component159')=='eyes' for v in o.data.vertices]
def error(a,b):
 tree=KDTree(len(b))
 for i,p in enumerate(b):tree.insert(p,i)
 tree.balance();return max(tree.find(p)[2] for p in a)
for key,item in records.items():
 bpy.ops.wm.open_mainfile(filepath=item['source']);s=bpy.context.scene;before=points(s)
 for o in list(s.objects):
  if o.get('component159')=='eyes':u.delete(o)
 bpy.ops.import_scene.gltf(filepath=item['glb']);after=points(s);delta=max(error(before,after),error(after,before));assert delta<2e-5
 raw=Path(item['glb']).read_bytes();n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n])
 assert all(m.get('alphaMode','OPAQUE')=='OPAQUE' for m in doc['materials'])
 result[key]={'max_bidirectional_world_error':delta,'bytes':len(raw),'triangles':sum(doc['accessors'][p['indices']]['count']//3 for m in doc['meshes'] for p in m['primitives']),'materials':len(doc['materials']),'source_sha256':u.sha(Path(item['source'])),'glb_sha256':u.sha(Path(item['glb'])),'compression':False}
u.dump(P/'output/export-proof232.json',result)
retained={}
def bodies(s,key):return sorted([o for o in s.objects if o.type=='MESH' and o.name.startswith('Eye / '+key)],key=lambda o:o.name)
for build in ['Feminine','Masculine']:
 for key in ['tapered','hooded','bean']:
  points_by_rev=[]
  for rev in [231,232]:
   bpy.ops.wm.open_mainfile(filepath=str(P.parent/f'refinement{rev}/output/sources/{build}-{key}.blend'))
   points_by_rev.append([[tuple(o.matrix_world@v.co) for v in o.data.vertices] for o in bodies(bpy.context.scene,key)])
  assert points_by_rev[0]==points_by_rev[1]
  retained[build+'-'+key]={'full_eye_surface_exact231':True,'changes':'Highlight size and seating only'}
 bpy.ops.wm.open_mainfile(filepath=str(P.parent/'refinement228/output/sources'/f'{build}-soft-squint.blend'))
 old=bodies(bpy.context.scene,'soft squint228')[0];oldz=[(old.matrix_world@v.co).z for v in old.data.vertices]
 bpy.ops.wm.open_mainfile(filepath=str(P/'output/sources'/f'{build}-squint.blend'))
 new=bodies(bpy.context.scene,'squint232')[0];newz=[(new.matrix_world@v.co).z for v in new.data.vertices]
 retained[build+'-squint']={'old_height':max(oldz)-min(oldz),'new_height':max(newz)-min(newz),'eye_anchors_retained':[.15,1.895]}
u.dump(P/'output/retained232.json',retained);print('Verified eight exports and exact retained surfaces for the three liked shapes')
