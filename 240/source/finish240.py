from pathlib import Path
import json,shutil,struct,hashlib,subprocess,datetime,io
from PIL import Image,ImageDraw
P=Path(__file__).parent;R=P.parent/'floating138/mobile-preview';D=R/'240'
fits=json.loads((P/'fits240.json').read_text());proof=json.loads((P/'proof240.json').read_text());hair=json.loads((P/'hair240.json').read_text());fixtures=json.loads((P/'fixtures240.json').read_text())
joins={build:{top:item['joined_surface'] for top,item in tops.items()} for build,tops in fits.items()}
assert all(j['surface_islands']==1 and j['open_seam_edges']==0 and j['upper_hood_exact'] for tops in joins.values() for j in tops.values())
(D/'joins240.json').write_text(json.dumps(joins,indent=2)+'\n',encoding='utf8',newline='\n')
assert sum(len(t) for t in fits.values())==14 and len(proof)==14 and len(hair)==16 and len(fixtures)==2
assert all(x['final_glbs_reopened'] and len(x['angles'])==7 and x['protected_exact'] for x in proof.values())
for build in fixtures:
    src=Path(fixtures[build]['source']);shutil.copy2(src,D/'assemblies'/f'{build}-pashmina240.blend')
    item=fixtures[build];assert item['packed'];assert all(x['packed'] for x in item['body_reference']['images'])
    assert item['portrait_settings']['120']['camera']['matrix_world']==item['portrait_settings']['512']['camera']['matrix_world']
for f in (P/'fixtures').glob('*.png'):shutil.copy2(f,D/'references'/f.name)
for f in (P/'review2').glob('*.png'):shutil.copy2(f,D/'references'/f.name)
# Small references are resampled from the exact128px render, never different
# geometry, tone, camera or lighting. They are visual evidence, not a phone test.
for f in (P/'review2').glob('*-skin*-portrait240-front.png'):
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
review=dict(revision=240,reviewer='self',owner_approval='pending',scope='Narrow the two hanging pashmina ends only',changes=['Both free ends are22 percent narrower, easing in below the upper crossing.','Existing fabric row curves are resampled, retaining length, torso contact and drape.','Fringe anchors follow the narrower fabric while individual tassel shapes stay unchanged.'],protected='Approved239 hood, inner neck corners, wrap and upper crossing remain exactly unchanged. All nonheadgear components, colors, materials and fixed studio are retained.',passes=['All14 source fits, front/three-quarter/both sides/back/top/underside.','Fresh GLB assemblies at the same seven angles, matched239 comparisons and packed/reopened default scenes.','Browser outfit routes, comparison toggle, colors and close all-angle checks.'],hair='All16 covered hairstyles are exact retained239 inputs. Upper hair-contact cloth is unchanged; no new all-hairstyle render certification.',native_qualification='Separate and not performed here.')
handoff=dict(revision=240,url='https://recdpz.github.io/ravedio-avatar-previews/240/',status='Owner-review tail-width refinement',baseline_commit='f860bb0abc5c1367adbe15fffcd47528f3a8432c',scope=review['scope'],changes=review['changes'],protected=review['protected'],coordinates='Shared coordinates unchanged; native Blender Z-up to glTF Y-up conversion only. No independent component recentering/resizing.',selection='Independent controls retained. pashminaTops[build][top] selects the fit; Compare239 swaps only headgear with the same outfit and view.',assemblies={b:'assemblies/'+b+'-pashmina240.blend' for b in fixtures},reference_framing='120 and512 portraits have the same transform and orthographic scale; exact studio/camera/color settings in fixtures240.json.',materials='Exact239 woven texture, opaque cloth and0.12 sheen mapping. Ordinary uncompressed GLBs; no new transparency or refraction.',portable_sources='Two packed scenes include their imported components. narrow240.py starts from preserved239 per-top authoring scenes and uses retained235/224 helper libraries.',qualification='No native parity, depth-composition or phone-performance claim. No profile-byte or product-repository changes.',technical='technical240.json',fixtures='fixtures240.json',review='review240.json',approval='approval239.json')
for name,obj in [('technical240.json',technical),('review240.json',review),('handoff240.json',handoff),('fixtures240.json',fixtures),('fit-proof240.json',proof),('hair-fits240.json',hair),('tail-widths240.json',fits)]:
 (D/name).write_text(json.dumps(obj,indent=2)+'\n',encoding='utf8',newline='\n')
previous=json.loads((R/'239/manifest239.json').read_text())
approved=dict(revision=239,frozen_commit='f860bb0abc5c1367adbe15fffcd47528f3a8432c',owner_statement='perfect and maybe we can make the both ends less wide to showcase our user\'s shirts/tops more',scope='Owner acceptance of239 pashmina design direction and repaired inner neck joins in the review. Frozen file list is traceability, not separate owner sign-off of every outfit or native renderer.240 changes only the lower free-end widths.',frozen_reference_files=[i for i in previous['files'] if i['path'].startswith('components/')],other_catalogue_approval='Not implied by this scoped approval')
(D/'approval239.json').write_text(json.dumps(approved,indent=2)+'\n',encoding='utf8',newline='\n')
for name in ['narrow240.py','verify240.py','package240.py','finish240.py','browser240.cjs','close240.cjs']:
 shutil.copy2(P/name,D/'source'/name)
(D/'README240.txt').write_text('Ravedio240: narrower pashmina ends\n\nBoth hanging ends are22 percent narrower, smoothly blended below the crossing. The approved239 upper hood, wrap and repaired inner corners are frozen. All14 top fits have fresh seven-angle export references; both default scenes are packed/reopened.\n\nCompare239 keeps the selected outfit and view. See the matched comparison, rendering handoff, camera/studio settings and technical metrics. Retained hair and other catalogue assets are exact239. New width refinement awaits owner review; native and phone qualification remain separate.\n',encoding='utf8',newline='\n')
print('FINISHED240',len(technical),'ordinary GLBs;14 top fits;2 packed scenes')
