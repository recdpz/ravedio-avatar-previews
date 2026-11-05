from pathlib import Path
import json,shutil,struct,hashlib,subprocess,datetime,io
from PIL import Image,ImageDraw
P=Path(__file__).parent;R=P.parent/'floating138/mobile-preview';D=R/'247'
fits=json.loads((P/'fits247.json').read_text());proof=json.loads((P/'proof247.json').read_text());hair=json.loads((P/'hair247.json').read_text());fixtures=json.loads((P/'fixtures247.json').read_text())
joins={build:{top:{k:item[k] for k in ['closed_surface','protected_neighbors_exact','approved_strips_exact246_from_row34','upper_hood_and_neck_wrap_exact246','free_ends_and_fringe_exact246','changed_rows','root_metrics','thickness','local_hood_join_vertices','hem_rings']} for top,item in tops.items()} for build,tops in fits.items()}
assert all(j['closed_surface'] and j['approved_strips_exact246_from_row34'] and j['upper_hood_and_neck_wrap_exact246'] and j['free_ends_and_fringe_exact246'] and j['protected_neighbors_exact'] for tops in joins.values() for j in tops.values())
(D/'joins247.json').write_text(json.dumps(joins,indent=2)+'\n',encoding='utf8',newline='\n')
assert sum(len(t) for t in fits.values())==14 and len(proof)==14 and len(hair)==16 and len(fixtures)==2
assert all(x.get('final_glbs_reopened') and len(x.get('angles',[]))==4 for x in hair.values())
assert all(x['final_glbs_reopened'] and len(x['angles'])==7 and x['protected_exact'] for x in proof.values())
for build in fixtures:
    src=Path(fixtures[build]['source']);shutil.copy2(src,D/'assemblies'/f'{build}-pashmina247.blend')
    item=fixtures[build];assert item['packed'];assert all(x['packed'] for x in item['body_reference']['images'])
    assert item['portrait_settings']['120']['camera']['matrix_world']==item['portrait_settings']['512']['camera']['matrix_world']
for f in (P/'fixtures').glob('*.png'):shutil.copy2(f,D/'references'/f.name)
for f in (P/'review2').glob('*.png'):shutil.copy2(f,D/'references'/f.name)
# Small references are resampled from the exact128px render, never different
# geometry, tone, camera or lighting. They are visual evidence, not a phone test.
for f in (P/'review2').glob('*-skin*-portrait247-front.png'):
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
review=dict(revision=247,reviewer='self',owner_approval='pending for new upper joins;246 main strips accepted',scope='Clean the short upper joins beneath the chin into the accepted246 crossing',changes=['Straighten inherited hooked root sections and blend the shared hood seam locally.','Bridge smoothly into the exact246 main strips with coherent thickness and tangent-aligned edging.','Clean the woven border mapping through the visible upper joins.'],protected='246 main strips from row34, all lower lengths/fringe, upper hood and neck wrap; all other objects/materials/studio and shared coordinates.',passes=['14 source construction reviews.','14 fresh GLB fits at seven angles;16 retained covered hairstyles at four angles; two packed/reopened scenes and matched246 comparisons.','Browser route/color/comparison checks and close six-angle review.'],visual_findings=['246 main crossing was accepted. Remaining roughness was localized to the short roots and edging above it.','Private close-up drafts were iterated to address root kinks, border mapping and shared-seam continuity before full export.'],native_qualification='Separate and not performed here.')
handoff=dict(revision=247,url='https://recdpz.github.io/ravedio-avatar-previews/247/',status='Owner-review upper neck joins',baseline_commit='41069f9a47c9c906e2025953434d074739c72a71',scope=review['scope'],changes=review['changes'],protected=review['protected'],coordinates='Shared coordinates unchanged; Blender Z-up to glTF Y-up only. No independent recentering/resizing.',selection='Independent feature/color controls retained. pashminaTops[build][top] selects authored fit. Compare246 changes only headgear for the same outfit and camera.',assemblies={b:'assemblies/'+b+'-pashmina247.blend' for b in fixtures},reference_framing='120 and512 portraits share camera transform and orthographic scale; exact camera/studio settings in fixtures247.json.',materials='Retained woven texture, opaque cloth and0.12 sheen mapping. Ordinary uncompressed GLBs.',portable_sources='Two packed assembly scenes; roots247.py starts from preserved246 per-top sources with235/224 helpers.',qualification='No native/depth-composition/phone-performance qualification; no profile-byte or product-repository changes.',technical='technical247.json',fixtures='fixtures247.json',review='review247.json',placement_approval='approval244.json',main_strips_approval='approval246.json')
for name,obj in [('technical247.json',technical),('review247.json',review),('handoff247.json',handoff),('fixtures247.json',fixtures),('fit-proof247.json',proof),('hair-fits247.json',hair),('drape-paths247.json',fits)]:
 (D/name).write_text(json.dumps(obj,indent=2)+'\n',encoding='utf8',newline='\n')
shutil.copy2(R/'246/approval239.json',D/'approval239.json')
shutil.copy2(R/'246/approval244.json',D/'approval244.json')
approval=dict(revision=246,commit='41069f9a47c9c906e2025953434d074739c72a71',owner_statement='very nicely done, but also clean up the upper most crossing areas even higher than the ones you fixed',scope='Accepted246 main strips and placement. Short upper joins remain requested work; this is not whole-catalogue or native qualification.',recorded_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
(D/'approval246.json').write_text(json.dumps(approval,indent=2)+'\n',encoding='utf8',newline='\n')
for name in ['roots247.py','verify247.py','close-export247.py','package247.py','finish247.py','browser247.cjs','close247.cjs']:
 shutil.copy2(P/name,D/'source'/name)
(D/'README247.txt').write_text('Ravedio247: upper pashmina joins\n\nCleans the short upper joins beneath the chin into the accepted246 crossing. Straightened sewn roots, local shared-seam relaxation, coherent thickness and aligned edging improve the transition without changing the main strips from row34, placement or lower lengths/fringe. All other objects/materials/studio and shared coordinates retained.\n\nIncludes14 authored top fits, fresh seven-angle GLB reviews,16 covered hairstyles at four angles, two packed/reopened scenes and matched246 comparison. New upper joins await owner review. Native/phone qualification remains separate.\n',encoding='utf8',newline='\n')
print('FINISHED247',len(technical),'ordinary GLBs;14 top fits;2 packed scenes')
