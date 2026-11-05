import sys,json
from pathlib import Path
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue260');from common260 import *
P=Path('E:/Ravedio-Avatar/catalogue262');R=P.parent/'floating138/mobile-preview';BASE=R/'261';CAT=json.loads((BASE/'catalogue261.json').read_text())
def load262(build,top='tank',bottom='shorts',hair=None):
 bpy.ops.wm.open_mainfile(filepath=str(P.parent/'catalogue251/sources'/f'{build}-assembly251.blend'));s=bpy.context.scene
 for o in list(s.objects):
  if o.type in ['MESH','CURVE'] and o.name!='Studio floor':u.delete(o)
 bc=CAT['builds'][build];hair=hair or ('ponytail' if build=='Feminine' else 'taper');paths=dict(base=bc.get('shirtlessBase') if top=='shirtless' else bc['base'],top=bc['tops'][top]['path'],bottom=bc['bottoms'][bottom]['path'],eyes=bc['eyes']['original']['path'],mouth=bc['mouths']['line']['path'],hair=bc['hair'][hair]['path'])
 if build=='Feminine':paths['lashes']=bc['lashes']['original']['path']
 for group,path in paths.items():
  if path:imported((BASE/path).resolve(),group)
 u.tone(s,1);a.setup();c.reset_head(s);s['build235']=build;return s
if __name__=='__main__':
 W=P/'hood-diagnostic';W.mkdir(exist_ok=True);rows={}
 for variant in ['full','no-opening','no-pouch','opening-only','pouch-only']:
  s=load262('Feminine','sweatshirt')
  for o in list(s.objects):
   if o.get('component159')!='top':continue
   opening='attached opening' in o.name.lower() or 'rolled opening' in o.name.lower();pouch='rounded resting hood' in o.name.lower() or 'smooth back seam' in o.name.lower()
   if (variant=='no-opening'and opening)or(variant=='no-pouch'and pouch)or(variant=='opening-only'and not opening)or(variant=='pouch-only'and not pouch):u.delete(o)
  u.bake(s);ex.export(s,W/(variant+'.glb'),'top');rows[variant]=[o.name for o in s.objects if o.get('component159')=='top']
 (W/'objects.json').write_text(json.dumps(rows,indent=2));print('HOOD_DIAGNOSTIC262_COMPLETE')
