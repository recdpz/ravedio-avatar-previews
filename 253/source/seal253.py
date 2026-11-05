from pathlib import Path
import json,hashlib,shutil,ast
P=Path(__file__).parent;D=P.parent/'floating138/mobile-preview/253';baseline='423249a53ebb5afb2548542d133a99bbe6a7f6db'
q=json.loads((P/'browser253.json').read_text());a=json.loads((P/'angles253.json').read_text());c=json.loads((D/'catalogue253.json').read_text());depth=json.loads((D/'depth253.json').read_text());assert len(q['checks'])==219 and not q['errors'] and not q['http'];assert a['additional_angles']==32 and not a['errors'];assert len(c['ombre'])==128;assert sum(len(x['hair']) for x in c['builds'].values())==16;assert len(depth['pairs'])==12;assert len(list((D/'assemblies').glob('*.blend')))==2
shutil.copy2(P/'angles253.json',D/'angles253.json');shutil.copy2(P/'angles253.cjs',D/'source/angles253.cjs')
review=json.loads((D/'review253.json').read_text());review['additional_rotation_checks']=a;review['passes'].append('Final right-profile and underside visual pass across all16 hairstyles:32 additional exported-model views.');(D/'review253.json').write_text(json.dumps(review,indent=2)+'\n',encoding='utf8',newline='\n')
shutil.copy2(P/'seal253.py',D/'source/seal253.py')
for f in D.rglob('*'):
 if f.is_file() and f.suffix in ['.json','.txt','.js','.html','.py','.cjs']:
  content=f.read_text(encoding='utf-8-sig').replace('\r\n','\n');f.write_text(content,encoding='utf8',newline='\n')
files=[dict(path=f.relative_to(D).as_posix(),bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in sorted(D.rglob('*')) if f.is_file() and f.name!='manifest253.json'];assert all(x['bytes']<100_000_000 for x in files)
(D/'manifest253.json').write_text(json.dumps(dict(revision=253,baseline_commit=baseline,files=files),indent=2)+'\n',encoding='utf8',newline='\n')
p=json.loads((P/'progress253.json').read_text());p.update(status='Final exports and handoff verified; publication remaining',browser_checks=len(q['checks']),extra_angle_views=32,color_variants=128,matched_color_depth_pairs=12,packed_assemblies=2,native_phone_qualified=False);(P/'progress253.json').write_text(json.dumps(p,indent=2)+'\n',encoding='utf8')
print('SEALED253',len(files),'files',sum(f['bytes'] for f in files),'bytes')
