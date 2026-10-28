from pathlib import Path
import json,hashlib,shutil,struct,datetime
P=Path(__file__).parent;D=P.parent/'floating138/mobile-preview/230'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
src=read(P/'output/eyes230.json');proof=read(P/'output/export-proof230.json');outline=read(P/'output/outline-proof230.json');browser=read(P/'final-browser230.json')
assert not browser['errors'] and not browser['http']
for b,r in src.items():
 assert sha(Path(r['source']))==r['source_sha256']==proof[b]['source_sha256']
 assert sha(Path(r['glb']))==r['glb_sha256']==proof[b]['glb_sha256']==sha(D/'components'/f'{b}-eyes-squint.glb')
 raw=Path(r['glb']).read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n])
 assert any('COLOR_0' in p['attributes'] for m in g['meshes'] for p in m['primitives'])
 assert all(m.get('alphaMode','OPAQUE')=='OPAQUE' for m in g['materials'])
handoff={'revision':230,'status':'Visible-pupil curved-squint candidate; owner acceptance pending','source_reference':228,'owner_feedback':'229 looked worse and still did not read as having a pupil','implemented':['Same228 frontal outline and spacing','Muted grey eye opening with thin dark perimeter','Larger distinct round pupil seated in the surface and clipped by the opening','One small pupil catchlight; reduced surface dome','Opaque vertex colors preserve eye opening/pupil contrast in ordinaryGLB','Direct before228 eye selector; original four eye types and independent controls retained'],'protected':['All non-eye geometry exact224 source','Selected ponytail/cap, face placement, bodies, wardrobe, skin palette, lighting','No other eye style edited; no profile-byte assignment'],'source':src,'exports':proof,'outline':outline,'browser':browser,'visual_review':{'pass1':'First discrete pupil was too small and protruding. Integrated a larger pupil into the eye surface and lowered its center.','pass2':'Final exported front, three-quarter, both profiles, top/underside/rear and four-tone32/48/64/128 portraits reviewed. Final browser output checked separately.','limits':'This is a new visual candidate after229 rejection. Other catalogue artistic holds remain; no native/phone qualification.'},'url':'https://recdpz.github.io/ravedio-avatar-previews/230/'}
(D/'handoff230.json').write_text(json.dumps(handoff,indent=2)+'\n',encoding='utf8')
(D/'README230.txt').write_text('Ravedio230 — visible-pupil Curved squint\n\nUse Eye shape to compare Curved squint pupil with before228 on the same avatar. Original four eye types remain unchanged.230 replaces rejected229 solid charcoal treatment with a muted grey opening, distinct round dark pupil and small catchlight. Shape and spacing are identical to228.\n\nAuthoring sources: E:/Ravedio-Avatar/refinement230/output/sources/. See handoff230.json for hashes, export and browser checks. Scripts require retained224 sources and helpers. Artwork remains a review candidate.\n',encoding='utf8')
for name in ['eyes230.py','catalogue230.py','controls230.js','package230.py','verify-eyes230.py','outline-proof230.py','sheets230.py','final-browser230.cjs','record230.py']:shutil.copy2(P/name,D/'source'/name)
for name in ['angles-0.jpg','angles-1.jpg','small230.jpg']:shutil.copy2(P/'output'/name,D/'references'/name)
for f in D.rglob('*'):
 if f.is_file() and f.suffix in {'.py','.js','.cjs','.html','.json','.txt'}:f.write_bytes((f.read_text(encoding='utf8').replace('\r\n','\n').rstrip('\n')+'\n').encode('utf8'))
manifest={f.relative_to(D).as_posix():{'sha256':sha(f),'bytes':f.stat().st_size} for f in D.rglob('*') if f.is_file() and f.name!='manifest230.json'}
(D/'manifest230.json').write_bytes((json.dumps(manifest,indent=2)+'\n').encode())
state={'revision':230,'status':handoff['status'],'url':handoff['url'],'source':str(P),'handoff':str(D/'handoff230.json'),'owner_approval':'pending','updated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
for p in [P/'progress230.json',Path('C:/Users/Ronnie/Downloads/Ravedio-Avatar-Hairstyles-2026-09-28/production/current/catalogue230.json')]:p.write_text(json.dumps(state,indent=2)+'\n',encoding='utf8')
print('230 checks passed; manifest',len(manifest),'files')
