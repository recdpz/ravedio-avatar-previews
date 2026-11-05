import bpy,json,struct,numpy as np,sys,argparse
from pathlib import Path
P=Path(__file__).parent
sys.path.insert(0,str(P))
import parameters222 as parameters
def delete(ob):bpy.data.objects.remove(ob,do_unlink=True)
class b:
 @staticmethod
 def dump(path,value):path.write_text(json.dumps(value,indent=2),encoding='utf8')
def export(s,path,group):
 bpy.ops.object.select_all(action='DESELECT');temporary=[];hidden=[];deps=bpy.context.evaluated_depsgraph_get()
 try:
  for ob in list(s.objects):
   if group=='headgear' and ob.get('capDesign') and ob.hide_render:hidden.append(ob);ob.hide_render=False
   if ob.type not in ['MESH','CURVE'] or ob.hide_render or ob.get('component159')!=group:continue
   if ob.type=='CURVE' or (ob.modifiers and not ob.data.shape_keys):
    me=bpy.data.meshes.new_from_object(ob.evaluated_get(deps));copy=bpy.data.objects.new(ob.name,me);s.collection.objects.link(copy);copy.matrix_world=ob.matrix_world;copy.update_tag();temporary.append(copy);copy.select_set(True)
    for key in ob.keys():copy[key]=ob[key]
   else:ob.select_set(True)
  bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_apply=False,export_morph=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False)
  bake_shader_colors(s,path,group)
 finally:
  for ob in temporary:delete(ob)
  for ob in hidden:ob.hide_render=True

def bake_shader_colors(s,path,group):
 # Blender's exporter can emit opaque dummy colors for a secondary material
 # even when both shaders read the same explicit named color attribute.
 # Bake that authored field into standard COLOR_0 by exact exported position.
 expected={}
 for ob in s.objects:
  if ob.type!='MESH' or ob.get('component159')!=group or not ob.data.color_attributes:continue
  co=ob.data.color_attributes[0]
  if co.domain!='POINT':continue
  points=np.array([[v.co.x,v.co.z,-v.co.y] for v in ob.data.vertices],dtype='f')
  lookup={tuple(np.round(p,5)):list(c.color) for p,c in zip(points,co.data)}
  expected[ob.data.name]=lookup;expected[ob.name]=lookup
 if not expected:return
 data=path.read_bytes();n=struct.unpack_from('<I',data,12)[0];doc=json.loads(data[20:20+n]);binary=bytearray(data[28+n:]);records=[]
 for mm in doc['meshes']:
  lookup=expected.get(mm['name'])
  if lookup is None:continue
  for primitive in mm['primitives']:
   accessor=doc['accessors'][primitive['attributes']['POSITION']];view=doc['bufferViews'][accessor['bufferView']];points=np.frombuffer(binary,dtype='<f4',count=accessor['count']*3,offset=view.get('byteOffset',0)+accessor.get('byteOffset',0)).reshape(-1,3).copy()
   colors=[]
   for point in points:
    key=tuple(np.round(point,5));assert key in lookup,(mm['name'],point);colors.append(lookup[key])
   ar=np.asarray(colors,dtype='<f4');binary.extend(b'\0'*((-len(binary))%4));offset=len(binary);binary.extend(ar.tobytes());vi=len(doc['bufferViews']);doc['bufferViews'].append(dict(buffer=0,byteOffset=offset,byteLength=ar.nbytes,target=34962));ai=len(doc['accessors']);doc['accessors'].append(dict(bufferView=vi,componentType=5126,count=len(ar),type='VEC4'));primitive['attributes']['COLOR_0']=ai;primitive['attributes'].pop('COLOR_1',None)
   if ar[:,3].min()<.999:doc['materials'][primitive['material']]['alphaMode']='BLEND'
   records.append(dict(mesh=mm['name'],alpha_min=float(ar[:,3].min()),alpha_max=float(ar[:,3].max()),vertices=len(ar)))
 doc['buffers'][0]['byteLength']=len(binary);text=json.dumps(doc,separators=(',',':')).encode();text+=b' '*((-len(text))%4);binary+=b'\0'*((-len(binary))%4);path.write_bytes(struct.pack('<III',0x46546C67,2,28+len(text)+len(binary))+struct.pack('<II',len(text),0x4E4F534A)+text+struct.pack('<II',len(binary),0x004E4942)+binary)
 b.dump(P/(path.stem+'-vertex-colors.json'),records)
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--scene',required=True);parser.add_argument('--group',choices=['hair','top','bottom','headgear','base'],required=True);parser.add_argument('--output',required=True);parser.add_argument('--choices');args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);bpy.ops.wm.open_mainfile(filepath=str((P/args.scene).resolve()));s=bpy.context.scene;parameters.apply(s,json.loads(Path(args.choices).read_text(encoding='utf8')) if args.choices else {});export(s,Path(args.output),args.group)
