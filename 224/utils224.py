"""224 shared-coordinate static export and original-studio reproduction helpers."""
import bpy,json,math,hashlib,struct,ast,numpy as np
from pathlib import Path
from mathutils import Vector
P=Path(__file__).parent
PALETTE=json.loads((P/'face-palette209.json').read_text())
def dump(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def tone(s,i):
 for ob in s.objects:
  if ob.type not in ['MESH','CURVE']:continue
  for mat in ob.data.materials:
   if not mat or not mat.use_nodes:continue
   bs=mat.node_tree.nodes.get('Principled BSDF')
   if not bs:continue
   key='skin' if mat.name.startswith('Skin') else 'stubble' if mat.name.startswith('Groom / stubble209') else 'ink' if mat.name.startswith('Face / ink209') else 'lip' if mat.name.startswith('Face / lip209') else None
   if key:bs.inputs['Base Color'].default_value=(*PALETTE[key][i],1)
def camera(s,angle='front',size=512,body=False):
 target=Vector((0,0,1.28 if body else 1.88));dirs={'front':(0,-8,0),'threequarter':(-4,-8,0),'profile':(-8,0,0),'rightprofile':(8,0,0),'rear':(0,8,0),'top':(0,-4,8),'underside':(0,-4,-8)};s.camera.location=target+Vector(dirs[angle]);s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=2.70 if body else 1.50;s.render.resolution_x=s.render.resolution_y=size;s.render.resolution_percentage=100;s.cycles.samples=64 if size>=512 else 40;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA'
def render(s,p,size=512,angle='front',body=False):
 camera(s,angle,size,body);s.render.filepath=str(p);hidden=[]
 try:
  if angle=='underside':
   for o in s.objects:
    if o.name=='Studio floor':hidden.append((o,o.visible_camera));o.visible_camera=False
  bpy.ops.render.render(scene=s.name,write_still=True)
 finally:
  for o,state in hidden:o.visible_camera=state

def delete(o):bpy.data.objects.remove(o,do_unlink=True)
def object_geometry(s,evaluated=False):
 out={};deps=bpy.context.evaluated_depsgraph_get()
 for o in s.objects:
  if o.type not in ['MESH','CURVE'] or o.get('component159')=='studio' or o.hide_render:continue
  if evaluated:
   me=bpy.data.meshes.new_from_object(o.evaluated_get(deps),preserve_all_data_layers=True,depsgraph=deps)
  else:me=o.data
  a=np.asarray([v.co[:] for v in me.vertices],dtype='f');out[o.name]=hashlib.sha256(a.tobytes()).hexdigest()
  if evaluated:bpy.data.meshes.remove(me)
 return out

def bake(s):
 before=object_geometry(s,True);deps=bpy.context.evaluated_depsgraph_get()
 for o in list(s.objects):
  if o.type not in ['MESH','CURVE'] or o.get('component159')=='studio' or o.hide_render:continue
  me=bpy.data.meshes.new_from_object(o.evaluated_get(deps),preserve_all_data_layers=True,depsgraph=deps);me.name=o.name+' / static224'
  if o.type=='MESH':o.data=me;o.modifiers.clear()
  else:
   old=o;name=old.name;matrix=old.matrix_world.copy();props={k:old[k] for k in old.keys()};visibility={k:getattr(old,k) for k in ['visible_camera','visible_diffuse','visible_glossy','visible_transmission','visible_volume_scatter','visible_shadow'] if hasattr(old,k)};delete(old);o=bpy.data.objects.new(name,me);s.collection.objects.link(o);o.matrix_world=matrix
   for k,v in props.items():o[k]=v
   for k,v in visibility.items():setattr(o,k,v)
  for key in list(o.keys()):
   if key.startswith('param') or key in ['capOriginal214']:del o[key]
  o['baked224']=True
 s.view_layers.update();after=object_geometry(s);assert before==after,[(k,before[k],after.get(k)) for k in before if before[k]!=after.get(k)]
 return {'evaluated_objects_exact':len(before),'no_live_shape_keys':all(not o.data.shape_keys for o in s.objects if o.type=='MESH' and not o.hide_render and o.get('component159')!='studio'),'geometry':after}

def colors(s,path,group=None):
 expected={}
 for o in s.objects:
  if o.type!='MESH' or (group and o.get('component159')!=group) or not o.data.color_attributes:continue
  co=o.data.color_attributes[0]
  if co.domain!='POINT':continue
  points=np.asarray([[v.co.x,v.co.z,-v.co.y] for v in o.data.vertices],dtype='f');lookup={tuple(np.round(p,5)):list(c.color) for p,c in zip(points,co.data)};expected[o.data.name]=lookup;expected[o.name]=lookup
 if not expected:return []
 data=path.read_bytes();n=struct.unpack_from('<I',data,12)[0];doc=json.loads(data[20:20+n]);binary=bytearray(data[28+n:]);records=[]
 for mesh in doc['meshes']:
  lookup=expected.get(mesh.get('name'))
  if lookup is None:continue
  for primitive in mesh['primitives']:
   ac=doc['accessors'][primitive['attributes']['POSITION']];bv=doc['bufferViews'][ac['bufferView']];points=np.frombuffer(binary,dtype='<f4',count=ac['count']*3,offset=bv.get('byteOffset',0)+ac.get('byteOffset',0)).copy().reshape(-1,3);ar=np.asarray([lookup[tuple(np.round(p,5))] for p in points],dtype='<f4');binary.extend(b'\0'*((-len(binary))%4));offset=len(binary);binary.extend(ar.tobytes());vi=len(doc['bufferViews']);doc['bufferViews'].append(dict(buffer=0,byteOffset=offset,byteLength=ar.nbytes,target=34962));ai=len(doc['accessors']);doc['accessors'].append(dict(bufferView=vi,componentType=5126,count=len(ar),type='VEC4'));primitive['attributes']['COLOR_0']=ai;primitive['attributes'].pop('COLOR_1',None)
   if ar[:,3].min()<.999:doc['materials'][primitive['material']]['alphaMode']='BLEND'
   records.append(dict(mesh=mesh['name'],alpha_min=float(ar[:,3].min()),alpha_max=float(ar[:,3].max())))
 doc['buffers'][0]['byteLength']=len(binary);text=json.dumps(doc,separators=(',',':')).encode();text+=b' '*((-len(text))%4);binary+=b'\0'*((-len(binary))%4);path.write_bytes(struct.pack('<III',0x46546C67,2,28+len(text)+len(binary))+struct.pack('<II',len(text),0x4E4F534A)+text+struct.pack('<II',len(binary),0x004E4942)+binary);return records

def export(s,path,group=None):
 bpy.ops.object.select_all(action='DESELECT')
 for o in s.objects:
  if o.type=='MESH' and not o.hide_render and o.get('component159')!='studio' and (not group or o.get('component159')==group):o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_apply=False,export_morph=False,export_yup=True,export_extras=True,export_cameras=False,export_lights=False);return colors(s,path,group)

def requirements(s):
 return {'scene':s.name,'settings':settings(s),'ray_visibility':{o.name:{k:getattr(o,k) for k in ['visible_camera','visible_diffuse','visible_glossy','visible_transmission','visible_volume_scatter','visible_shadow'] if hasattr(o,k)} for o in s.objects if o.type=='MESH' and o.get('component159')!='studio'},'images':[{'name':im.name,'dimensions':list(im.size),'packed':bool(im.packed_file),'source':im.source} for im in bpy.data.images if im.type=='IMAGE']}
# Exact original producer settings recorder, copied as a local portable function.

def settings(s):
 lights=[]
 for ob in s.objects:
  if ob.type=='LIGHT':lights.append(dict(name=ob.name,matrix_world=[list(row) for row in ob.matrix_world],type=ob.data.type,energy_W=ob.data.energy,color_linear=list(ob.data.color),shape=getattr(ob.data,'shape',None),size=getattr(ob.data,'size',None),size_y=getattr(ob.data,'size_y',None)))
 world=[]
 if s.world and s.world.use_nodes:
  for n in s.world.node_tree.nodes:
   world.append(dict(name=n.name,type=n.type,inputs={p.name:list(p.default_value) if hasattr(p.default_value,'__len__') else p.default_value for p in n.inputs if hasattr(p,'default_value') and (isinstance(p.default_value,(int,float)) or hasattr(p.default_value,'__len__'))}))
 return dict(blender=bpy.app.version_string,coordinates='Blender right-handed Z-up; front -Y. GLB right-handed Y-up; front +Z. Native glTF export conversion only; all components retain common world coordinates.',camera=dict(matrix_world=[list(r) for r in s.camera.matrix_world],type=s.camera.data.type,ortho_scale=s.camera.data.ortho_scale,clip_start=s.camera.data.clip_start,clip_end=s.camera.data.clip_end,portrait_target=[0,0,1.88],resolution=[s.render.resolution_x,s.render.resolution_y],pixel_aspect=[s.render.pixel_aspect_x,s.render.pixel_aspect_y]),render=dict(engine=s.render.engine,samples=s.cycles.samples,device=s.cycles.device,denoising=s.cycles.use_denoising,transparent=s.render.film_transparent,seed=s.cycles.seed),color=dict(display_device=s.display_settings.display_device,view_transform=s.view_settings.view_transform,look=s.view_settings.look,exposure=s.view_settings.exposure,gamma=s.view_settings.gamma),lights=lights,world=world,world_links=[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in s.world.node_tree.links] if s.world and s.world.use_nodes else [],compositor=[dict(name=n.name,type=n.type) for n in s.node_tree.nodes] if getattr(s,'use_nodes',False) and getattr(s,'node_tree',None) else [])
