from pathlib import Path
import json,urllib.request,hashlib,datetime,concurrent.futures
P=Path(__file__).parent;D=P.parent/'floating138/mobile-preview/250';BASE='https://recdpz.github.io/ravedio-avatar-previews/250/'
manifest=(D/'manifest250.json').read_bytes();m=json.loads(manifest);lookup={x['path']:x for x in m['files']}
paths=['manifest250.json','index.html','viewer250.js','catalogue250.json','handoff250.json','assemblies250.json','technical250.json','depth250.json','references/identity-comparison250.jpg']+[x for x in lookup if x.startswith(('components/','assemblies/')) or x.endswith('.exr') or '-paired250-color.png' in x]
def verify(name):
 req=urllib.request.Request(BASE+name+'?verify=250final',headers={'Cache-Control':'no-cache','User-Agent':'Ravedio-art-check/250'})
 with urllib.request.urlopen(req,timeout=120) as response:data=response.read()
 sha=hashlib.sha256(data).hexdigest();expected=hashlib.sha256(manifest).hexdigest() if name=='manifest250.json' else lookup[name]['sha256'];assert sha==expected,name
 return dict(path=name,bytes=len(data),sha256=sha)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:files=list(pool.map(verify,paths))
(P/'live250.json').write_text(json.dumps(dict(revision=250,commit=json.loads((P/'progress250.json').read_text())['commit'],verified_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),manifest_matches=True,files=files),indent=2)+'\n',encoding='utf8')
print('LIVE250',len(files),'exact files; every new GLB, both packed scenes and paired color/Z')
