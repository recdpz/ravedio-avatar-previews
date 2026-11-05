"""Fresh GLBs, true uncovered baselines, cloth-hidden coverage and top stress."""
import sys
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue249')
from common249 import *
cat=json.loads((D/'catalogue249.json').read_text());fits=json.loads((P/'fits249.json').read_text())
ANGLES=['front','threequarter','profile','rightprofile','rear','top','underside']

def assemble(b,style,top,mode='new',sprout=False,glasses=False):
 ref=fits[b+'-'+style+'-'+('open' if b=='Feminine' else 'tank')]
 bpy.ops.wm.open_mainfile(filepath=ref['source']);s=bpy.context.scene
 for o in list(s.objects):
  if o.type in ['MESH','CURVE'] and o.name!='Studio floor':u.delete(o)
 bc=cat['builds'][b];pair=cat['previousPashminaFits'][b+'-'+style] if mode=='before248' else cat['fits'][b+'-'+style]['pashmina']
 paths=dict(base=bc['shirtlessBase'] if top=='shirtless' else bc['base'],top=bc['tops'][top]['path'],bottom=bc['bottoms']['skirt' if b=='Feminine' else 'shorts']['path'],eyes=bc['eyes']['original']['path'],mouth=bc['mouths']['line']['path'],hair=bc['hair'][style]['path'] if mode=='uncovered' else pair['hair'])
 paths['eyelashes' if b=='Feminine' else 'groom']=bc['lashes']['original']['path'] if b=='Feminine' else bc['grooms']['stubble']['path']
 if mode not in ['uncovered','cloth-hidden']:
  paths['headgear']=cat['previousPashminaVariants'][b][cat['previousPashminaHairFamilies'][b][style]][top] if mode=='before248' else cat['pashminaVariants'][b][style][top]
 if sprout:paths['extra']=cat['sprouts'][b+'-'+style+'--pashmina']['path']
 if glasses:paths.update(bc['rectangular'])
 for group,path in paths.items():
  if path:imported((D/path).resolve(),group)
 u.tone(s,1);return s,paths

def close(s,key,angles=['front','profile','rear'],folder='review2'):
 for angle in angles:
  u.camera(s,angle,512,False);s.camera.data.ortho_scale=1.70;s.cycles.samples=24;s.render.filepath=str(P/folder/f'{key}-{angle}.png')
  floor=s.objects.get('Studio floor');hidden=floor.hide_render if floor else False
  if floor and angle=='underside':floor.hide_render=True
  try:bpy.ops.render.render(write_still=True)
  finally:
   if floor:floor.hide_render=hidden

def main():
 only=next((x.split('=',1)[1].split(',') for x in sys.argv if x.startswith('--styles=')),None)
 proof=json.loads((P/'proof249.json').read_text()) if only else {};assemblies=json.loads((P/'assemblies249.json').read_text()) if only else {}
 for b in cat['builds']:
  top='open' if b=='Feminine' else 'tank'
  for style in cat['builds'][b]['hair']:
   if only and style not in only:continue
   key=b+'-'+style;s,paths=assemble(b,style,top)
   render(s,key+'-export249',ANGLES,'review2',320,True);close(s,key+'-new',['front','threequarter','profile','rightprofile','rear','top','underside'])
   proof[key]=dict(final_glbs_reopened=True,full_angles=ANGLES,enlarged_angles=ANGLES,paths=paths,original_visible_hair=not bool(fits[b+'-'+style+'-'+top]['localized_gathers']))
   if style==('curls' if b=='Feminine' else 'taper'):
    u.camera(s,'front',512,False);bpy.ops.file.pack_all();p=P/'sources'/f'{b}-pashmina-assembly249.blend';bpy.ops.wm.save_as_mainfile(filepath=str(p),compress=True);bpy.ops.wm.open_mainfile(filepath=str(p));s=bpy.context.scene;portraits={}
    render(s,b+'-pashmina249',ANGLES,'fixtures',512,True)
    for size in [120,512]:render(s,b+'-portrait'+str(size)+'-249',['front'],'fixtures',size,False);portraits[str(size)]=u.settings(s)
    assert portraits['120']['camera']['matrix_world']==portraits['512']['camera']['matrix_world'] and portraits['120']['camera']['ortho_scale']==portraits['512']['camera']['ortho_scale']
    for tone in range(4):u.tone(s,tone);render(s,b+'-skin'+str(tone)+'-portrait249',['front'],'fixtures',128,False)
    assemblies[b]=dict(source=str(p),top=top,hair=style,packed=True,settings=u.requirements(s),portraits=portraits)
   for mode in ['cloth-hidden','uncovered','before248']:
    s,_=assemble(b,style,top,mode);close(s,key+'-'+mode,['front','profile','rear'])
   (P/'proof249.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf8');(P/'assemblies249.json').write_text(json.dumps(assemblies,indent=2)+'\n',encoding='utf8')
   print('VERIFY249',key,flush=True)
 print('VERIFY249_COMPLETE',len(proof),'styles; seven full and enlarged views, true uncovered and cloth-hidden comparisons')

def tops():
 looks=[(b,'curls' if b=='Feminine' else 'taper',top) for b in cat['builds'] for top in cat['builds'][b]['tops']]
 looks += [('Feminine',style,top) for style in ['straight','ponytail','box-braids'] for top in ['jersey','sweatshirt']]
 looks += [('Masculine','afro','sweatshirt'),('Feminine','space-buns','sweatshirt')]
 proof=json.loads((P/'top-proof249.json').read_text()) if '--resume' in sys.argv else {}
 for b,style,top in looks:
  key=b+'-'+style+'-'+top
  if key in proof:continue
  s,paths=assemble(b,style,top,sprout=True,glasses=top=='sweatshirt');render(s,key+'-stress249',ANGLES,'review2',320,True)
  close(s,key+'-stress249',['profile','rear','underside']);proof[key]=dict(angles=ANGLES,final_glbs=True,sprout=True,glasses=top=='sweatshirt',paths=paths)
  (P/'top-proof249.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf8');print('STRESS249',key,flush=True)
 print('TOP_VERIFY249_COMPLETE',len(proof))
if '--tops' in sys.argv:tops()
else:main()
