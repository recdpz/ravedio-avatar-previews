from pathlib import Path
import json,hashlib,shutil,ast
from PIL import Image,ImageDraw
P=Path(__file__).parent;D=P.parent/'floating138/mobile-preview/258'
im=Image.new('RGB',(1004,530),'#29394c');draw=ImageDraw.Draw(im)
for i,name in enumerate(['artifact-rightprofile-baseline.png','export-check-rightprofile.png']):
 pic=Image.open(P/name).convert('RGBA');assert pic.size==(502,502);im.paste(pic,(i*502,0),pic);draw.text((i*502+8,510),'257 / white reflection streak' if i==0 else '258 / smooth fade, rounded locks',fill='white')
im.save(D/'references/artifact-comparison258.jpg',quality=95)
index=D/'index.html';s=index.read_text(encoding='utf-8-sig');s=s.replace('<a href="references/taper-comparison258.jpg">','<a href="references/artifact-comparison258.jpg">Flagged reflection before and after</a><a href="references/taper-comparison258.jpg">');index.write_text(s,encoding='utf8',newline='\n')
for name in ['black258.cjs','finalize258.py']:
 shutil.copy2(P/name,D/'source'/name)
shutil.copy2(P/'black258.json',D/'black258.json')
for f in (D/'source').glob('*.py'):ast.parse(f.read_text(encoding='utf-8-sig'))
for f in D.rglob('*'):
 if f.is_file() and f.suffix in ['.json','.txt','.js','.html','.py','.cjs']:f.write_text(f.read_text(encoding='utf-8-sig').replace('\r\n','\n'),encoding='utf8',newline='\n')
for name in ['pass1','pass2','pass3','pass4']:
 folder=P/name;target=folder/'snapshot-manifest.json';assert not target.exists();rows=[dict(path=f.relative_to(folder).as_posix(),bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in sorted(folder.rglob('*')) if f.is_file()];target.write_text(json.dumps(dict(pass_name=name,status='Failed export trial; not published' if name=='pass3' else 'Superseded source pass' if name!='pass4' else 'Final source and fitted exports',files=rows),indent=2)+'\n',encoding='utf8',newline='\n')
files=[dict(path=f.relative_to(D).as_posix(),bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in sorted(D.rglob('*')) if f.is_file() and f.name!='manifest258.json'];assert all(x['bytes']<100_000_000 for x in files);(D/'manifest258.json').write_text(json.dumps(dict(revision=258,baseline_commit='444304044f001b0de9acd46509de3fd2e928c524',files=files),indent=2)+'\n',encoding='utf8',newline='\n')
status=dict(revision=258,status='All source/export checks complete; publication pending',browser_checks=137,black_checks=29,exported_visual_views=312,new_glbs=72,packed_assemblies=3,matched_color_depth_pairs=30,native_phone_qualified=False,remaining=['Commit and publish assets/UI','Verify exact public file hashes and browser controls','Record final receipt'])
for name in ['plan258.json','progress258.json']:
 f=P/name;p=json.loads(f.read_text());p.update(status);f.write_text(json.dumps(p,indent=2)+'\n',encoding='utf8',newline='\n')
print('SEALED258',len(files),'files',sum(x['bytes'] for x in files),'bytes')
