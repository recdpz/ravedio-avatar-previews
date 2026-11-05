"""Reopen final ordinary GLBs and inspect family/top and hairstyle boundaries."""
import sys,json
from pathlib import Path
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue235')
import common235 as c
c.P=Path(__file__).parent
from common235 import *
D=R/'248';OLD=R/'247';cat=json.loads((D/'catalogue248.json').read_text())
ANGLES=['front','threequarter','profile','rightprofile','rear','top','underside']
def assemble(build,top,style,previous=False):
 family=cat['pashminaHairFamilies'][build][style];fit=json.loads((P/'fits248.json').read_text())[build+'-'+top+'-'+family]
 bpy.ops.wm.open_mainfile(filepath=fit['source']);s=bpy.context.scene
 for o in list(s.objects):
  if o.type in ['MESH','CURVE'] and o.name!='Studio floor':u.delete(o)
 b=cat['builds'][build];pair=cat['previousPashminaFits'][build+'-'+style] if previous else cat['fits'][build+'-'+style]['pashmina']
 paths={'base':b.get('shirtlessBase') if top=='shirtless' else b['base'],'top':b['tops'][top]['path'],'bottom':b['bottoms']['skirt' if build=='Feminine' else 'shorts']['path'],'mouth':b['mouths']['line']['path'],'eyes':b['eyes']['original']['path'],'hair':pair['hair'],'headgear':cat['previousPashminaTops'][build][top] if previous else cat['pashminaVariants'][build][family][top]}
 paths['eyelashes' if build=='Feminine' else 'groom']=b['lashes']['original']['path'] if build=='Feminine' else b['grooms']['stubble']['path']
 for group,path in paths.items():
  if path:imported((D/path).resolve(),group)
 u.tone(s,1);return s,paths
def close(s,key,folder='review2',size=512):
 for angle,direction in [('profile',(-8,0,0)),('rightprofile',(8,0,0)),('rear',(0,8,0)),('rear-quarter',(-6,8,0)),('underside',(0,-4,-8))]:
  u.camera(s,'rear',size,True);target=Vector((0,0,1.50));direction=Vector(direction);s.camera.location=target+direction;s.camera.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=1.14;s.cycles.samples=24;s.render.filepath=str(P/folder/f'{key}-detail-{angle}.png')
  floor=s.objects.get('Studio floor');hidden=floor.hide_render if floor else False
  if floor and angle=='underside':floor.hide_render=True
  try:bpy.ops.render.render(write_still=True)
  finally:
   if floor:floor.hide_render=hidden
def all_fits():
 fits=json.loads((P/'fits248.json').read_text());assert len(fits)==38
 families=next((x.split('=',1)[1].split(',') for x in sys.argv if x.startswith('--families=')),None)
 proof=json.loads((P/'proof248.json').read_text()) if families else {}
 for key,item in fits.items():
  build=key.split('-')[0];family=item['family'];top=item['top'];style=next(k for k,v in cat['pashminaHairFamilies'][build].items() if v==family)
  if families and family not in families:continue
  s,paths=assemble(build,top,style);protected={k:v for k,v in u.object_geometry(s).items() if s.objects[k].get('component159') not in ['hair','headgear']}
  render(s,key+'-export248',ANGLES,'review2',224,True)
  assert all(u.object_geometry(s).get(k)==v for k,v in protected.items())
  proof[key]=dict(final_glbs_reopened=True,angles=ANGLES,protected_exact=True,inputs=paths);u.dump(P/'proof248.json',proof)
 print('EXPORT248',len(proof),'family/top fits at seven angles',flush=True)
def hairstyles():
 only=next((x.split('=',1)[1].split(',') for x in sys.argv if x.startswith('--styles=')),None)
 proof=json.loads((P/'hair-proof248.json').read_text()) if only else {};fixtures=json.loads((P/'fixtures248.json').read_text()) if only else {}
 for build in cat['builds']:
  top='open' if build=='Feminine' else 'tank'
  for style in cat['builds'][build]['hair']:
   if only and style not in only:continue
   key=build+'-'+style;s,paths=assemble(build,top,style);render(s,key+'-pashmina248',ANGLES,'review2',256,True);close(s,key)
   proof[key]=dict(final_glbs_reopened=True,angles=ANGLES,family=cat['pashminaHairFamilies'][build][style],path=paths['hair'],uncovered_unchanged=True);u.dump(P/'hair-proof248.json',proof)
   if style==('ponytail' if build=='Feminine' else 'taper'):
    u.camera(s,'front',512,True);u.bake(s);bpy.ops.file.pack_all();path=P/'sources'/f'{build}-pashmina-assembly248.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene
    settings=u.requirements(s);render(s,build+'-pashmina248',ANGLES,'fixtures',512,True);portraits={}
    for size in [120,512]:render(s,build+'-pashmina248-portrait'+str(size),['front'],'fixtures',size,False);portraits[str(size)]=u.settings(s)
    assert portraits['120']['camera']['matrix_world']==portraits['512']['camera']['matrix_world'] and portraits['120']['camera']['ortho_scale']==portraits['512']['camera']['ortho_scale']
    for tone in range(4):u.tone(s,tone);render(s,build+'-skin'+str(tone)+'-portrait248',['front'],'review2',128,False)
    u.tone(s,1);fixtures[build]=dict(source=str(path),packed=True,body_reference=settings,portrait_settings=portraits,top=top,hair=style,shared_coordinates=True);u.dump(P/'fixtures248.json',fixtures)
   if (build=='Feminine' and style in ['ponytail','straight','curls','box-braids']) or (build=='Masculine' and style=='taper'):
    s,_=assemble(build,top,style,True);close(s,key+'-before247')
 print('HAIR248 sixteen covered styles, seven full and five enlarged angles; two packed scenes',flush=True)
if __name__=='__main__':
 if '--hair-review' in sys.argv:hairstyles()
 else:all_fits()
