from pathlib import Path
import json,shutil,struct,hashlib,subprocess,datetime,io
from PIL import Image,ImageDraw
P=Path(__file__).parent;R=P.parent/'floating138/mobile-preview';D=R/'243'
fits=json.loads((P/'fits243.json').read_text());proof=json.loads((P/'proof243.json').read_text());hair=json.loads((P/'hair243.json').read_text());fixtures=json.loads((P/'fixtures243.json').read_text())
joins={build:{top:dict(closed_surface=item['closed_surface'],hood_roots_and_underwrap_exact242=item['hood_roots_and_underwrap_exact242'],protected_neighbors_exact=item['protected_neighbors_exact'],end_metrics=item['end_metrics']) for top,item in tops.items()} for build,tops in fits.items()}
assert all(j['closed_surface'] and j['hood_roots_and_underwrap_exact242'] and j['protected_neighbors_exact'] for tops in joins.values() for j in tops.values())
(D/'joins243.json').write_text(json.dumps(joins,indent=2)+'\n',encoding='utf8',newline='\n')
assert sum(len(t) for t in fits.values())==14 and len(proof)==14 and len(hair)==16 and len(fixtures)==2
assert all(x.get('final_glbs_reopened') and len(x.get('angles',[]))==4 for x in hair.values())
assert all(x['final_glbs_reopened'] and len(x['angles'])==7 and x['protected_exact'] for x in proof.values())
for build in fixtures:
    src=Path(fixtures[build]['source']);shutil.copy2(src,D/'assemblies'/f'{build}-pashmina243.blend')
    item=fixtures[build];assert item['packed'];assert all(x['packed'] for x in item['body_reference']['images'])
    assert item['portrait_settings']['120']['camera']['matrix_world']==item['portrait_settings']['512']['camera']['matrix_world']
for f in (P/'fixtures').glob('*.png'):shutil.copy2(f,D/'references'/f.name)
for f in (P/'review2').glob('*.png'):shutil.copy2(f,D/'references'/f.name)
# Small references are resampled from the exact128px render, never different
# geometry, tone, camera or lighting. They are visual evidence, not a phone test.
for f in (P/'review2').glob('*-skin*-portrait243-front.png'):
    im=Image.open(f)
    for size in [32,48,64]:im.resize((size,size),Image.Resampling.LANCZOS).save(D/'references'/(f.stem+'-'+str(size)+'.png'))
technical=[]
for f in sorted((D/'components').glob('*.glb')):
    data=f.read_bytes();length=struct.unpack_from('<I',data,12)[0];g=json.loads(data[20:20+length]);tri=sum(g['accessors'][p['indices']]['count']//3 if 'indices' in p else g['accessors'][p['attributes']['POSITION']]['count']//3 for m in g['meshes'] for p in m['primitives']);ext=g.get('extensionsUsed',[])
    assert not any(x in ext for x in ['KHR_draco_mesh_compression','EXT_meshopt_compression','KHR_mesh_quantization'])
    images=[];binary=data[28+length:]
    for im in g.get('images',[]):
        b=g['bufferViews'][im['bufferView']];raw=binary[b.get('byteOffset',0):b.get('byteOffset',0)+b['byteLength']];pic=Image.open(io.BytesIO(raw));images.append(dict(width=pic.width,height=pic.height,bytes=len(raw)))
    for m in g.get('materials',[]):
        sheen=m.get('extensions',{}).get('KHR_materials_sheen',{}).get('sheenColorFactor')
        if 'Headwear' in m.get('name','') and sheen:assert max(sheen)<=.12001
    technical.append(dict(path='components/'+f.name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),triangles=tri,materials=len(g.get('materials',[])),textures=images,alpha_modes=sorted(set(m.get('alphaMode','OPAQUE') for m in g.get('materials',[]))),extensions=ext))
review=dict(revision=243,reviewer='self',owner_approval='pending',scope='Raise the pashmina crossing to a small loose neck knot and redirect the ends toward the outer chest',changes=['Two existing continuous cloth lengths form the small folded knot high on the torso.','The crossing lengths fan outward before settling on major shoulder/chest forms, revealing the shirt centre.','Broad hanging-end widths are retained; fringe and sewn border follow their actual fabric attachments.'],protected='242 hood, sewn roots and underlying neck wrap are fixed; end paths change as requested. All non-headgear geometry, materials and fixed studio remain unchanged.',passes=['14 source fits with front/three-quarter/profile construction checks.','14 freshly reopened GLB assemblies at seven angles; two packed/reopened default scenes; matched242 views.','16 retained covered hairstyles reviewed at front/three-quarter/profile/rear; browser outfit/comparison/color and close six-angle checks.'],native_qualification='Separate and not performed here.')
review['visual_findings']=['Matched242/243 views visibly raise the crossing and shift both hanging lengths away from the breast centres.','The first two private drafts read as a flat X; the delivered upper cloth path adds a small overhand tucked turn, with a softer fold through the crossing.','Front, both sides, rear and underside checks show the ends seated on major torso forms; no new floating shoulder gap or separated root corner was observed in the reviewed fits.','The knot is deliberately small beneath the oversized head. Owner judgment of its styling and outward flare remains pending.']
handoff=dict(revision=243,url='https://recdpz.github.io/ravedio-avatar-previews/243/',status='Owner-review raised loose-knot drape',baseline_commit='5ce4cbe3005485adfe9ad648909e54b20196ad90',scope=review['scope'],changes=review['changes'],protected=review['protected'],coordinates='Shared coordinates unchanged; native Blender Z-up to glTF Y-up conversion only. No independent component recentering/resizing.',selection='Independent controls retained. pashminaTops[build][top] selects the authored fit; Compare242 swaps only headgear with the same outfit and view.',assemblies={b:'assemblies/'+b+'-pashmina243.blend' for b in fixtures},reference_framing='120 and512 portraits share camera transform and orthographic scale; exact studio/camera/color settings in fixtures243.json.',materials='Retained woven texture, opaque cloth and0.12 sheen mapping. Ordinary uncompressed GLBs; no new transparency or refraction.',portable_sources='Two packed scenes include their imported components. knot243.py starts from242 per-top authoring scenes and uses retained235/224 helper libraries.',qualification='No native parity, depth-composition or phone-performance claim. No profile-byte or product-repository changes.',technical='technical243.json',fixtures='fixtures243.json',review='review243.json',approval='approval239.json')
for name,obj in [('technical243.json',technical),('review243.json',review),('handoff243.json',handoff),('fixtures243.json',fixtures),('fit-proof243.json',proof),('hair-fits243.json',hair),('drape-paths243.json',fits)]:
 (D/name).write_text(json.dumps(obj,indent=2)+'\n',encoding='utf8',newline='\n')
previous=json.loads((R/'239/manifest239.json').read_text())
approved=dict(revision=239,frozen_commit='f860bb0abc5c1367adbe15fffcd47528f3a8432c',owner_statement='perfect and maybe we can make the both ends less wide to showcase our user\'s shirts/tops more',scope='Owner acceptance of239 pashmina design direction and repaired inner neck joins in the review. Frozen file list is traceability, not separate owner sign-off of every outfit or native renderer.243 changes only the lower crossing widths.',frozen_reference_files=[i for i in previous['files'] if i['path'].startswith('components/')],other_catalogue_approval='Not implied by this scoped approval')
approved.update(scope='Historical239 hood and join acceptance only.243 is a new higher loose-knot and outward-end drape requested by the owner; its paths and placement await review.',owner_clarification='Move the crossing higher toward the neck, create a loose knot look, then flare outward before settling instead of descending over the centre of each breast.')
(D/'approval239.json').write_text(json.dumps(approved,indent=2)+'\n',encoding='utf8',newline='\n')
for name in ['knot243.py','verify243.py','package243.py','finish243.py','browser243.cjs','close243.cjs']:
 shutil.copy2(P/name,D/'source'/name)
(D/'README243.txt').write_text('Ravedio243: higher loose neck knot and outward drape\n\nThe two continuous cloth lengths cross higher and form a small folded knot. They fan toward the outer chest before settling onto the torso, keeping the shirt centre visible. End widths are retained; fringe and border follow their attachments. The242 hood, sewn roots, under-wrap and all other models/materials/studio are protected.\n\nAll14 top fits have fresh seven-angle GLB references;16 retained covered hairstyles have fresh four-angle checks. Both default scenes are packed/reopened. Compare242 keeps the selected outfit and camera. Owner review is pending. Native rendering, depth composition and phone performance remain separate.\n',encoding='utf8',newline='\n')
print('FINISHED243',len(technical),'ordinary GLBs;14 top fits;2 packed scenes')
