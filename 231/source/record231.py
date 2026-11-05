from pathlib import Path
import json,hashlib,shutil,datetime
P=Path(__file__).parent;D=P.parent/'floating138/mobile-preview/231'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
src=read(P/'output/eyes231.json');proof=read(P/'output/export-proof231.json');browser=read(P/'browser231.json')
assert len(src)==len(proof)==6 and not browser['errors'] and not browser['http']
for key,r in src.items():
 assert sha(Path(r['source']))==r['source_sha256']==proof[key]['source_sha256']
 assert sha(Path(r['glb']))==r['glb_sha256']==proof[key]['glb_sha256']==sha(D/'components'/f"{r['build']}-eyes-{r['shape']}.glb")
handoff={'revision':231,'status':'Three eye-outline comparisons; owner selection pending','retained_reference':224,'owner_direction':['Keep established glossy dark cartoon eye style','229 charcoal shading and230 separate-pupil direction rejected','Show Tapered oval, Soft hooded and Rounded bean alongside Original before selecting a shape'],'implemented':['Three authored outlines on both builds using unchanged original eye/highlight materials','Independent feature controls and established eye choices retained','Original default; four quick eye comparison buttons preserve outfit, camera and other features','Matched front portraits for both builds; ordinary shared-coordinate GLBs'],'source':src,'export_proof':proof,'browser':browser,'protected':['All non-eye geometry exact224 source','Eye anchor positions','Existing material settings, skin palette and fixed lighting','Current wardrobe, selected ponytail/cap, body, face and floating arms'],'visual_review':{'construction':'Softened tapered outer tip; reduced bean indentation twice to avoid pointed or cut-out appearance. Hooded main highlight seated farther below upper edge.','final':'Final exported front, three-quarter, both profiles, top and underside reviewed for six candidates; four tones at128 and derived32/48/64. Browser controls and final mobile appearance reviewed separately.','artistic_disposition':'All three are comparison candidates. Tapered oval is lively, hooded calm, bean playful. None is owner-approved or assigned to a production profile slot.','limits':'Existing227 artistic holds and native-phone qualification remain separate.'},'url':'https://recdpz.github.io/ravedio-avatar-previews/231/','no_profile_wire_change':True}
(D/'handoff231.json').write_text(json.dumps(handoff,indent=2)+'\n',encoding='utf8')
(D/'README231.txt').write_text('Ravedio231 — eye shape comparisons\n\nOriginal, Tapered oval, Soft hooded, Rounded bean. Use the four buttons under the live model, or Eye shape. Build, skin, outfit, hair and other feature controls remain independent. Rotate and zoom to inspect. Native reference portraits appear beneath the controls.\n\nThe established glossy dark eye materials are retained.229 and230 directions were rejected; those finishes are not used here. Original remains default. Three new shapes are review candidates, with no profile-byte assignment.\n\nSource scenes: E:/Ravedio-Avatar/refinement231/output/sources/. See handoff231.json for export hashes and verification. Scripts require retained224 sources and helpers.\n',encoding='utf8')
for name in ['eyes231.py','catalogue231.py','controls231.js','package231.py','sheets231.py','verify231.py','browser231.cjs','record231.py']:shutil.copy2(P/name,D/'source'/name)
for f in (P/'output').glob('*.jpg'):shutil.copy2(f,D/'references'/f.name)
for f in D.rglob('*'):
 if f.is_file() and f.suffix in {'.py','.js','.cjs','.html','.json','.txt'}:f.write_bytes((f.read_text(encoding='utf8').replace('\r\n','\n').rstrip('\n')+'\n').encode('utf8'))
manifest={f.relative_to(D).as_posix():{'sha256':sha(f),'bytes':f.stat().st_size} for f in D.rglob('*') if f.is_file() and f.name!='manifest231.json'}
(D/'manifest231.json').write_bytes((json.dumps(manifest,indent=2)+'\n').encode())
state={'revision':231,'status':handoff['status'],'url':handoff['url'],'source':str(P),'handoff':str(D/'handoff231.json'),'owner_approval':'pending','updated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
for p in [P/'progress231.json',Path('C:/Users/Ronnie/Downloads/Ravedio-Avatar-Hairstyles-2026-09-28/production/current/catalogue231.json')]:p.write_text(json.dumps(state,indent=2)+'\n',encoding='utf8')
for rev in [229,230]:
 p=P.parent/f'refinement{rev}/progress{rev}.json';s=read(p);s['owner_approval']='rejected; keep established glossy dark eye style';s['superseded_by']=231;p.write_text(json.dumps(s,indent=2)+'\n',encoding='utf8')
print('231 manifest:',len(manifest),'files;6 authored components verified')
