from pathlib import Path
import json,subprocess,hashlib
P=Path(__file__).parent;R=P.parent/'floating138/mobile-preview';D=R/'250'
def git(*args):return subprocess.check_output(['git',*args],cwd=R,text=True).strip()
assert git('branch','--show-current')=='main' and git('rev-parse','HEAD')=='3228f60f6402b0ce0104ce83eb656a975d828ef3';assert not git('diff','--cached','--name-only')
plan=json.loads((P/'plan250.json').read_text());plan.update(status='Implemented; self-reviewed export and browser checks complete; owner review pending',handoff='250/handoff250.json',manifest='250/manifest250.json');f=R/'plans/pashmina-worn-fit250.json';f.write_text(json.dumps(plan,indent=2)+'\n',encoding='utf8');subprocess.run(['git','add','--','250','plans/pashmina-worn-fit250.json'],cwd=R,check=True);subprocess.run(['git','diff','--cached','--check'],cwd=R,check=True)
paths=git('diff','--cached','--name-only').splitlines();m=json.loads((D/'manifest250.json').read_text());assert set(paths)=={'250/'+x['path'] for x in m['files']}|{'250/manifest250.json','plans/pashmina-worn-fit250.json'}
for x in m['files']:
 data=subprocess.check_output(['git','show',':250/'+x['path']],cwd=R);assert hashlib.sha256(data).hexdigest()==x['sha256'],x['path']
subprocess.run(['git','commit','-m','Author covered hair and restrained pashmina drape'],cwd=R,check=True);sha=git('rev-parse','HEAD');q=json.loads((P/'progress250.json').read_text());q.update(commit=sha,status='Committed250; publishing',local_browser_checks=122,manifest_sha256=hashlib.sha256((D/'manifest250.json').read_bytes()).hexdigest());(P/'progress250.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf8');print('COMMITTED250',sha)
