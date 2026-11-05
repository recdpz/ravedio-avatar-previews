from pathlib import Path
import json,shutil
P=Path(__file__).parent;D=P.parent/'floating138/mobile-preview/260';c=json.loads((D/'catalogue260.json').read_text());selected=json.loads((P/'selected260.json').read_text())
for key in ['Feminine-straight','Feminine-side-sweep']:
 row=selected[key];path=c['builds']['Feminine']['hair'][key.split('-',1)[1]]['path'];assert Path(row['path']).name==Path(path).name;shutil.copy2(row['path'],D/path)
fits=json.loads((P/'fits4/fits260.json').read_text());sprouts=json.loads((P/'fits4/sprouts260.json').read_text());assert len(fits)==14 and len(sprouts)==16
for key,row in fits.items():style,hat=key.split('|');assert c['fits'][style][hat]['hair']==row['hair'];shutil.copy2(P/'fits4'/row['hair'],D/row['hair'])
for key,row in sprouts.items():assert c['sprouts'][key]['path']==row['path'];c['sprouts'][key]=row;shutil.copy2(P/'fits4'/row['path'],D/row['path'])
(D/'catalogue260.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf8',newline='\n');print('FEMALE_OVERLAY260_COMPLETE')
