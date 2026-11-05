from pathlib import Path
import json,shutil
P=Path(__file__).parent;D=P.parent/'floating138/mobile-preview/261';c=json.loads((D/'catalogue261.json').read_text())
for key,row in json.loads((P/'fits/fits261.json').read_text()).items():
 style,hat=key.split('|');c['fits'][style][hat]['hair']=row['hair'];shutil.copy2(P/'fits'/row['hair'],D/row['hair'])
for key,row in json.loads((P/'fits/sprouts261.json').read_text()).items():c['sprouts'][key]=row;shutil.copy2(P/'fits'/row['path'],D/row['path'])
(D/'catalogue261.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf8')
print('FIT_PACKAGE261_COMPLETE')
