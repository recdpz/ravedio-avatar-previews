"""Repair from intact hair. Shared Z-up authoring coordinates, front -Y."""
import sys,json,hashlib
from pathlib import Path
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue235')
import common235 as c
c.P=Path(__file__).parent
from common235 import *
P=Path(__file__).parent;D=R/'249';OLD=R/'248'
CAT249=json.loads((OLD/'catalogue248.json').read_text())
FITS248=json.loads((P.parent/'catalogue248/fits248.json').read_text())
for folder in ['sources','components','review1','review2','fixtures','browser']:(P/folder).mkdir(exist_ok=True)
def source(style,top='open',build='Feminine',covered=False,native_cloth=False):
 family=CAT249['pashminaHairFamilies'][build][style];fit=FITS248[build+'-'+top+'-'+family]
 bpy.ops.wm.open_mainfile(filepath=fit['source']);s=bpy.context.scene
 for o in list(s.objects):
  if o.type in ['MESH','CURVE'] and o.name!='Studio floor' and not (native_cloth and o.get('component159')=='headgear'):u.delete(o)
 b=CAT249['builds'][build]
 paths=dict(base=b['base'],top=b['tops'][top]['path'],bottom=b['bottoms']['skirt' if build=='Feminine' else 'shorts']['path'],eyes=b['eyes']['original']['path'],mouth=b['mouths']['line']['path'],hair=CAT249['fits'][build+'-'+style]['pashmina']['hair'] if covered else b['hair'][style]['path'],headgear=CAT249['pashminaVariants'][build][family][top])
 paths['eyelashes' if build=='Feminine' else 'groom']=b['lashes']['original']['path'] if build=='Feminine' else b['grooms']['stubble']['path']
 for group,path in paths.items():
   if path and not (group=='headgear' and native_cloth):imported((OLD/path).resolve(),group)
 u.tone(s,1);a.setup();h._support_cache=None
 return s,paths
def head_object(s):
 obs=[o for o in s.objects if o.type=='MESH' and o.name.startswith('Skin / soft oval head')]
 assert len(obs)==1,[o.name for o in obs];return obs[0]
def views(s,key,folder='review1',size=384,body=False):
 render(s,key,['front','threequarter','profile','rightprofile','rear','top','underside'],folder,size,body)
def detail(s,key,angles=['front','profile','rear']):
 for angle in angles:
  u.camera(s,angle,512,False);s.camera.data.ortho_scale=1.52;s.cycles.samples=24;s.render.filepath=str(P/'review1'/f'{key}-detail-{angle}.png');bpy.ops.render.render(write_still=True)
