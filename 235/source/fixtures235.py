"""Two packed final assemblies and matched reference renders for the handoff."""
import sys
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue235')
from common235 import *
import fits235 as fits

def main():
 records={};(P/'fixtures').mkdir(exist_ok=True)
 pairs=json.loads((P/'fits235.json').read_text())
 for build,style in [('Feminine','ponytail'),('Masculine','taper')]:
  s=load(build);remove(['hair','headgear','extra']);pair=pairs[build+'-'+style]['pashmina']
  for group,path in pair.items():imported((P/path if path.startswith('components/') else R/'234'/path).resolve(),group)
  u.camera(s,'front',512,True);u.bake(s);bpy.ops.file.pack_all();path=P/'sources'/f'{build}-pashmina-assembly235.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene
  body_settings=u.requirements(s);key=build+'-pashmina235';render(s,key,['front','threequarter','profile','rightprofile','rear','top','underside'],'fixtures',512,True)
  portraits={}
  for size in [120,512]:
   render(s,key+'-portrait'+str(size),['front'],'fixtures',size,False);portraits[str(size)]=u.settings(s)
  assert portraits['120']['camera']['matrix_world']==portraits['512']['camera']['matrix_world'];assert portraits['120']['camera']['ortho_scale']==portraits['512']['camera']['ortho_scale']
  records[build]=dict(source=str(path),packed=True,hair=style,headwear='pashmina',detail='none',skin_index=1,no_nose=True,mouth='line',body_reference=body_settings,portrait_settings=portraits,shared_coordinates=True,native_phone_qualified=False)
  u.dump(P/'fixtures235.json',records)
 print('FIXTURES235 packed and reopened; both portrait resolutions share framing')
if __name__=='__main__':main()
