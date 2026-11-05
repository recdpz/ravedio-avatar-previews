"""Matched final-GLB close-ups of the small upper joins, not a new camera preset."""
import sys,json
from pathlib import Path
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue235')
import common235 as c
c.P=Path(__file__).parent
from common235 import *
for build in ['Feminine','Masculine']:
 bpy.ops.wm.open_mainfile(filepath=str(P/'sources'/f'{build}-pashmina-assembly247.blend'));s=bpy.context.scene
 for revision in [247,246]:
  if revision==246:
   for ob in list(s.objects):
    if ob.get('component159')=='headgear':u.delete(ob)
   table=json.loads((R/'246/catalogue246.json').read_text());top='open' if build=='Feminine' else 'tank'
   imported((R/'246'/table['pashminaTops'][build][top]).resolve(),'headgear')
  for angle in ['front','threequarter']:
   u.camera(s,angle,768,True);s.camera.data.ortho_scale=.65;s.camera.location.z+=.10;s.cycles.samples=24
   s.render.filepath=str(P/'review2'/f'{build}-upper{revision}-{angle}.png');bpy.ops.render.render(write_still=True)
print('UPPER247 matched final exports complete',flush=True)
