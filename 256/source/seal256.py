from pathlib import Path
import json,hashlib,shutil,ast
P=Path(__file__).parent;R=P.parent/'floating138/mobile-preview';D=R/'256';baseline='511cb1d204bbb74ef1fd61c77e78c2aea3ce452a';b=json.loads((P/'browser256.json').read_text());extra=json.loads((P/'extra-angles256.json').read_text());assert len(b['checks'])==97 and not b['errors'] and not b['http'];assert extra['additionalExportedViews']==60 and not extra['errors'];assert len(list((P/'browser-verified').glob('final-*.png')))==180;assert len(json.loads((D/'depth256.json').read_text())['pairs'])==12
review=json.loads((D/'review256.json').read_text());review.update(exported_visual_views=180,covered_visual_views=112,cloth_hidden_views=4,exact120px_images=8,extra_angle_checks=extra,selected_B_top_attributes_exact=True);(D/'review256.json').write_text(json.dumps(review,indent=2)+'\n',encoding='utf8',newline='\n');shutil.copy2(P/'extra-angles256.json',D/'extra-angles256.json')
shutil.copy2(P/'seal256.py',D/'source/seal256.py')
for f in D.rglob('*'):
 if f.is_file() and f.suffix in ['.json','.txt','.js','.html','.py','.cjs']:f.write_text(f.read_text(encoding='utf-8-sig').replace('\r\n','\n'),encoding='utf8',newline='\n')
files=[dict(path=f.relative_to(D).as_posix(),bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in sorted(D.rglob('*')) if f.is_file() and f.name!='manifest256.json'];assert all(f['bytes']<100_000_000 for f in files);(D/'manifest256.json').write_text(json.dumps(dict(revision=256,baseline_commit=baseline,files=files),indent=2)+'\n',encoding='utf8',newline='\n')
# Keep the recovered snapshot text bytes unchanged. The scoped Git attribute disables conversion.
D255=R/'255'
for key in ['A','B','C','D']:
 folder=D255/'drafts'/key;manifest=json.loads((folder/'snapshot-manifest.json').read_text(encoding='utf-8-sig'))
 for row in manifest['files']:
  data=(folder/row['path']).read_bytes();assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'],(key,row['path'])
for f in D255.iterdir():
 if f.is_file() and f.suffix in ['.json','.txt','.js','.html']:f.write_text(f.read_text(encoding='utf-8-sig').replace('\r\n','\n'),encoding='utf8',newline='\n')
files255=[dict(path=f.relative_to(D255).as_posix(),bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in sorted(D255.rglob('*')) if f.is_file() and f.name!='manifest255.json'];(D255/'manifest255.json').write_text(json.dumps(dict(revision=255,baseline_commit=baseline,files=files255),indent=2)+'\n',encoding='utf8',newline='\n')
# Each authored/export pass is frozen independently of the public package.
for name in ['pass1','pass2']:
 folder=P/name;target=folder/'snapshot-manifest.json';assert not target.exists();rows=[dict(path=f.relative_to(folder).as_posix(),bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in sorted(folder.rglob('*')) if f.is_file()];target.write_text(json.dumps(dict(pass_name=name,files=rows),indent=2)+'\n',encoding='utf8')
p=json.loads((P/'progress256.json').read_text());p.update(status='Selected B higher fade verified; publication remaining',browser_checks=97,exported_visual_views=180,new_glbs=50,packed_assemblies=2,matched_color_depth_pairs=12,native_phone_qualified=False);(P/'progress256.json').write_text(json.dumps(p,indent=2)+'\n',encoding='utf8');print('SEALED255',len(files255),'files;',sum(x['bytes'] for x in files255),'bytes');print('SEALED256',len(files),'files;',sum(x['bytes'] for x in files),'bytes')
