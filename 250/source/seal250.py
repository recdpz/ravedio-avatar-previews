from pathlib import Path
import json,hashlib,subprocess,ast,datetime
P=Path(__file__).parent;R=P.parent/'floating138/mobile-preview';D=R/'250';local=json.loads((P/'browser250.json').read_text());close=json.loads((P/'close250.json').read_text());assert len(local['checks'])==122 and not local['errors'] and not local['http'] and not close['errors']
images=list((P/'browser').glob('*.png'));assert len(images)==81 and min(f.stat().st_mtime for f in images)>max(f.stat().st_mtime for f in (D/'components').glob('*.glb'))
close.update(verified_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),final_components={x['path']:x['sha256'] for x in json.loads((D/'technical250.json').read_text())},screenshots=len(images))
for name,value in [('browser250.json',local),('close250.json',close)]:(D/name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf8')
for f in D.rglob('*'):
 if f.is_file() and f.suffix in ['.json','.txt','.js','.html','.py','.cjs']:f.write_text(f.read_text(encoding='utf-8-sig').replace('\r\n','\n'),encoding='utf8',newline='\n')
files=[dict(path=f.relative_to(D).as_posix(),bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in sorted(D.rglob('*')) if f.is_file() and f.name!='manifest250.json'];manifest=dict(revision=250,baseline_commit='3228f60f6402b0ce0104ce83eb656a975d828ef3',files=files);(D/'manifest250.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8')
print('SEALED250',len(files),'files',sum(x['bytes'] for x in files),'bytes')
