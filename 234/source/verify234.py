import bpy,sys,json,struct
from pathlib import Path
from mathutils.kdtree import KDTree
P=Path(__file__).parent;sys.path.insert(0,str(P.parent/'refinement224'));import utils224 as u
records=json.loads((P/'output/lashes234.json').read_text(encoding='utf8'));assert len(records)==6;result={}
def points(s):return [o.matrix_world@v.co for o in s.objects if o.type=='MESH' and o.get('component159')=='eyelashes' for v in o.data.vertices]
def error(a,b):
 tree=KDTree(len(b))
 for i,p in enumerate(b):tree.insert(p,i)
 tree.balance();return max(tree.find(p)[2] for p in a)
for key,item in records.items():
 bpy.ops.wm.open_mainfile(filepath=item['source']);s=bpy.context.scene;before=points(s);protected={k:v for k,v in u.object_geometry(s).items() if s.objects[k].get('component159')!='eyelashes'}
 for o in list(s.objects):
  if o.get('component159')=='eyelashes':u.delete(o)
 old=set(s.objects);bpy.ops.import_scene.gltf(filepath=item['glb'])
 for o in s.objects:
  if o not in old and o.type=='MESH':o['component159']='eyelashes'
 after=points(s);delta=max(error(before,after),error(after,before));assert delta<2e-5
 assert protected=={k:v for k,v in u.object_geometry(s).items() if s.objects[k].get('component159')!='eyelashes'}
 raw=Path(item['glb']).read_bytes();n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n]);assert all(m.get('alphaMode','OPAQUE')=='OPAQUE' for m in doc['materials'])
 result[key]={'max_bidirectional_world_error':delta,'bytes':len(raw),'triangles':sum(doc['accessors'][p['indices']]['count']//3 for m in doc['meshes'] for p in m['primitives']),'materials':len(doc['materials']),'source_sha256':u.sha(Path(item['source'])),'glb_sha256':u.sha(Path(item['glb'])),'protected_neighbors_exact':True,'compression':False}
u.dump(P/'output/export-proof234.json',result);print('Verified all six lash components and protected eye/head geometry')
