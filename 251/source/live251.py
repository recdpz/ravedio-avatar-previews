from pathlib import Path
import json,urllib.request,hashlib,datetime,concurrent.futures
P=Path(__file__).parent;D=P.parent/'floating138/mobile-preview/251';BASE='https://recdpz.github.io/ravedio-avatar-previews/251/'
manifest=(D/'manifest251.json').read_bytes();m=json.loads(manifest);lookup={x['path']:x for x in m['files']}
paths=['manifest251.json','index.html','viewer251.js','catalogue251.json','handoff251.json','assemblies251.json','technical251.json','depth251.json','references/fits-review251.jpg']+[x for x in lookup if x.startswith(('components/','assemblies/')) or x.endswith('.exr') or '-paired251-color.png' in x]
def verify(name):
 req=urllib.request.Request(BASE+name+'?verify=251final',headers={'Cache-Control':'no-cache','User-Agent':'Ravedio-art-check/251'})
 with urllib.request.urlopen(req,timeout=120) as response:data=response.read()
 sha=hashlib.sha256(data).hexdigest();expected=hashlib.sha256(manifest).hexdigest() if name=='manifest251.json' else lookup[name]['sha256'];assert sha==expected,name
 return dict(path=name,bytes=len(data),sha256=sha)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:files=list(pool.map(verify,paths))
(P/'live251.json').write_text(json.dumps(dict(revision=251,commit=json.loads((P/'progress251.json').read_text())['commit'],verified_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),manifest_matches=True,files=files),indent=2)+'\n',encoding='utf8')
print('LIVE251',len(files),'exact files; every new GLB, both packed scenes and paired color/Z')
