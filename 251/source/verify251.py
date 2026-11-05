import sys,json,shutil
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue251')
from common251 import *
CAT=json.loads((D/'catalogue251.json').read_text());fits=json.loads((P/'fits251.json').read_text());ANGLES=['front','threequarter','profile','rightprofile','rear','top','underside']
def assemble(b,style,hat='none',top=None,highlight=False):
 s,_=load251(b,style);top=top or ('open' if b=='Feminine' else 'tank')
 for ob in list(s.objects):
  if ob.type in ['MESH','CURVE'] and ob.name!='Studio floor':u.delete(ob)
 bc=CAT['builds'][b];paths=dict(base=bc['base'],hair=bc['hair'][style]['path'],top=bc['tops'][top]['path'],bottom=bc['bottoms']['skirt' if b=='Feminine' else 'shorts']['path'],eyes=bc['eyes']['original']['path'],mouth=bc['mouths']['line']['path'])
 if b=='Feminine':paths['eyelashes']=bc['lashes']['original']['path']
 if hat!='none':paths.update(CAT['fits'][b+'-'+style][hat])
 if hat=='pashmina':paths['headgear']=CAT['pashminaVariants'][b][CAT['pashminaHairFamilies'][b][style]][top]
 if b=='Feminine' and style=='twin-braids':paths['hairLengths']=CAT['braidLengths']['pashmina' if hat=='pashmina' else 'normal'][top]
 if highlight:
  for k in ['hair','hairLengths']:
   if k in paths:paths[k]=CAT['highlights'][paths[k]]
 for k,path in paths.items():
  if path:imported((D/path).resolve(),k)
 u.tone(s,1);gpu();return s,paths

def main():
 proofs=json.loads((P/'proof251.json').read_text()) if (P/'proof251.json').exists() else {};assemblies=json.loads((P/'assemblies251.json').read_text()) if (P/'assemblies251.json').exists() else {};looks=[('Masculine',style,'none',None,False) for style in json.loads((P/'hair251.json').read_text())]
 looks += [(b,style,hat,None,False) for key in fits for b in CAT['builds'] for style in CAT['builds'][b]['hair'] for hat in CAT['headwear'] if key==b+'-'+style+'-'+hat]
 looks += [('Feminine','twin-braids',hat,top,False) for hat in ['none','pashmina'] for top in CAT['builds']['Feminine']['tops']]
 looks += [(b,style,hat,None,True) for b,style,hat in [('Masculine','taper','none'),('Masculine','curly-top','none'),('Masculine','flow','none'),('Feminine','ponytail','none'),('Feminine','curls','none'),('Feminine','twin-braids','pashmina')]]
 for b,style,hat,top,highlight in looks:
  key='-'.join([b,style,hat,top or 'default','highlights' if highlight else 'default'])
  if key in proofs:continue
  s,paths=assemble(b,style,hat,top,highlight);seven=(hat=='none' and b=='Masculine') or (b=='Feminine' and (style=='space-buns' or (style=='ponytail' and hat in ['beanie','pashmina']) or style=='twin-braids'));angles=ANGLES if seven and top is None else ['front','profile','rear'];close251(s,key+'-export251',angles,'review2',384)
  if (b,style,hat,top,highlight) in [('Masculine','flow','cap',None,False),('Feminine','ponytail','pashmina',None,False)]:
   bpy.ops.file.pack_all();src=P/'sources'/f'{b}-assembly251.blend';u.camera(s,'front',512,False);bpy.ops.wm.save_as_mainfile(filepath=str(src),compress=True);portraits={}
   for size in [120,512]:close251(s,b+'-portrait'+str(size)+'251',['front'],'fixtures',size);portraits[str(size)]=u.settings(s)
   for tone in range(4):u.tone(s,tone);close251(s,b+'-skin'+str(tone)+'251',['front'],'fixtures',128)
   assert portraits['120']['camera']['matrix_world']==portraits['512']['camera']['matrix_world'] and portraits['120']['camera']['ortho_scale']==portraits['512']['camera']['ortho_scale'];assemblies[b]=dict(source=str(src),packed=True,paths=paths,settings=u.requirements(s),portraits=portraits)
  proofs[key]=dict(paths=paths,angles=angles,final_glbs=True);(P/'proof251.json').write_text(json.dumps(proofs,indent=2)+'\n');(P/'assemblies251.json').write_text(json.dumps(assemblies,indent=2)+'\n');print('VERIFY251',key,flush=True)
 print('VERIFY251_COMPLETE',len(proofs),flush=True)
if __name__=='__main__':main()
