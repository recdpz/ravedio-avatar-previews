from pathlib import Path
import json,shutil,struct,hashlib,subprocess,datetime,io
from PIL import Image,ImageDraw
P=Path(__file__).parent;R=P.parent/'floating138/mobile-preview';D=R/'244'
fits=json.loads((P/'fits244.json').read_text());proof=json.loads((P/'proof244.json').read_text());hair=json.loads((P/'hair244.json').read_text());fixtures=json.loads((P/'fixtures244.json').read_text())
joins={build:{top:dict(closed_surface=item['closed_surface'],upper_hood_exact_above=item['upper_hood_exact_above'],free_drape_exact243_after_t=item['free_drape_exact243_after_t'],protected_neighbors_exact=item['protected_neighbors_exact'],moved_vertices=item['moved_vertices']) for top,item in tops.items()} for build,tops in fits.items()}
assert all(j['closed_surface'] and j['upper_hood_exact_above']==1.49 and j['free_drape_exact243_after_t']==.27 and j['protected_neighbors_exact'] for tops in joins.values() for j in tops.values())
(D/'joins244.json').write_text(json.dumps(joins,indent=2)+'\n',encoding='utf8',newline='\n')
assert sum(len(t) for t in fits.values())==14 and len(proof)==14 and len(hair)==16 and len(fixtures)==2
assert all(x.get('final_glbs_reopened') and len(x.get('angles',[]))==4 for x in hair.values())
assert all(x['final_glbs_reopened'] and len(x['angles'])==7 and x['protected_exact'] for x in proof.values())
for build in fixtures:
    src=Path(fixtures[build]['source']);shutil.copy2(src,D/'assemblies'/f'{build}-pashmina244.blend')
    item=fixtures[build];assert item['packed'];assert all(x['packed'] for x in item['body_reference']['images'])
    assert item['portrait_settings']['120']['camera']['matrix_world']==item['portrait_settings']['512']['camera']['matrix_world']
for f in (P/'fixtures').glob('*.png'):shutil.copy2(f,D/'references'/f.name)
for f in (P/'review2').glob('*.png'):shutil.copy2(f,D/'references'/f.name)
# Small references are resampled from the exact128px render, never different
# geometry, tone, camera or lighting. They are visual evidence, not a phone test.
for f in (P/'review2').glob('*-skin*-portrait244-front.png'):
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
review=dict(revision=244,reviewer='self',owner_approval='pending',scope='Remove inherited wavy neck tabs while retaining243 higher knot and outward drape',changes=['The lower hood, neck return and early end roots gather into one narrower continuous neck fold.','Outward shoulder tabs are removed from the actual cloth silhouette; no additional covering panel is added.','The243 knot and outward falling lengths after t0.27 remain exact, as do the fringe and all non-headgear components.'],protected='Upper hood above1.49,243 free drape after t0.27, body/face/hair/wardrobe/materials/studio and shared coordinates.',passes=['14 source construction reviews.','14 fresh GLB fits at seven angles;16 covered hairstyles at four angles; two packed/reopened scenes and matched243 comparisons.','Browser selectors,22 routes/color/comparison checks, six close assemblies at six angles and live delivery checks.'],visual_findings=['Owner identified an inherited wave/tab on each outer neck edge. A colored topology inspection isolated the lower hood, return and early end-root transition.','The corrective field is confined to that lower neck transition; higher crossing and outer-chest fall remain the243 design.'],native_qualification='Separate and not performed here.')
handoff=dict(revision=244,url='https://recdpz.github.io/ravedio-avatar-previews/244/',status='Owner-review clean neck transition',baseline_commit='8df4ee2d3e1fff42c8cb264e7cf3d939aa92f6ea',scope=review['scope'],changes=review['changes'],protected=review['protected'],coordinates='Shared coordinates unchanged; native Blender Z-up to glTF Y-up conversion only. No independent component recentering/resizing.',selection='Independent controls retained. pashminaTops[build][top] selects the authored fit; Compare243 swaps only headgear with the same outfit and view.',assemblies={b:'assemblies/'+b+'-pashmina244.blend' for b in fixtures},reference_framing='120 and512 portraits share camera transform and orthographic scale; exact studio/camera/color settings in fixtures244.json.',materials='Retained woven texture, opaque cloth and0.12 sheen mapping. Ordinary uncompressed GLBs; no new transparency or refraction.',portable_sources='Two packed scenes include their imported components. clean244.py starts from243 per-top authoring scenes and uses retained235/224 helper libraries.',qualification='No native parity, depth-composition or phone-performance claim. No profile-byte or product-repository changes.',technical='technical244.json',fixtures='fixtures244.json',review='review244.json',approval='approval239.json')
for name,obj in [('technical244.json',technical),('review244.json',review),('handoff244.json',handoff),('fixtures244.json',fixtures),('fit-proof244.json',proof),('hair-fits244.json',hair),('drape-paths244.json',fits)]:
 (D/name).write_text(json.dumps(obj,indent=2)+'\n',encoding='utf8',newline='\n')
previous=json.loads((R/'239/manifest239.json').read_text())
approved=dict(revision=239,frozen_commit='f860bb0abc5c1367adbe15fffcd47528f3a8432c',owner_statement='perfect and maybe we can make the both ends less wide to showcase our user\'s shirts/tops more',scope='Owner acceptance of239 pashmina design direction and repaired inner neck joins in the review. Frozen file list is traceability, not separate owner sign-off of every outfit or native renderer.244 changes only the lower crossing widths.',frozen_reference_files=[i for i in previous['files'] if i['path'].startswith('components/')],other_catalogue_approval='Not implied by this scoped approval')
approved.update(scope='Historical239 hood and join acceptance only.244 corrects inherited wavy neck tabs, retaining243 higher knot and outward drape. Owner review of the correction is pending.',owner_clarification='Remove the wavy extra fabric protruding from both outer neck edges; a rectangular scarf should have a coherent continuous edge there.')
(D/'approval239.json').write_text(json.dumps(approved,indent=2)+'\n',encoding='utf8',newline='\n')
for name in ['clean244.py','verify244.py','package244.py','finish244.py','browser244.cjs','close244.cjs']:
 shutil.copy2(P/name,D/'source'/name)
(D/'README244.txt').write_text('Ravedio244: clean continuous pashmina neck fold\n\nRemoves the inherited wavy outward tabs beside the neck. The lower hood, neck return and early end roots gather into one continuous fold. No added cover-up panel. Retains243 higher knot, outward drape and broad ends. Shared coordinates, upper hood, all other models, materials and studio are protected.\n\n14 authored top fits have source and fresh seven-angle GLB reviews;16 retained covered hairstyles have four-angle checks. Two packed/reopened scenes, matched243 comparison and separate feature/color controls are included. Owner review is pending; native/phone qualification remains separate.\n',encoding='utf8',newline='\n')
print('FINISHED244',len(technical),'ordinary GLBs;14 top fits;2 packed scenes')
