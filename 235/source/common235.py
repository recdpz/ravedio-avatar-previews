import bpy,sys,math,json,random,struct
from pathlib import Path
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).parent; R=P.parent/'floating138/mobile-preview'; D=R/'235'
sys.path.insert(0,str(P.parent/'refinement224'));sys.path.insert(0,str(P.parent/'catalogue226'))
import utils224 as u, sculpt226 as a, export226 as ex, hair227 as h
_export226=ex.export
def export235(s,path,group):
 result=_export226(s,path,group);data=Path(path).read_bytes();n=struct.unpack_from('<I',data,12)[0];doc=json.loads(data[20:20+n]);changed=False
 for m in doc.get('materials',[]):
  p=m.get('pbrMetallicRoughness',{})
  if m.get('name','').startswith('Hair / neutral coverage235') and 'baseColorTexture' in p:
   p['baseColorFactor']=[.060,.022,.011,p.get('baseColorFactor',[1,1,1,1])[3]];changed=True
  sheen=m.get('extensions',{}).get('KHR_materials_sheen');source=bpy.data.materials.get(m.get('name',''))
  if group=='headgear' and sheen and source and source.use_nodes:
   bs=source.node_tree.nodes.get('Principled BSDF')
   if bs is not None:
    weight=float(bs.inputs['Sheen Weight'].default_value)
    if weight<.999:
     sheen['sheenColorFactor']=[float(v)*weight for v in sheen.get('sheenColorFactor',[1,1,1])];m.setdefault('extras',{})['authoringSheenWeight235']=weight;changed=True
 if changed:
  text=json.dumps(doc,separators=(',',':')).encode();text+=b' '*((-len(text))%4);binary=data[28+n:];Path(path).write_bytes(struct.pack('<III',0x46546c67,2,28+len(text)+len(binary))+struct.pack('<II',len(text),0x4e4f534a)+text+struct.pack('<II',len(binary),0x004e4942)+binary)
 return result
ex.export=export235
CAT=json.loads((R/'234/catalogue234.json').read_text(encoding='utf8'))
bpy.context.preferences.filepaths.save_version=0
for folder in ['sources','components','review1','review2','fits']:(P/folder).mkdir(parents=True,exist_ok=True)
def remove(groups):
 for o in list(bpy.context.scene.objects):
  if o.get('component159') in groups:u.delete(o)
def imported(path,group):
 before=set(bpy.context.scene.objects);bpy.ops.import_scene.gltf(filepath=str(path));out=[o for o in bpy.context.scene.objects if o not in before]
 for o in out:o['component159']=group
 bpy.context.view_layer.update();return [o for o in out if o.type=='MESH']
def library(path,groups):
 with bpy.data.libraries.load(str(path),link=False) as(src,dst):dst.objects=list(src.objects)
 out=[]
 for o in dst.objects:
  if o.get('component159') in groups:bpy.context.scene.collection.objects.link(o);out.append(o)
  else:u.delete(o)
 return out
def load(build):
 bpy.ops.wm.open_mainfile(filepath=str(P.parent/'refinement224/scenes'/('Feminine-uncovered.blend' if build=='Feminine' else 'Masculine-taper.blend')))
 s=bpy.context.scene;s.cycles.device='CPU';remove(['nose','mouth','eyes','eyelashes','glasses','lenses','extra','headgear'])
 c=CAT['builds'][build]
 for group,path in [('mouth',c['mouths']['line']['path']),('eyes',c['eyes']['original']['path'])]:imported((R/'234'/path).resolve(),group)
 if build=='Feminine':imported((R/'234'/c['lashes']['original']['path']).resolve(),'eyelashes')
 u.tone(s,1);h._support_cache=None;a.setup();return s
def tree(obs):
 v=[];f=[]
 for o in obs:
  if o.type!='MESH':continue
  k=len(v);v.extend(o.matrix_world@x.co for x in o.data.vertices);f.extend([k+i for i in p.vertices] for p in o.data.polygons)
 return BVHTree.FromPolygons(v,f)
def protect(s):return {k:v for k,v in u.object_geometry(s).items() if s.objects[k].get('component159') not in ['hair','headgear','glasses','lenses','extra']}
def check(s,p):assert p==protect(s),'Protected anatomy/wardrobe/face changed'
def render(s,key,angles,folder='review1',size=256,body=False):
 for angle in angles:
  u.camera(s,angle,size,body);s.cycles.samples=16 if folder=='review1' else 32;s.render.filepath=str(P/folder/f'{key}-{angle}.png');floor=s.objects.get('Studio floor');previous=floor.visible_camera if floor else True;hidden=floor.hide_render if floor else False
  try:
   if floor and angle=='underside':floor.visible_camera=False;floor.hide_render=True
   bpy.ops.render.render(write_still=True)
  finally:
   if floor:floor.visible_camera=previous;floor.hide_render=hidden
def save(s,key,groups):
 u.bake(s);bpy.ops.file.pack_all();src=P/'sources'/f'{key}.blend';bpy.ops.wm.save_as_mainfile(filepath=str(src),compress=True)
 bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene
 out={}
 for group in groups:
  path=P/'components'/f'{key}-{group}.glb';ex.export(s,path,group);out[group]='components/'+path.name
 return out
def rgba(o,values):
 for c in list(o.data.color_attributes):o.data.color_attributes.remove(c)
 c=o.data.color_attributes.new(name='Coverage235',type='FLOAT_COLOR',domain='POINT');c.data.foreach_set('color',np.asarray(values,dtype='f').ravel());o.data.color_attributes.active_color=c;o.data.color_attributes.render_color_index=0
 for m in o.data.materials:
  if not m.use_nodes:continue
  bs=m.node_tree.nodes.get('Principled BSDF');vc=m.node_tree.nodes.new('ShaderNodeVertexColor');vc.layer_name='Coverage235';m.node_tree.links.new(vc.outputs['Alpha'],bs.inputs['Alpha'])
def smooth(t):return h.smooth(t)
