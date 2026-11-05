"""Normalize and verify exact catalogue dependencies, then seal238 outputs."""
from pathlib import Path
import json,hashlib,subprocess,ast
P=Path(__file__).parent;R=P.parent/'floating138/mobile-preview';D=R/'238';commit='20524322159ac1c33d4f9c2ddb82753c19d6e912'
browser=json.loads((P/'browser238.json').read_text());close=json.loads((P/'close238.json').read_text())
assert not browser['errors'] and not browser['http'] and browser['mobileLayout'] and browser['oneCanvas'];assert not close['errors']
for name in ['browser238.json','close238.json']:(D/name).write_bytes((P/name).read_bytes())
for name in ['close238.cjs','seal238.py']:(D/'source'/name).write_bytes((P/name).read_bytes())
for f in (D/'source').glob('*.py'):ast.parse(f.read_text(encoding='utf8'),filename=f.name)
refs=set()
def walk(obj):
    if isinstance(obj,dict):
        for v in obj.values():walk(v)
    elif isinstance(obj,list):
        for v in obj:walk(v)
    elif isinstance(obj,str) and obj.endswith('.glb'):refs.add((D/obj).resolve())
walk(json.loads((D/'catalogue238.json').read_text()))
deps=[];proc=subprocess.Popen(['git','cat-file','--batch'],cwd=R,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
for f in sorted(refs):
    assert f.is_relative_to(R.resolve()) and f.is_file(),f
    if f.is_relative_to(D.resolve()):continue
    relative=f.relative_to(R.resolve()).as_posix();raw=f.read_bytes();sha=hashlib.sha256(raw).hexdigest()
    proc.stdin.write((commit+':'+relative+'\n').encode());proc.stdin.flush();h=proc.stdout.readline().split();assert len(h)==3 and h[1]==b'blob',relative
    saved=proc.stdout.read(int(h[2]));assert proc.stdout.read(1)==b'\n';assert hashlib.sha256(saved).hexdigest()==sha,relative
    deps.append(dict(path=relative,bytes=len(raw),sha256=sha))
proc.stdin.close();proc.wait();assert proc.returncode==0
(D/'dependencies238.json').write_text(json.dumps(dict(source_commit=commit,retained_glbs=deps),indent=2)+'\n',encoding='utf8',newline='\n')
for f in D.rglob('*'):
    if f.is_file() and f.suffix in ['.json','.js','.cjs','.py','.html','.txt','.md']:f.write_bytes(f.read_text(encoding='utf-8-sig').replace('\r\n','\n').replace('\r','\n').encode())
files=[dict(path=f.relative_to(D).as_posix(),bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in sorted(D.rglob('*')) if f.is_file() and f.name!='manifest238.json']
(D/'manifest238.json').write_text(json.dumps(dict(revision=238,files=files,total_bytes=sum(x['bytes'] for x in files)),indent=2)+'\n',encoding='utf8',newline='\n')
print('SEALED238',len(files),'files,',len(deps),'exact retained inputs,',sum(x['bytes'] for x in files),'bytes')
