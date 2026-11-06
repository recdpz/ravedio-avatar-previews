"""Standard-library delivery check. Manifest intentionally excludes itself."""
import hashlib,json
from pathlib import Path
D=Path(__file__).resolve().parent.parent
manifest=json.loads((D/'manifest.json').read_text(encoding='utf8'));bad=[]
for r in manifest['files']:
 path=D/r['path']
 if not path.is_file()or path.stat().st_size!=r['bytes']or hashlib.sha256(path.read_bytes()).hexdigest()!=r['sha256']:bad.append(r['path'])
assert not bad,'Missing or changed files: '+', '.join(bad)
print('PACKAGE264_COMPLETE',len(manifest['files']),'files; all hashes match')
