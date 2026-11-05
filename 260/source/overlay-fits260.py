from pathlib import Path
import json,shutil
P=Path(__file__).parent;D=P.parent/'floating138/mobile-preview/260';c=json.loads((D/'catalogue260.json').read_text());fits=json.loads((P/'fits3/fits260.json').read_text());sprouts=json.loads((P/'fits3/sprouts260.json').read_text());assert len(fits)==28 and len(sprouts)==28
for key,row in fits.items():
 style,hat=key.split('|');assert c['fits'][style][hat]['hair']==row['hair'];shutil.copy2(P/'fits3'/row['hair'],D/row['hair'])
for key,row in sprouts.items():assert c['sprouts'][key]['path']==row['path'];shutil.copy2(P/'fits3'/row['path'],D/row['path']);c['sprouts'][key]=row
(D/'catalogue260.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf8',newline='\n')
print('OVERLAY260_COMPLETE',len(fits),len(sprouts))
