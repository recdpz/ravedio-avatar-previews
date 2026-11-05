from pathlib import Path
import json,subprocess,hashlib
P=Path(__file__).parent;R=P.parent/'floating138/mobile-preview';D=R/'249';base='9cea4e0637473b9b73e9b9ea1c7fa0c7cdc0559a'
assert subprocess.check_output(['git','branch','--show-current'],cwd=R,text=True).strip()=='main'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()==base
assert not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=R,text=True).strip()
m=json.loads((D/'manifest249.json').read_text());expected={x['path']:x['sha256'] for x in m['files']};expected['manifest249.json']=hashlib.sha256((D/'manifest249.json').read_bytes()).hexdigest()
plan=dict(status='Implemented249 artwork repair; owner review pending',baseline_commit=base,source_artwork='cc3d03d9caf726bc0406338a9a60579dba2b3ab4',revision=249,scope='Rooted hair coverage, original visible hairstyle identity and fitted pashmina volume',handoff='249/handoff249.json',manifest_sha256=expected['manifest249.json'],cloth_top_fits=112,exact_original_hair_components=14,localized_gathered_hair_components=2,headwear_sprout_fits=16,default_hair_reviews=16,wardrobe_accessory_stress_cases=22,source_and_export_review=True,native_phone_qualified=False)
(R/'plans/pashmina-hair-repair249.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf8',newline='\n')
subprocess.run(['git','add','--','249','plans/pashmina-hair-repair249.json'],cwd=R,check=True);subprocess.run(['git','diff','--cached','--check'],cwd=R,check=True)
files=subprocess.check_output(['git','diff','--cached','--name-only'],cwd=R,text=True).splitlines();assert set(files)=={'249/'+p for p in expected}|{'plans/pashmina-hair-repair249.json'}
proc=subprocess.Popen(['git','cat-file','--batch'],cwd=R,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
for name,sha in expected.items():
 proc.stdin.write((':249/'+name+'\n').encode());proc.stdin.flush();h=proc.stdout.readline().split();assert len(h)==3 and h[1]==b'blob',name;raw=proc.stdout.read(int(h[2]));assert proc.stdout.read(1)==b'\n';assert hashlib.sha256(raw).hexdigest()==sha,name
proc.stdin.close();proc.wait();assert proc.returncode==0
print('STAGED249',len(files),'exact indexed bytes checked')
