import sys,json,shutil
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue252')
from common252 import *
CAT=json.loads((D/'catalogue252.json').read_text())
def assemble(b,style,hat='none'):
 s,_=load252(b,style,hat);remove(['hair']);p=CAT['builds'][b]['hair'][style]['path'] if hat=='none' else CAT['fits'][b+'-'+style][hat]['hair'];imported((D/p).resolve(),'hair');u.tone(s,1);c.gpu();return s
out=json.loads((P/'assemblies252.json').read_text()) if (P/'assemblies252.json').exists() else {};clips=json.loads((P/'bare-sprouts252.json').read_text()) if (P/'bare-sprouts252.json').exists() else {}
for style,rec in json.loads((P/'hair252.json').read_text()).items():
 b='Feminine' if style=='straight' else 'Masculine';s=assemble(b,style);import accessories235;clip=accessories235.sprout();u.bake(s);ep=P/'components'/f'{b}-{style}-none252-sprout.glb';ex.export(s,ep,'extra');clip['path']='components/'+ep.name;clips[b+'-'+style+'--none']=clip;remove(['extra'])
 if style in ['taper','straight'] and '--clips-only' not in sys.argv:
  portraits={}
  for size in [120,512]:render252(s,b+'-portrait'+str(size)+'252',('front',),folder='fixtures',size=size);portraits[str(size)]=u.settings(s)
  for tone in range(4):u.tone(s,tone);render252(s,b+'-skin'+str(tone)+'252',('front',),folder='fixtures',size=128)
  u.tone(s,1);u.camera(s,'front',512,False);s.camera.data.ortho_scale=1.65;s.cycles.samples=32;s.render.filepath='//'+b+'-reference252.png';bpy.ops.outliner.orphans_purge(do_recursive=True);bpy.ops.file.pack_all();src=P/'sources'/f'{b}-assembly252.blend';bpy.ops.wm.save_as_mainfile(filepath=str(src),compress=True);assert portraits['120']['camera']['matrix_world']==portraits['512']['camera']['matrix_world'];assert portraits['120']['camera']['ortho_scale']==portraits['512']['camera']['ortho_scale'];out[b]=dict(source=str(src),packed=True,portraits=portraits,settings=u.requirements(s),packed_scene_settings=u.settings(s))
 print('BARE_SPROUT252',style,flush=True)
(P/'bare-sprouts252.json').write_text(json.dumps(clips,indent=2)+'\n',encoding='utf8');(P/'assemblies252.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8');print('ASSEMBLIES252_COMPLETE',flush=True)
