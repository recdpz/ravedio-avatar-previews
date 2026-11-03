from pathlib import Path
import json,urllib.request
P=Path(__file__).parent;wanted=json.loads((P/'progress250.json').read_text())['commit']
req=urllib.request.Request('https://api.github.com/repos/recdpz/ravedio-avatar-previews/actions/runs?per_page=8',headers={'User-Agent':'Ravedio-art-check/250','Accept':'application/vnd.github+json'})
with urllib.request.urlopen(req,timeout=30) as response:runs=json.load(response)['workflow_runs']
result=[dict(id=r['id'],sha=r['head_sha'],status=r['status'],conclusion=r['conclusion'],url=r['html_url']) for r in runs if r['head_sha']==wanted]
(P/'deployment250.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8');print(json.dumps(result))
