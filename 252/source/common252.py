import sys,json,math,random,hashlib,struct,shutil
from pathlib import Path
import numpy as np
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue251')
from common251 import *
import common251 as c
P=Path('E:/Ravedio-Avatar/catalogue252');R=P.parent/'floating138/mobile-preview';D=R/'252';OLD=R/'251';CAT252=json.loads((OLD/'catalogue251.json').read_text());shared.P=P
sp=c.sp;surf=c.surf

def load252(b='Masculine',style='taper',hat='none',top=None):
 bpy.ops.wm.open_mainfile(filepath=str(P.parent/'catalogue251/sources'/f'{b}-assembly251.blend'));s=bpy.context.scene
 for o in list(s.objects):
  if o.type in ['MESH','CURVE'] and o.name!='Studio floor':u.delete(o)
 bc=CAT252['builds'][b];top=top or ('open' if b=='Feminine' else 'tank');paths=dict(base=bc['base'],top=bc['tops'][top]['path'],bottom=bc['bottoms']['skirt' if b=='Feminine' else 'shorts']['path'],eyes=bc['eyes']['original']['path'],mouth=bc['mouths']['line']['path'],hair=bc['hair'][style]['path'])
 if b=='Feminine':paths['eyelashes']=bc['lashes']['original']['path']
 if hat!='none':paths.update(CAT252['fits'][b+'-'+style][hat])
 if hat=='pashmina':paths['headgear']=CAT252['pashminaVariants'][b][CAT252['pashminaHairFamilies'][b][style]][top]
 for group,path in paths.items():
  if path:imported((OLD/path).resolve(),group)
 u.tone(s,1);a.setup();c.reset_head(s);s['build235']=b;s['hairStyle235']=style;s['revision252']=True;return s,paths

def render252(s,key,angles=('front','threequarter','profile','rightprofile','rear','top','underside'),folder='review1',size=448,body=False):
 c.gpu()
 for angle in angles:
  u.camera(s,angle,size,body);s.camera.data.ortho_scale=2.7 if body else 1.65;s.cycles.samples=24;s.render.filepath=str(P/folder/f'{key}-{angle}.png');floor=s.objects.get('Studio floor');old=floor.hide_render if floor else False
  if floor and angle=='underside':floor.hide_render=True
  try:bpy.ops.render.render(write_still=True)
  finally:
   if floor:floor.hide_render=old

_export=c.ex.export
def export252(s,path,group):
 result=_export(s,path,group);raw=Path(path).read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);changed=False
 for m in g.get('materials',[]):
  name=m.get('name','')
  if name.startswith('Hair252 /'):
   source=bpy.data.materials.get(name)
   if source is not None and source.get('hairBase252') is not None:m.setdefault('pbrMetallicRoughness',{})['baseColorFactor']=list(source['hairBase252'])
   m['alphaMode']='BLEND' if 'fade coverage' in name or 'buzz edge' in name else 'OPAQUE';m['doubleSided']=m['alphaMode']!='BLEND';changed=True
 if changed:
  data=json.dumps(g,separators=(',',':')).encode();data+=b' '*((-len(data))%4);binary=raw[28+n:];Path(path).write_bytes(struct.pack('<III',0x46546c67,2,28+len(data)+len(binary))+struct.pack('<II',len(data),0x4e4f534a)+data+struct.pack('<II',len(binary),0x004e4942)+binary)
 return result
ex.export=export252
