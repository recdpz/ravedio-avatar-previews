from pathlib import Path
import json,hashlib,shutil,datetime
P=Path(__file__).parent;D=P.parent/'floating138/mobile-preview/233'
read=lambda p:json.loads(p.read_text(encoding='utf8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
src=read(P/'output/eyes233.json');proof=read(P/'output/export-proof233.json');browser=read(P/'browser233.json');old=read(P.parent/'refinement232/output/eyes232.json')
assert len(src)==len(proof)==4 and not browser['errors'] and not browser['http']
for key,r in src.items():
 assert sha(Path(r['source']))==r['source_sha256']==proof[key]['source_sha256']
 assert sha(Path(r['glb']))==r['glb_sha256']==proof[key]['glb_sha256']==sha(D/'components'/f"{r['build']}-eyes-{r['shape']}.glb")
 assert r['materials_unchanged_from_baseline']==old[key]['materials_unchanged_from_baseline']
cat=read(D/'catalogue233.json');oldcat=read(D.parent/'232/catalogue232.json')
for build in ['Feminine','Masculine']:
 assert set(cat['builds'][build]['eyes'])=={'original','almond','tapered','hooded','bean','squint'}
 for key in ['original','almond','hooded','squint']:
  assert (D/cat['builds'][build]['eyes'][key]['path']).resolve()==(D.parent/'232'/oldcat['builds'][build]['eyes'][key]['path']).resolve()
 for key in cat['builds'][build]:
  if key!='eyes':assert cat['builds'][build][key]==oldcat['builds'][build][key]
handoff={'revision':233,'status':'More defined Tapered oval and Rounded bean; owner review pending','source_reference':232,'owner_direction':['Keep chosen shapes and established glossy dark style','Make outer taper more noticeable','Give Bean fuller upper portion and a more distinct broad off-center lower bend'],'implemented':['Tapered oval widened, with a rounded outer taper','Bean upper portion fuller; continuous lower bend moved toward outer third','Current232 eye anchor positions, materials and highlights retained','Original, Almond, Soft hooded and Curved squint reuse their prior assets','Review-only Show previous232 toggle changes affected eye component while holding camera, outfit and features','Flat authored-outline comparison without highlights'],'source':src,'export_proof':proof,'browser':browser,'protected':['All non-eye geometry exact224 sources','Other four eye families reuse exact prior files','Material settings and232 highlights','Eye anchors, palette, fixed lighting, body, wardrobe, hair, cap and floating arms'],'visual_review':{'construction':'First Bean draft had an excessive lower notch. Replaced it with one broad turn toward the outer third. Checked matching flat outlines without highlights.','final':'Reopened/exported front, three-quarter, both profiles, top and underside reviewed on both builds. Four tones at128 and derived32/48/64 reviewed; actual browser render and before/after toggle checked separately.','limits':'Distinctive contour detail is stronger at profile and48/64px views;32px remains resolution-limited. These are candidate refinements, not a new material or separate-pupil direction. No native phone qualification.'},'url':'https://recdpz.github.io/ravedio-avatar-previews/233/','no_profile_wire_change':True}
(D/'handoff233.json').write_text(json.dumps(handoff,indent=2)+'\n',encoding='utf8')
(D/'README233.txt').write_text('Ravedio233 — defined Tapered oval and Rounded bean\n\nSelect either eye shape and toggle Show previous232 to compare in the same view. Turning it on changes only the affected eye component; saved PNG names indicate before232. Other features, camera and colors are retained. Original, Almond, Soft hooded and Curved squint reuse prior assets. Round and Soft square remain removed.\n\nThe established dark materials,232 highlights and eye anchors are retained. New outlines are owner-review candidates with no profile-byte assignment. Matched Blender references and a flat-outline check are below the controls.\n\nSources: E:/Ravedio-Avatar/refinement233/output/sources/. See handoff233.json for hashes and verification. Scripts depend on retained224 inputs and helpers.\n',encoding='utf8')
for name in ['eyes233.py','catalogue233.py','controls233.js','package233.py','sheets233.py','verify233.py','browser233.cjs','record233.py']:shutil.copy2(P/name,D/'source'/name)
for f in (P/'output').glob('*.jpg'):shutil.copy2(f,D/'references'/f.name)
for f in D.rglob('*'):
 if f.is_file() and f.suffix in {'.py','.js','.cjs','.html','.json','.txt','.svg'}:f.write_bytes((f.read_text(encoding='utf8').replace('\r\n','\n').rstrip('\n')+'\n').encode('utf8'))
manifest={f.relative_to(D).as_posix():{'sha256':sha(f),'bytes':f.stat().st_size} for f in D.rglob('*') if f.is_file() and f.name!='manifest233.json'}
(D/'manifest233.json').write_bytes((json.dumps(manifest,indent=2)+'\n').encode())
state={'revision':233,'status':handoff['status'],'url':handoff['url'],'source':str(P),'handoff':str(D/'handoff233.json'),'owner_approval':'233 contours pending; prior directions retained','updated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
for p in [P/'progress233.json',Path('C:/Users/Ronnie/Downloads/Ravedio-Avatar-Hairstyles-2026-09-28/production/current/catalogue233.json')]:p.write_text(json.dumps(state,indent=2)+'\n',encoding='utf8')
print('233:',len(manifest),'manifest files;4 authored exports; four prior eye families reused exactly')
