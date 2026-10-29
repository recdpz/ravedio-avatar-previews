from pathlib import Path
import json,shutil,struct,hashlib,subprocess,datetime,io
from PIL import Image,ImageDraw
P=Path(__file__).parent;R=P.parent/'floating138/mobile-preview';D=R/'238'
fits=json.loads((P/'fits238.json').read_text());proof=json.loads((P/'proof238.json').read_text());hair=json.loads((P/'hair238.json').read_text());fixtures=json.loads((P/'fixtures238.json').read_text())
joins={build:{top:item['joined_surface'] for top,item in tops.items()} for build,tops in fits.items()}
assert all(j['surface_islands']==1 and j['open_seam_edges']==0 and j['upper_hood_exact'] for tops in joins.values() for j in tops.values())
(D/'joins238.json').write_text(json.dumps(joins,indent=2)+'\n',encoding='utf8',newline='\n')
assert sum(len(t) for t in fits.values())==14 and len(proof)==14 and len(hair)==16 and len(fixtures)==2
assert all(x['final_glbs_reopened'] and len(x['angles'])==7 and x['protected_exact'] for x in proof.values())
for build in fixtures:
    src=Path(fixtures[build]['source']);shutil.copy2(src,D/'assemblies'/f'{build}-pashmina238.blend')
    item=fixtures[build];assert item['packed'];assert all(x['packed'] for x in item['body_reference']['images'])
    assert item['portrait_settings']['120']['camera']['matrix_world']==item['portrait_settings']['512']['camera']['matrix_world']
for f in (P/'fixtures').glob('*.png'):shutil.copy2(f,D/'references'/f.name)
for f in (P/'review2').glob('*.png'):shutil.copy2(f,D/'references'/f.name)
# Small references are resampled from the exact128px render, never different
# geometry, tone, camera or lighting. They are visual evidence, not a phone test.
for f in (P/'review2').glob('*-skin*-portrait238-front.png'):
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
review=dict(revision=238,reviewer='self',owner_approval='pending',scope='Repair the two hood-to-neck-fold junctions only',passes=['Construction close-ups and all-angle checks of both builds and all14 top-specific fits.','Actual GLBs reopened, all14 tops at seven angles;16 covered hairstyles rechecked; both final assemblies packed/reopened.','Final browser comparison, close side/back/underside review and retained feature controls.'],protected='All237 heads, bodies, wardrobe, face/eyes, palette, fixed studio, covered/uncovered hair and all other headwear unchanged.',changes=['Join hood, wrap and both fold roots with shared mesh vertices and matching UVs.','Continue the face border into each neck fold instead of drawing a hem across the internal join.','Blend the local junction normals and apply cloth thickness once to the connected surface.','Retain237 wrap, narrow crossings, upper hood, top-specific contact and all other assets.'],hair='Every covered and uncovered hairstyle reuses its exact237 export; no hair geometry changed.',native_qualification='Not performed in this artwork correction.')
handoff=dict(revision=238,url='https://recdpz.github.io/ravedio-avatar-previews/238/',status='Owner-review correction candidate',baseline_commit='20524322159ac1c33d4f9c2ddb82753c19d6e912',scope=review['scope'],changes=review['changes'],protected=review['protected'],coordinates='Unchanged shared coordinates; Blender Z-up/front-Y, standard glTF Y-up/front+Z conversion only. Never independently recenter or resize components.',selection='pashminaTops[build][top] selects an authored lower-wrap fit; hair and clothing remain separate selectable/recolorable parts. previousPashminaFits and previousPashminaTops restore237 for the review checkbox, using the same selected top.',assemblies={b:'assemblies/'+b+'-pashmina238.blend' for b in fixtures},reference_framing='120 and512 front portraits use exactly the same camera transform and orthographic scale. Full settings are in fixtures238.json.',materials='Retain235 woven pattern and physically authored0.12 sheen intensity; map Blender weight to linear KHR_materials_sheen color factor. Ordinary uncompressed GLBs. No transmission or refraction in cloth. Existing clear glasses remain separate thin opacity panes.',fit_support='Retain236 radial major-form support, and extend the existing hood nape into a shoulder-seated wrap with front edges tucked below the crossing ends. Cloth follows major shoulders/chest and bridges small garment openings. No runtime physics. The broad fit does not authorize changing garment/body shapes.',portable_sources='Both assembled Blender scenes include their imported components and packed dependencies. Generator scripts also depend on the retained local235/224/226 authoring libraries; scenes do not require replaying those generators.',browser_vs_blender='Fixed reference Blender studio retained. Live browser PBR remains an approximation; color/depth portrait outputs must be rebaked together for the same geometry/camera/version.',technical='technical238.json',fixtures='fixtures238.json',review='review238.json',qualification='No native parity, transmission-aware portrait composition or real-phone benchmark claim. No profile-byte or product repository changes.')
for name,obj in [('technical238.json',technical),('review238.json',review),('handoff238.json',handoff),('fixtures238.json',fixtures),('fit-proof238.json',proof),('hair-fits238.json',hair)]:
    (D/name).write_text(json.dumps(obj,indent=2)+'\n',encoding='utf8',newline='\n')
for name in ['browser238.cjs','finish238.py','scarf238.py','joined238.py','verify238.py','package238.py']:
    shutil.copy2(P/name,D/'source'/name)
(D/'README238.txt').write_text('Ravedio238: pashmina fit correction\n\nOpen index.html through HTTP. Independent feature/color selectors remain. Compare235 pashmina switches only the prior wrap and its covered-hair fit.\n\nBoth builds: connected hood-to-fold joins and continuous border;237 neck wrap, narrow crossings and shoulder/chest contact retained.14 authored top fits and16 covered hairstyles were checked. Two packed Blender assemblies and seven-angle export references are included.\n\nSee handoff238.json, fixtures238.json and technical238.json for coordinates, camera/studio settings, dependencies and component statistics. New artwork awaits owner review; native/phone qualification is separate.\n',encoding='utf8',newline='\n')
print('FINISHED238',len(technical),'GLBs;14 top fits,16 hair reviews,2 portable scenes')
