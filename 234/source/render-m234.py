import bpy,sys,json
from pathlib import Path
P=Path(__file__).parent;O=P/'output';R=P.parent/'floating138/mobile-preview';cat=json.loads((R/'234/catalogue234.json').read_text(encoding='utf8'))
sys.path.insert(0,str(P.parent/'refinement224'));import utils224 as u
for key,item in cat['builds']['Masculine']['eyes'].items():
 bpy.ops.wm.open_mainfile(filepath=str(P.parent/'refinement224/scenes/Masculine-taper.blend'));s=bpy.context.scene;s.cycles.device='CPU'
 for o in list(s.objects):
  if o.get('component159') in ['eyes','nose','mouth']:u.delete(o)
 for path in [item['path'],cat['builds']['Masculine']['mouths']['line']['path']]:bpy.ops.import_scene.gltf(filepath=str((R/'234'/path).resolve()))
 u.render(s,O/'renders'/f'Masculine-{key}-front.png',384,'front')
