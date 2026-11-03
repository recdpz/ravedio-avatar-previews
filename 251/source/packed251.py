import sys,json,shutil
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue251')
from common251 import *
q=json.loads((P/'assemblies251.json').read_text())
for b,rec in q.items():
 bpy.ops.wm.open_mainfile(filepath=rec['source']);s=bpy.context.scene;u.camera(s,'front',512,False);s.camera.data.ortho_scale=1.65;s.cycles.samples=32;s.render.filepath='//'+b+'-reference251.png';settings=u.settings(s);assert settings['camera']['matrix_world']==rec['portraits']['512']['camera']['matrix_world'];assert settings['camera']['ortho_scale']==rec['portraits']['512']['camera']['ortho_scale'];bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=rec['source'],compress=True);shutil.copy2(rec['source'],D/'assemblies'/f'{b}-assembly251.blend');rec['packed_scene_settings']=settings
(P/'assemblies251.json').write_text(json.dumps(q,indent=2)+'\n');(D/'assemblies251.json').write_text(json.dumps(q,indent=2)+'\n');print('PACKED_CAMERA_MATCH251',flush=True)
