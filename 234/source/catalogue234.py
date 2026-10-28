from pathlib import Path
import json,shutil
P=Path(__file__).parent;R=P.parent/'floating138/mobile-preview';D=R/'234';D.mkdir(exist_ok=True)
cat=json.loads((R/'233/catalogue233.json').read_text(encoding='utf8'))
for b,c in cat['builds'].items():
 for item in c['eyes'].values():
  if item['path'].startswith('components/'):item['path']='../233/'+item['path']
 c['noses']={'none':c['noses']['none']};c['mouths']={'line':c['mouths']['line']}
 if b=='Feminine':c['lashes']={k:{'path':f'components/Feminine-{k}-lashes.glb'} for k in c['eyes']}
for c in cat['builds'].values():
 for item in c['eyes'].values():assert (D/item['path']).is_file()
(D/'catalogue234.json').write_text(json.dumps(cat,indent=2)+'\n',encoding='utf8')
shutil.copy2(R/'233/face-palette209.json',D/'face-palette209.json')
