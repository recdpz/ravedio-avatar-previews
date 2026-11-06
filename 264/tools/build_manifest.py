"""Build hashes after verification. Updating hashes does not confer visual approval."""
import json,hashlib
from pathlib import Path
D=Path(__file__).resolve().parent.parent;rows=[]
for p in sorted(D.rglob('*')):
 if not p.is_file()or p.name=='manifest.json'or'__pycache__'in p.parts or p.suffix in ['.pyc','.blend1','.zip']:continue
 # Keep transfer hashes identical in Windows/Linux Git checkouts. Preserve
 # vendored upstream bytes, including their documented source hashes.
 if p.suffix in ['.json','.js','.cjs','.mjs','.py','.html','.md','.txt'] and 'vendor'not in p.parts:
  p.write_text(p.read_text(encoding='utf8'),encoding='utf8',newline='\n')
 rows.append({'path':p.relative_to(D).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(D/'manifest.json').write_text(json.dumps({'revision':264,'source_revision':263,'source_commit':'dc2d174e5342e6683f727354e4e5711fe2116f3f','files':rows,'total_bytes':sum(x['bytes']for x in rows)},indent=2)+'\n',encoding='utf8',newline='\n');print('MANIFEST264_COMPLETE',len(rows),sum(x['bytes']for x in rows))
