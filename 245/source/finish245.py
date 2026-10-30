from pathlib import Path
import json,shutil,struct,hashlib,subprocess,datetime,io
from PIL import Image,ImageDraw
P=Path(__file__).parent;R=P.parent/'floating138/mobile-preview';D=R/'245'
fits=json.loads((P/'fits245.json').read_text());proof=json.loads((P/'proof245.json').read_text());hair=json.loads((P/'hair245.json').read_text());fixtures=json.loads((P/'fixtures245.json').read_text())
joins={build:{top:dict(closed_surface=item['closed_surface'],hood_and_neck_exact244=item['hood_and_neck_exact244'],free_ends_and_fringe_exact244=item['free_ends_and_fringe_exact244'],protected_neighbors_exact=item['protected_neighbors_exact'],changed_region=item['changed_region']) for top,item in tops.items()} for build,tops in fits.items()}
assert all(j['closed_surface'] and j['hood_and_neck_exact244'] and j['free_ends_and_fringe_exact244'] and j['protected_neighbors_exact'] for tops in joins.values() for j in tops.values())
(D/'joins245.json').write_text(json.dumps(joins,indent=2)+'\n',encoding='utf8',newline='\n')
assert sum(len(t) for t in fits.values())==14 and len(proof)==14 and len(hair)==16 and len(fixtures)==2
assert all(x.get('final_glbs_reopened') and len(x.get('angles',[]))==4 for x in hair.values())
assert all(x['final_glbs_reopened'] and len(x['angles'])==7 and x['protected_exact'] for x in proof.values())
for build in fixtures:
    src=Path(fixtures[build]['source']);shutil.copy2(src,D/'assemblies'/f'{build}-pashmina245.blend')
    item=fixtures[build];assert item['packed'];assert all(x['packed'] for x in item['body_reference']['images'])
    assert item['portrait_settings']['120']['camera']['matrix_world']==item['portrait_settings']['512']['camera']['matrix_world']
for f in (P/'fixtures').glob('*.png'):shutil.copy2(f,D/'references'/f.name)
for f in (P/'review2').glob('*.png'):shutil.copy2(f,D/'references'/f.name)
# Small references are resampled from the exact128px render, never different
# geometry, tone, camera or lighting. They are visual evidence, not a phone test.
for f in (P/'review2').glob('*-skin*-portrait245-front.png'):
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
review=dict(revision=245,reviewer='self',owner_approval='pending',scope='Simple overlapping pashmina ends at the accepted244 high placement; remove knot-like tuck',changes=['Remove the central reversing tucked path, pinch and raised gather.','The two lengths cross once, with a small thickness clearance establishing over/under order.','Keep244 clean hood/neck transition, outward free drape, tips and fringe exact.'],protected='All244 cloth outside t0.185..0.615 of the crossed lengths; all other objects, materials, shared coordinates and studio.',passes=['14 source construction reviews.','14 fresh GLB fits at seven angles;16 covered hairstyles at four angles; two packed/reopened scenes and matched244 comparisons.','Browser selectors, outfit/color/comparison checks and close six-angle review.'],visual_findings=['Owner accepted244 placement and requested a plain crossing instead of a knot.','Only the middle overlap changes; the accepted height, lower ends and corrected neck edges remain protected.'],native_qualification='Separate and not performed here.')
handoff=dict(revision=245,url='https://recdpz.github.io/ravedio-avatar-previews/245/',status='Owner-review plain crossing at accepted placement',baseline_commit='ffb33aa31b246ce4dec49e9028a621383bd3a54a',scope=review['scope'],changes=review['changes'],protected=review['protected'],coordinates='Shared coordinates unchanged; native Blender Z-up to glTF Y-up conversion only. No independent component recentering/resizing.',selection='Independent controls retained. pashminaTops[build][top] selects the authored fit; Compare244 swaps only headgear with the same outfit and view.',assemblies={b:'assemblies/'+b+'-pashmina245.blend' for b in fixtures},reference_framing='120 and512 portraits share camera transform and orthographic scale; exact studio/camera/color settings in fixtures245.json.',materials='Retained woven texture, opaque cloth and0.12 sheen mapping. Ordinary uncompressed GLBs; no new transparency or refraction.',portable_sources='Two packed scenes include their imported components. cross245.py starts from244 per-top authoring scenes and uses retained235/224 helper libraries.',qualification='No native parity, depth-composition or phone-performance claim. No profile-byte or product-repository changes.',technical='technical245.json',fixtures='fixtures245.json',review='review245.json',approval='approval239.json')
handoff['placement_approval']='approval244.json'
for name,obj in [('technical245.json',technical),('review245.json',review),('handoff245.json',handoff),('fixtures245.json',fixtures),('fit-proof245.json',proof),('hair-fits245.json',hair),('drape-paths245.json',fits)]:
 (D/name).write_text(json.dumps(obj,indent=2)+'\n',encoding='utf8',newline='\n')
previous=json.loads((R/'239/manifest239.json').read_text())
approved=dict(revision=239,frozen_commit='f860bb0abc5c1367adbe15fffcd47528f3a8432c',owner_statement='perfect and maybe we can make the both ends less wide to showcase our user\'s shirts/tops more',scope='Owner acceptance of239 pashmina design direction and repaired inner neck joins in the review. Frozen file list is traceability, not separate owner sign-off of every outfit or native renderer.245 changes only the lower crossing widths.',frozen_reference_files=[i for i in previous['files'] if i['path'].startswith('components/')],other_catalogue_approval='Not implied by this scoped approval')
approved.update(scope='Historical239 design/join acceptance only.245 retains244 placement with a new simple crossing; no whole-catalogue or native approval implied.',owner_clarification='Keep the244 placement but remove the knot and let the two ends simply cross.')
(D/'approval239.json').write_text(json.dumps(approved,indent=2)+'\n',encoding='utf8',newline='\n')
placement=dict(revision=244,frozen_commit='ffb33aa31b246ce4dec49e9028a621383bd3a54a',owner_statement='that is the placement i want but lets not make it a knot anymore and have them just cross while keeping the same placement',scope='Acceptance of244 placement only.245 removes the knot and awaits review; this does not approve the whole catalogue or native rendering.',frozen_files=[i for i in json.loads((R/'244/manifest244.json').read_text())['files'] if i['path'].startswith('components/')])
(D/'approval244.json').write_text(json.dumps(placement,indent=2)+'\n',encoding='utf8',newline='\n')
for name in ['cross245.py','verify245.py','package245.py','finish245.py','browser245.cjs','close245.cjs']:
 shutil.copy2(P/name,D/'source'/name)
(D/'README245.txt').write_text('Ravedio245: plain pashmina crossing at the accepted placement\n\nRemoves the central knot-like tuck, pinch and gather. Two cloth lengths simply overlap at the same high position.244 clean neck edges, outward free drape, broad tips and fringe are retained exactly. Shared coordinates, all other models/materials and studio are protected.\n\n14 authored top fits have source and fresh seven-angle GLB reviews;16 retained covered hairstyles have four-angle checks. Two packed/reopened scenes and matched244 comparison are included. New crossing awaits owner review; native/phone qualification remains separate.\n',encoding='utf8',newline='\n')
print('FINISHED245',len(technical),'ordinary GLBs;14 top fits;2 packed scenes')
