from pathlib import Path
import json,shutil,struct,hashlib,subprocess,datetime,io
from PIL import Image,ImageDraw
P=Path(__file__).parent;R=P.parent/'floating138/mobile-preview';D=R/'246'
fits=json.loads((P/'fits246.json').read_text());proof=json.loads((P/'proof246.json').read_text());hair=json.loads((P/'hair246.json').read_text());fixtures=json.loads((P/'fixtures246.json').read_text())
joins={build:{top:dict(closed_surface=item['closed_surface'],hood_and_neck_exact245=item['hood_and_neck_exact245'],free_ends_and_fringe_exact245=item['free_ends_and_fringe_exact245'],protected_neighbors_exact=item['protected_neighbors_exact'],changed_region=item['changed_region'],ribbon_metrics=item['ribbon_metrics'],thickness=item['thickness']) for top,item in tops.items()} for build,tops in fits.items()}
assert all(j['closed_surface'] and j['hood_and_neck_exact245'] and j['free_ends_and_fringe_exact245'] and j['protected_neighbors_exact'] for tops in joins.values() for j in tops.values())
(D/'joins246.json').write_text(json.dumps(joins,indent=2)+'\n',encoding='utf8',newline='\n')
assert sum(len(t) for t in fits.values())==14 and len(proof)==14 and len(hair)==16 and len(fixtures)==2
assert all(x.get('final_glbs_reopened') and len(x.get('angles',[]))==4 for x in hair.values())
assert all(x['final_glbs_reopened'] and len(x['angles'])==7 and x['protected_exact'] for x in proof.values())
for build in fixtures:
    src=Path(fixtures[build]['source']);shutil.copy2(src,D/'assemblies'/f'{build}-pashmina246.blend')
    item=fixtures[build];assert item['packed'];assert all(x['packed'] for x in item['body_reference']['images'])
    assert item['portrait_settings']['120']['camera']['matrix_world']==item['portrait_settings']['512']['camera']['matrix_world']
for f in (P/'fixtures').glob('*.png'):shutil.copy2(f,D/'references'/f.name)
for f in (P/'review2').glob('*.png'):shutil.copy2(f,D/'references'/f.name)
# Small references are resampled from the exact128px render, never different
# geometry, tone, camera or lighting. They are visual evidence, not a phone test.
for f in (P/'review2').glob('*-skin*-portrait246-front.png'):
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
review=dict(revision=246,reviewer='self',owner_approval='pending',scope='Rebuild distorted high crossing as clean fabric strips at accepted244 placement',changes=['Replace inherited twisted rows with controlled-width ruled strips and smoothly varying frames.','Fit depth against major forms without radially warping the strip edges; keep the upper edge below the chin.','Reorient the inner layer to maintain coherent cloth thickness instead of carrying the knot offsets forward.'],protected='245 hood/neck wrap and all other objects/materials/studio; free ends and fringe after t0.68 remain exact245, retaining accepted244 placement.',passes=['14 source construction reviews.','14 fresh GLB fits at seven angles;16 retained covered hairstyles at four angles; two packed/reopened scenes and matched245 comparisons.','Browser route/color/comparison checks and close six-angle review.'],visual_findings=['Owner rejected245 upper crossing as distorted. The cause was inherited twisted cross-sections plus per-vertex radial fitting that changed their visible width.','246 authors coherent strip edges and surface thickness while retaining the accepted placement.'],native_qualification='Separate and not performed here.')
handoff=dict(revision=246,url='https://recdpz.github.io/ravedio-avatar-previews/246/',status='Owner-review clean upper fabric strips',baseline_commit='f85f7cef1797fa09d666b80dc52099b2ac3a894c',scope=review['scope'],changes=review['changes'],protected=review['protected'],coordinates='Shared coordinates unchanged; Blender Z-up to glTF Y-up only. No independent recentering/resizing.',selection='Independent feature/color controls retained. pashminaTops[build][top] selects authored fit. Compare245 changes only the headgear for the same outfit and camera.',assemblies={b:'assemblies/'+b+'-pashmina246.blend' for b in fixtures},reference_framing='120 and512 portraits share camera transform and orthographic scale; exact camera/studio settings in fixtures246.json.',materials='Retained woven texture, opaque cloth and0.12 sheen mapping. Ordinary uncompressed GLBs.',portable_sources='Two packed assembly scenes; ribbons246.py starts from preserved245 per-top sources with235/224 helpers.',qualification='No native/depth-composition/phone-performance qualification; no profile-byte or product-repository changes.',technical='technical246.json',fixtures='fixtures246.json',review='review246.json',placement_approval='approval244.json')
review['visual_findings'].extend(['The first private rebuild was too wide and bunched against the chin; the delivered version controls the strip width and caps its upper edge below the chin.','Final source, reopened GLB and browser close views show continuous borders through the overlap on both builds; the hanging ends and neck wrap remain fixed.'])
for name,obj in [('technical246.json',technical),('review246.json',review),('handoff246.json',handoff),('fixtures246.json',fixtures),('fit-proof246.json',proof),('hair-fits246.json',hair),('drape-paths246.json',fits)]:
 (D/name).write_text(json.dumps(obj,indent=2)+'\n',encoding='utf8',newline='\n')
shutil.copy2(R/'245/approval239.json',D/'approval239.json')
shutil.copy2(R/'245/approval244.json',D/'approval244.json')
for name in ['ribbons246.py','verify246.py','package246.py','finish246.py','browser246.cjs','close246.cjs']:
 shutil.copy2(P/name,D/'source'/name)
(D/'README246.txt').write_text('Ravedio246: clean upper pashmina strips\n\nRebuilds the distorted high crossing as controlled-width strips with smooth edges and coherent thickness. Depth fitting bridges minor hollows without distorting the X/Z outline. The upper edge stays below the chin.245 hood/neck wrap, free ends and fringe remain fixed, preserving the accepted244 placement. All other objects/materials/studio and shared coordinates are retained.\n\n14 authored top fits have source and fresh seven-angle GLB reviews;16 covered hairstyles have four-angle checks. Includes two packed/reopened scenes and matched245 comparison. New strip shape awaits owner review; native/phone qualification remains separate.\n',encoding='utf8',newline='\n')
print('FINISHED246',len(technical),'ordinary GLBs;14 top fits;2 packed scenes')
