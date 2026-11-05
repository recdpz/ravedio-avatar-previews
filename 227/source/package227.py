"""Stage reviewed static assets; leaves224 and all old published pages untouched."""
from pathlib import Path
import json,shutil
from PIL import Image
P=Path(__file__).parent;O=P/'revision227';R=P.parent/'floating138/mobile-preview';D=R/'227';D.mkdir(exist_ok=True)
proof=json.loads((O/'export-proof.json').read_text());baseline=json.loads((R/'224/looks224.json').read_text())
labels={'straight':'Straight','curls':'Curls','side-sweep':'Side sweep','space-buns':'Space buns','twin-braids':'Twin braids','box-braids':'Box braids','curly-top':'Curly top','afro':'Afro','buzz':'Buzz','flow':'Flow','locs':'Locs','bucket':'Bucket hat','cowboy':'Cowboy hat','beanie':'Beanie','headband':'Headband','ears':'Animal ears','pashmina':'Pashmina','reading':'Reading glasses','wayfarer':'Rectangular glasses','cat-eye':'Cat-eye glasses','heart':'Heart glasses','wraparound':'Sport glasses','kaleidoscope':'Faceted frames','gems':'Face gems','sprout':'Sprout'}
for folder in ['components','native','portraits','before']:(D/folder).mkdir(exist_ok=True)
config={}
for key,item in proof.items():
 basekey='Feminine-uncovered' if item['build']=='Feminine' else 'Masculine-taper';base=baseline[basekey];parts={g:'../224/'+p.removeprefix('./') for g,p in base['components'].items()}
 for g,p in item['components'].items():shutil.copy2(O/p,D/p);parts[g]=p
 for p in (O/'roundtrip').glob(key+'-*.png'):shutil.copy2(p,D/'native'/p.name)
 for p in (O/'portraits').glob(key+'-*.png'):shutil.copy2(p,D/'portraits'/p.name)
 for p in (P/'review1').glob(key+'-*.png'):shutil.copy2(p,D/'before'/p.name)
 config[key]={'label':item['build']+' · '+labels[item['style']],'components':parts,'build':item['build'],'style':item['style'],'portraits':True,'note':'Correction candidate. Fixed224 body, face, wardrobe, skin palette and studio. New components are not yet owner-approved or native-phone-qualified.','source':item['source']}
(D/'looks227.json').write_text(json.dumps(config,indent=2)+'\n')
shutil.copy2(R/'224/face-palette209.json',D/'face-palette209.json')
shutil.copytree(R/'224/vendor',D/'vendor',dirs_exist_ok=True)
(D/'asset-statistics227.json').write_text(json.dumps({k:v['statistics'] for k,v in proof.items()},indent=2)+'\n')
(D/'export-proof227.json').write_text(json.dumps(proof,indent=2)+'\n')
print('STAGED227',len(config))
