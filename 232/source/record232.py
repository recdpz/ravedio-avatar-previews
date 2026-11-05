from pathlib import Path
import json,hashlib,shutil,datetime
P=Path(__file__).parent;D=P.parent/'floating138/mobile-preview/232'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
src=read(P/'output/eyes232.json');proof=read(P/'output/export-proof232.json');retained=read(P/'output/retained232.json');browser=read(P/'browser232.json');previous=read(P.parent/'refinement231/output/eyes231.json')
assert len(src)==len(proof)==8 and not browser['errors'] and not browser['http']
for key,r in src.items():
 assert sha(Path(r['source']))==r['source_sha256']==proof[key]['source_sha256']
 assert sha(Path(r['glb']))==r['glb_sha256']==proof[key]['glb_sha256']==sha(D/'components'/f"{r['build']}-eyes-{r['shape']}.glb")
 if r['shape']!='squint':assert r['materials_unchanged_from_baseline']==previous[key]['materials_unchanged_from_baseline']
cat=read(D/'catalogue232.json')
for build in ['Feminine','Masculine']:
 assert set(cat['builds'][build]['eyes'])=={'original','almond','tapered','hooded','bean','squint'}
handoff={'revision':232,'status':'Owner-liked three shapes retained; small-size refinement and fuller Curved squint pending review','retained_reference':224,'owner_direction':['Owner likes Tapered oval, Soft hooded and Rounded bean; keep them','Refine small-size appearance where justified','Remove Round and Soft square from current options','Curved squint undecided; improve shape, even if less squinted'],'implemented':['Liked eye surfaces exact231; highlights smaller and seated farther inside','Curved squint has fuller rounded upper arch, more middle area and shallower lower bend','Original and Almond retained; Round and Soft square removed from current selectors','Independent feature controls, quick comparison buttons and matched references for both builds','Historical228 squint comparison retained beneath current references'],'source':src,'export_proof':proof,'retained_surfaces':retained,'browser':browser,'protected':['All non-eye geometry exact224 source','Selected three eye surfaces exact231','Eye anchor positions and existing material settings','Skin palette, fixed lighting, bodies, face, wardrobe, hair/cap and floating arms'],'visual_review':{'construction':'First squint draft still read as a thin chevron. Filled lower middle further and rounded upper arch. The three owner-liked silhouettes were retained exactly.','final':'Final exported front, three-quarter, both profiles, top and underside reviewed; four tones at128 and derived32/48/64 sizes for eight components. Browser appearance and quick controls reviewed separately.','limits':'At32px subtle outline differences remain limited by resolution; no claim of unique recognition for every type at that size. Refined highlights protect the dark silhouette. Curved squint remains a choice for owner review. Native-phone qualification and other catalogue holds remain separate.'},'url':'https://recdpz.github.io/ravedio-avatar-previews/232/','no_profile_wire_change':True}
(D/'handoff232.json').write_text(json.dumps(handoff,indent=2)+'\n',encoding='utf8')
(D/'README232.txt').write_text('Ravedio232 — retained eye choices and a fuller Curved squint\n\nTapered oval, Soft hooded and Rounded bean retain their231 eye surfaces exactly. Highlights are slightly smaller and moved inward. Curved squint is fuller and less closed, with an older228 comparison below the current references. Original and Almond remain; Round and Soft square are removed from current selectors.\n\nUse quick eye buttons or Eye shape. Rotate, zoom and change builds/skin/outfits independently. This is artwork review, with no profile-byte assignment.\n\nSource scenes: E:/Ravedio-Avatar/refinement232/output/sources/. See handoff232.json for hashes, retained-surface assertions and browser verification. Scripts require retained224 sources and helpers.\n',encoding='utf8')
for name in ['eyes232.py','catalogue232.py','controls232.js','package232.py','sheets232.py','verify232.py','browser232.cjs','record232.py']:shutil.copy2(P/name,D/'source'/name)
for f in (P/'output').glob('*.jpg'):shutil.copy2(f,D/'references'/f.name)
for f in D.rglob('*'):
 if f.is_file() and f.suffix in {'.py','.js','.cjs','.html','.json','.txt'}:f.write_bytes((f.read_text(encoding='utf8').replace('\r\n','\n').rstrip('\n')+'\n').encode('utf8'))
manifest={f.relative_to(D).as_posix():{'sha256':sha(f),'bytes':f.stat().st_size} for f in D.rglob('*') if f.is_file() and f.name!='manifest232.json'}
(D/'manifest232.json').write_bytes((json.dumps(manifest,indent=2)+'\n').encode())
state={'revision':232,'status':handoff['status'],'url':handoff['url'],'source':str(P),'handoff':str(D/'handoff232.json'),'owner_approval':{'231_directions':'Owner likes tapered, hooded and bean','232_refinements':'Pending','curved_squint':'Undecided'},'updated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
for p in [P/'progress232.json',Path('C:/Users/Ronnie/Downloads/Ravedio-Avatar-Hairstyles-2026-09-28/production/current/catalogue232.json')]:p.write_text(json.dumps(state,indent=2)+'\n',encoding='utf8')
print('232 manifest:',len(manifest),'files;8 components and three retained surfaces verified')
