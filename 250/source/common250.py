import sys,json,hashlib,math
from pathlib import Path
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue249')
import common249 as previous
from common249 import *
import common235 as shared
P=Path(__file__).parent;D=R/'250';OLD=R/'249'
shared.P=P
CAT250=json.loads((OLD/'catalogue249.json').read_text())
FITS249=json.loads((P.parent/'catalogue249/fits249.json').read_text())
for folder in ['sources','components','review1','review2','fixtures','browser','fields']:(P/folder).mkdir(exist_ok=True)
def load250(build,style,top=None):
 top=top or ('open' if build=='Feminine' else 'tank');ref=FITS249[build+'-'+style+'-'+top]
 bpy.ops.wm.open_mainfile(filepath=ref['source']);s=bpy.context.scene
 for o in list(s.objects):
  if o.type in ['MESH','CURVE'] and o.name!='Studio floor' and o.get('component159')!='headgear':u.delete(o)
 b=CAT250['builds'][build];paths=dict(base=b['shirtlessBase'] if top=='shirtless' else b['base'],top=b['tops'][top]['path'],bottom=b['bottoms']['skirt' if build=='Feminine' else 'shorts']['path'],eyes=b['eyes']['original']['path'],mouth=b['mouths']['line']['path'],hair=CAT250['fits'][build+'-'+style]['pashmina']['hair'],headgear=CAT250['pashminaVariants'][build][style][top])
 paths['eyelashes' if build=='Feminine' else 'groom']=b['lashes']['original']['path'] if build=='Feminine' else b['grooms']['stubble']['path']
 if ref.get('source_is_frozen248_with_field'):
  from fit249 import move_cloth
  field_key=build+'-'+style+('' if ref['field_reuse'] else '-'+top);field=np.load(P.parent/'catalogue249/fields'/f'{field_key}.npz');ob=next(o for o in s.objects if 'joined hood wrap and ends239' in o.name);old=[ob.matrix_world@v.co for v in ob.data.vertices];move_cloth(s,{int(i):Vector(d) for i,d in zip(field['ids'],field['delta'])},old)
 for group,path in paths.items():
  if path and group!='headgear':imported((OLD/path).resolve(),group)
 u.tone(s,1);a.setup();h._support_cache=None
 return s,paths
def close(s,key,angles,folder='review1',size=384):
 for angle in angles:
  u.camera(s,angle,size,False);s.camera.data.ortho_scale=1.65;s.cycles.samples=20;s.render.filepath=str(P/folder/f'{key}-{angle}.png')
  floor=s.objects.get('Studio floor');hidden=floor.hide_render if floor else False
  if floor and angle=='underside':floor.hide_render=True
  try:bpy.ops.render.render(write_still=True)
  finally:
   if floor:floor.hide_render=hidden
