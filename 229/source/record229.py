from pathlib import Path
import json,hashlib,shutil,struct,datetime
P=Path(__file__).parent;D=P.parent/'floating138/mobile-preview/229'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
src=read(P/'output/eyes229.json');proof=read(P/'output/export-proof229.json');outline=read(P/'output/outline-proof229.json');browser=read(P/'final-browser229.json')
assert not browser['errors'] and not browser['http']
for b,r in src.items():
 assert sha(Path(r['source']))==r['source_sha256']==proof[b]['source_sha256']
 assert sha(Path(r['glb']))==r['glb_sha256']==proof[b]['glb_sha256']==sha(D/'components'/f'{b}-eyes-squint.glb')
 raw=Path(r['glb']).read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n])
 assert all('COLOR_0' in p['attributes'] for m in g['meshes'] for p in m['primitives'])
 assert all(m.get('alphaMode','OPAQUE')=='OPAQUE' for m in g['materials'])
 assert not any('KHR_draco_mesh_compression' in p.get('extensions',{}) for m in g['meshes'] for p in m['primitives'])
handoff={'revision':229,'status':'Glossy charcoal curved-squint candidate; owner acceptance pending','source_reference':228,'implemented':['Same228 frontal outline and eye spacing','Gentle rounded surface; lighter deep-charcoal lower region','One broad soft tonal reflection replaces tiny highlight dots','Opaque vertex colors preserve authored tonal treatment in ordinaryGLB; physical specular responds to light','Direct before228 eye selector; original four eye types and independent controls retained'],'protected':['All non-eye geometry exact224 source','Selected ponytail/cap, face placement, bodies, wardrobe, skin palette, lighting','No other eye style edited; no profile-byte assignment'],'source':src,'exports':proof,'outline':outline,'browser':browser,'visual_review':{'pass1':'First reflection too narrow and lower region too dark; broadened reflection, lifted charcoal, slightly reduced dome depth.','pass2':'Final exported front, three-quarter, both profiles, top/underside/rear and four-tone32/48/64/128 portraits reviewed. Final browser output reviewed separately. Eyes read as a soft squint; no sclera or realistic pupils.','limits':'Other catalogue artistic holds remain; no native/phone qualification. Web and Blender lighting are not identical.'},'url':'https://recdpz.github.io/ravedio-avatar-previews/229/'}
(D/'handoff229.json').write_text(json.dumps(handoff,indent=2)+'\n',encoding='utf8')
(D/'README229.txt').write_text('Ravedio229 — glossy charcoal Curved squint\n\nUse Eye shape to compare Curved squint glossy with before228 on the same avatar. Original four eye types remain unchanged. Shape and spacing are identical to228; depth, tonal shading and reflection are revised. Ordinary GLBs use opaque vertex colors plus a physical glossy material, without separate dots, sclera or pupils.\n\nAuthoring sources: E:/Ravedio-Avatar/refinement229/output/sources/. See handoff229.json for hashes, export and browser checks. Scripts require retained224 sources and helpers. Artwork remains a review candidate.\n',encoding='utf8')
for name in ['eyes229.py','catalogue229.py','controls229.js','package229.py','verify-eyes229.py','outline-proof229.py','sheets229.py','final-browser229.cjs','record229.py']:shutil.copy2(P/name,D/'source'/name)
for name in ['angles-0.jpg','angles-1.jpg','small229.jpg']:shutil.copy2(P/'output'/name,D/'references'/name)
for f in D.rglob('*'):
 if f.is_file() and f.suffix in {'.py','.js','.cjs','.html','.json','.txt'}:
  raw=f.read_bytes()
  try:s=raw.decode('utf8')
  except UnicodeDecodeError:s=raw.decode('cp1252')
  f.write_bytes((s.replace('\r\n','\n').rstrip('\n')+'\n').encode('utf8'))
manifest={f.relative_to(D).as_posix():{'sha256':sha(f),'bytes':f.stat().st_size} for f in D.rglob('*') if f.is_file() and f.name!='manifest229.json'}
(D/'manifest229.json').write_bytes((json.dumps(manifest,indent=2)+'\n').encode())
state={'revision':229,'status':handoff['status'],'url':handoff['url'],'source':str(P),'handoff':str(D/'handoff229.json'),'owner_approval':'pending','updated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
for p in [P/'progress229.json',Path('C:/Users/Ronnie/Downloads/Ravedio-Avatar-Hairstyles-2026-09-28/production/current/catalogue229.json')]:p.write_text(json.dumps(state,indent=2)+'\n',encoding='utf8')
print('229 checks passed; manifest',len(manifest),'files')
