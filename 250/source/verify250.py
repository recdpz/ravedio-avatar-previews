import sys
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue250')
from common250 import *
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='CUDA';prefs.get_devices()
for device in prefs.devices:device.use=device.type=='CUDA'
cat=json.loads((D/'catalogue250.json').read_text());fits=json.loads((P/'fits250.json').read_text());ANGLES=['front','threequarter','profile','rightprofile','rear','top','underside']
def assemble(b,style,top,mode='new',extra=False):
 ref=fits[b+'-'+style+'-'+('open' if b=='Feminine' else 'tank')];bpy.ops.wm.open_mainfile(filepath=ref['source']);s=bpy.context.scene
 for o in list(s.objects):
  if o.type in ['MESH','CURVE'] and o.name!='Studio floor':u.delete(o)
 bc=cat['builds'][b];pair=cat['previousPashminaFits'][b+'-'+style] if mode=='before249' else cat['fits'][b+'-'+style]['pashmina'];paths=dict(base=bc['shirtlessBase'] if top=='shirtless' else bc['base'],top=bc['tops'][top]['path'],bottom=bc['bottoms']['skirt' if b=='Feminine' else 'shorts']['path'],eyes=bc['eyes']['original']['path'],mouth=bc['mouths']['line']['path'],hair=bc['hair'][style]['path'] if mode=='uncovered' else pair['hair']);paths['eyelashes' if b=='Feminine' else 'groom']=bc['lashes']['original']['path'] if b=='Feminine' else bc['grooms']['stubble']['path']
 if mode not in ['uncovered','cloth-hidden']:paths['headgear']=cat['previousPashminaVariants'][b][style][top] if mode=='before249' else cat['pashminaVariants'][b][style][top]
 if extra:paths.update(extra=cat['sprouts'][b+'-'+style+'--pashmina']['path'],**bc['rectangular'])
 for group,path in paths.items():
  if path:imported((D/path).resolve(),group)
 u.tone(s,1);s.cycles.device='GPU';return s,paths
def main():
 proof=json.loads((P/'proof250.json').read_text()) if '--resume' in sys.argv and (P/'proof250.json').exists() else {};assemblies=json.loads((P/'assemblies250.json').read_text()) if (P/'assemblies250.json').exists() else {}
 for b,bc in cat['builds'].items():
  top='open' if b=='Feminine' else 'tank'
  for style in bc['hair']:
   key=b+'-'+style
   if key in proof:continue
   s,paths=assemble(b,style,top);close(s,key+'-new',ANGLES,'review2',384)
   if style==('curls' if b=='Feminine' else 'taper'):
    render(s,b+'-pashmina250',ANGLES,'fixtures',384,True);u.camera(s,'front',512,False);bpy.ops.file.pack_all();src=P/'sources'/f'{b}-pashmina-assembly250.blend';bpy.ops.wm.save_as_mainfile(filepath=str(src),compress=True);portraits={}
    for size in [120,512]:render(s,b+'-portrait'+str(size)+'-250',['front'],'fixtures',size,False);portraits[str(size)]=u.settings(s)
    settings=u.requirements(s)
    for tone in range(4):u.tone(s,tone);render(s,b+'-skin'+str(tone)+'-portrait250',['front'],'fixtures',128,False)
    assert portraits['120']['camera']['matrix_world']==portraits['512']['camera']['matrix_world'] and portraits['120']['camera']['ortho_scale']==portraits['512']['camera']['ortho_scale'];assemblies[b]=dict(source=str(src),packed=True,settings=settings,portraits=portraits)
   for mode in (['cloth-hidden','before249'] if style in ['straight','curls','ponytail','taper','afro'] else ['cloth-hidden']):
    s,_=assemble(b,style,top,mode);close(s,key+'-'+mode,['front','profile','rear'],'review2',320 if mode=='cloth-hidden' else 384)
   proof[key]=dict(paths=paths,full_angles=ANGLES,enlarged_angles=ANGLES,cloth_hidden=True,matched249=True,final_glbs=True);(P/'proof250.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf8');(P/'assemblies250.json').write_text(json.dumps(assemblies,indent=2)+'\n',encoding='utf8');print('VERIFY250',key,flush=True)
 print('VERIFY250_COMPLETE',len(proof),flush=True)
def tops():
 looks=[(b,'curls' if b=='Feminine' else 'taper',top) for b in cat['builds'] for top in cat['builds'][b]['tops']]+[('Feminine',hair,top) for hair in ['straight','ponytail','box-braids'] for top in ['jersey','sweatshirt']]+[('Masculine','afro','sweatshirt'),('Feminine','space-buns','sweatshirt')];proof=json.loads((P/'top-proof250.json').read_text()) if '--resume' in sys.argv and (P/'top-proof250.json').exists() else {}
 for b,style,top in looks:
  key=b+'-'+style+'-'+top
  if key in proof:continue
  s,paths=assemble(b,style,top,extra=True);close(s,key+'-stress250',['front','profile','rear','underside'],'review2',384);proof[key]=dict(paths=paths,final_glbs=True,angles=['front','profile','rear','underside'],rectangular_glasses=True,lens_finish='Source default tinted; clear variant tested separately in browser',sprout=True);(P/'top-proof250.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf8');print('STRESS250',key,flush=True)
 print('TOP_VERIFY250_COMPLETE',len(proof),flush=True)
if '--tops' in sys.argv:tops()
else:main()
