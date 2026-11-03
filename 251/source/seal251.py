from pathlib import Path
import json,hashlib,ast,shutil,datetime
P=Path(__file__).parent;D=P.parent/'floating138/mobile-preview/251';local=json.loads((P/'browser251.json').read_text());target=json.loads((P/'opaque-browser251.json').read_text());crown=json.loads((P/'pole-browser251.json').read_text());assert len(local['checks'])==162 and len(target['checks'])==16
for q in [local,target,crown]:assert not q['errors'] and not q['http']
# Refresh the technical material classification after the last export-only fix.
technical=json.loads((D/'technical251.json').read_text())
import struct
for r in technical:
 f=D/r['path'];raw=f.read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);r.update(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),alpha_modes=sorted({m.get('alphaMode','OPAQUE') for m in g.get('materials',[])}))
(D/'technical251.json').write_text(json.dumps(technical,indent=2)+'\n')
for n in ['browser251.json','opaque-browser251.json','pole-browser251.json','opacity251.json','grain-tint251.json']:
 shutil.copy2(P/n,D/n)
for f in P.glob('*.py'):
 ast.parse(f.read_text(encoding='utf-8-sig'));shutil.copy2(f,D/'source'/f.name)
for f in P.glob('*.cjs'):shutil.copy2(f,D/'source'/f.name)
for f in (P/'browser').glob('*review*251.jpg'):shutil.copy2(f,D/'references'/('browser-'+f.name))
review=json.loads((D/'review251.json').read_text());review.update(local_browser_feature_checks=162,targeted_solid_curl_assemblies=16,fresh_crown_angles=4,export_cases=114,authored_headwear_pairs=85,export_corrections=['Explicit neutral grain texture PBR tint','Fully opaque curl masses marked OPAQUE instead of unnecessary BLEND; geometry and alpha buffers unchanged','Beanie clearance and concealed Afro apex seated'],verification_notes='A premature local page load occurred before a comparison image was packaged. The clean162-check run passed after packaging; later curl material classification received a separate fresh16-assembly/four-angle browser review.');(D/'review251.json').write_text(json.dumps(review,indent=2)+'\n')
hand=json.loads((D/'handoff251.json').read_text());hand['export_materials']='Solid curly-top and Afro masses have all vertex/material alpha1 and are explicitly OPAQUE, avoiding unnecessary transparency sorting. Their clipped side fades remain BLEND. The neutral clipped-grain texture has an explicit brown PBR factor; Blender MixRGB constants are not inferred by native renderers.';(D/'handoff251.json').write_text(json.dumps(hand,indent=2)+'\n')
for f in D.rglob('*'):
 if f.is_file() and f.suffix in ['.json','.txt','.js','.html','.py','.cjs']:f.write_text(f.read_text(encoding='utf-8-sig').replace('\r\n','\n'),encoding='utf8',newline='\n')
files=[dict(path=f.relative_to(D).as_posix(),bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in sorted(D.rglob('*')) if f.is_file() and f.name!='manifest251.json'];(D/'manifest251.json').write_text(json.dumps(dict(revision=251,baseline_commit='b45d0d5f5ab18fa457f26b6477f2a0e20d73c321',files=files),indent=2)+'\n',encoding='utf8',newline='\n')
q=json.loads((P/'progress251.json').read_text());q.update(status='Final251 assets and rendering handoff verified; publication remaining',headwear_pairs=85,export_cases=114,local_browser_checks=162,targeted_curl_assemblies=16,matched_color_depth_pairs=4,retained_input_glbs=398,packed_assemblies=2,native_phone_qualified=False);(P/'progress251.json').write_text(json.dumps(q,indent=2)+'\n');print('SEALED251',len(files),'files',sum(f['bytes'] for f in files),'bytes')
