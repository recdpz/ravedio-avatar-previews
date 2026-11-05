import sys,json,math,random,hashlib
from pathlib import Path
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue250')
from common250 import *
import common235 as shared
P=Path(__file__).parent;R=P.parent/'floating138/mobile-preview';D=R/'251';OLD=R/'250';CAT251=json.loads((OLD/'catalogue250.json').read_text());shared.P=P
for n in ['sources','components','review1','review2','fixtures','browser']:(P/n).mkdir(exist_ok=True)
HEAD=None
def reset_head(s):
 global HEAD
 HEAD=tree([head_object(s)]);h._support_cache=None
def sp(th,ph,extra=.02):
 d=Vector((.48*math.sin(th)*math.sin(ph),-.405*math.sin(th)*math.cos(ph),.455*math.cos(th))).normalized();hit,_,_,_=HEAD.ray_cast(a.C,d,2);assert hit is not None;return hit+d*extra
def surf(x,y,extra=.02):
 hit,_,_,_=HEAD.ray_cast(Vector((x,y,3)),Vector((0,0,-1)),2);assert hit is not None,(x,y);return hit+Vector((0,0,extra))
def load251(b='Masculine',style='taper',hat='none',top=None,groom=False):
 bpy.ops.wm.open_mainfile(filepath=str(P.parent/'catalogue250/sources'/f'{b}-pashmina-assembly250.blend'));s=bpy.context.scene
 for o in list(s.objects):
  if o.type in ['MESH','CURVE'] and o.name!='Studio floor':u.delete(o)
 bc=CAT251['builds'][b];top=top or ('open' if b=='Feminine' else 'tank');paths=dict(base=bc['base'],top=bc['tops'][top]['path'],bottom=bc['bottoms']['skirt' if b=='Feminine' else 'shorts']['path'],eyes=bc['eyes']['original']['path'],mouth=bc['mouths']['line']['path'],hair=bc['hair'][style]['path'])
 if hat!='none':paths.update(CAT251['fits'][b+'-'+style][hat]);paths['headgear']=CAT251['pashminaVariants'][b][style][top] if hat=='pashmina' else paths['headgear']
 if b=='Feminine':paths['eyelashes']=bc['lashes']['original']['path']
 elif groom:paths['groom']=bc['grooms']['stubble']['path']
 for group,path in paths.items():
  if path:imported((OLD/path).resolve(),group)
 u.tone(s,1);a.setup();reset_head(s);s['build235']=b;s['hairStyle235']=style;return s,paths
def close251(s,key,angles,folder='review1',size=384,body=False):
 for angle in angles:
  u.camera(s,angle,size,body);s.camera.data.ortho_scale=2.7 if body else 1.65;s.cycles.samples=20;s.render.filepath=str(P/folder/f'{key}-{angle}.png');floor=s.objects.get('Studio floor');hidden=floor.hide_render if floor else False
  if floor and angle=='underside':floor.hide_render=True
  try:bpy.ops.render.render(write_still=True)
  finally:
   if floor:floor.hide_render=hidden
def gpu():
 pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='CUDA';pref.get_devices()
 for d in pref.devices:d.use=d.type=='CUDA'
 bpy.context.scene.cycles.device='GPU'

# glTF exports the grain image but not Blender's constant MixRGB tint.
# Preserve that constant explicitly in ordinary glTF PBR material metadata.
_export_before251=ex.export
def export251(s,path,group):
 result=_export_before251(s,path,group)
 import struct
 raw=Path(path).read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);changed=False
 for mat in g.get('materials',[]):
  pbr=mat.get('pbrMetallicRoughness',{})
  if mat.get('name','').startswith(('Hair / sculpted afro251','Hair / sculpted curly crown251')):mat['alphaMode']='OPAQUE';changed=True
  if mat.get('name','').startswith('Hair / clipped grain251') and 'baseColorTexture' in pbr:
   factor=pbr.get('baseColorFactor',[1,1,1,1]);pbr['baseColorFactor']=[.095,.037,.019,factor[3]];changed=True
 if changed:
  doc=json.dumps(g,separators=(',',':')).encode();doc+=b' '*((-len(doc))%4);binary=raw[28+n:];Path(path).write_bytes(struct.pack('<III',0x46546c67,2,28+len(doc)+len(binary))+struct.pack('<II',len(doc),0x4e4f534a)+doc+struct.pack('<II',len(binary),0x004e4942)+binary)
 return result
ex.export=export251
