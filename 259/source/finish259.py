from pathlib import Path
import json,hashlib,shutil,subprocess,io,ast
import numpy as np
from PIL import Image,ImageDraw,ImageOps
from glbcheck259 import *
P=Path(__file__).parent;R=P.parent/'floating138/mobile-preview';D=R/'259';BASE='f5e302d931298e6267aa058516d396e74756918b';STYLES=['taper','sidepart','curly-top'];LABELS=dict(taper='Taper',sidepart='Crop',**{'curly-top':'Curly top'})
def load(f):return json.loads(Path(f).read_text(encoding='utf-8-sig'))
def save(n,obj):(D/n).write_text(json.dumps(obj,indent=2)+'\n',encoding='utf8',newline='\n')
browser=load(P/'browser259.json');extra=load(P/'extra-angles259.json');shape=load(P/'shape259.json');authors=load(P/'pass4/hair259.json')
flow_checks=load(P/'ombre-flow259.json');assert len(flow_checks['checks'])==16 and not flow_checks['errors'] and not flow_checks['http']
assert len(browser['checks'])==137 and not browser['errors'] and not browser['http'];assert extra['additionalExportedViews']==90 and not extra['errors']
assert len(list((P/'browser-final').glob('final-*.png')))==272;assert len(load(D/'depth259.json')['pairs'])==30;assert shape['taper']['top_height_unchanged'] and shape['crop']['closed_surface']
for st in STYLES:
 for src,dst in [(f'{st}-final-review259.jpg',f'{st}-angles259.jpg'),(f'{st}-covered-review259.jpg',f'{st}-covered259.jpg')]:shutil.copy2(P/src,D/'references'/dst)
 im=Image.new('RGB',(1200,620),'#29394c');draw=ImageDraw.Draw(im)
 for row,kind in enumerate(['before','none']):
  for col,angle in enumerate(['front','profile','rear','top']):
   paste(im,P/'browser-final'/f'final-{st}-{kind}-{angle}.png',col*300,row*310,300,285);draw.text((col*300+5,row*310+288),('258 / '+('Side part' if st=='sidepart' else LABELS[st]) if row==0 else '259 / '+LABELS[st])+' / '+angle,fill='white')
 im.save(D/'references'/f'{st}-comparison259.jpg',quality=94)
im=Image.new('RGB',(800,525),'#29394c');draw=ImageDraw.Draw(im)
for i,(st,color,skin) in enumerate((st,color,skin) for st in STYLES for color in ['default','ombre'] for skin in ['0','3']):
 f=P/'browser-final'/f'final-{st}-{color}-skin{skin}-small120.png';assert Image.open(f).size==(120,120);x=i%4*200;y=i//4*175;paste(im,f,x+40,y,120,120);draw.text((x+8,y+128),LABELS[st]+' / '+color+' / skin'+skin,fill='white')
im.save(D/'references/small259.jpg',quality=95)
im=Image.new('RGB',(1200,930),'#29394c');draw=ImageDraw.Draw(im)
for row,st in enumerate(STYLES):
 for col,color in enumerate(['default','black','blonde','ombre']):
  name=f'final-{st}-'+('none' if color=='default' else color)+'-threequarter.png';paste(im,P/'browser-final'/name,col*300,row*310,300,282);draw.text((col*300+8,row*310+288),LABELS[st]+' / '+color,fill='white')
im.save(D/'references/colors259.jpg',quality=94)
im=Image.new('RGB',(1000,1060),'#29394c');draw=ImageDraw.Draw(im)
for row,angle in enumerate(['profile','rightprofile']):
 for col,kind in enumerate(['214','259']):
  f=P/'browser-pass4'/f'214-taper-{angle}.png' if kind=='214' else P/'browser-final'/f'final-taper-none-{angle}.png';paste(im,f,col*500,row*530,500,500);draw.text((col*500+10,row*530+508),('214 / directional reference' if kind=='214' else '259 / shorter banks, curved direction')+' / '+angle,fill='white')
im.save(D/'references/direction214-comparison259.jpg',quality=95)
tech=[]
for f in sorted((D/'components').glob('*.glb')):
 raw=f.read_bytes();g,b=glb(f);used={p['material'] for m in g['meshes'] for p in m['primitives']};assert not set(g.get('extensionsUsed',[]))&{'KHR_draco_mesh_compression','EXT_meshopt_compression','KHR_mesh_quantization'};textures=[]
 for img in g.get('images',[]):
  v=g['bufferViews'][img['bufferView']];blob=b[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']];pic=Image.open(io.BytesIO(blob));textures.append(dict(size=[pic.width,pic.height],bytes=len(blob)))
 trans=[g['materials'][i]['name'] for i in used if set(g['materials'][i].get('extensions',{}))&{'KHR_materials_transmission','KHR_materials_volume'}];assert not trans
 for m in g['meshes']:
  for pr in m['primitives']:
   for key in ['POSITION','NORMAL']:assert np.isfinite(array(g,b,pr['attributes'][key])).all()
   normals=array(g,b,pr['attributes']['NORMAL']);assert np.max(np.abs(np.linalg.norm(normals,axis=1)-1))<.001
   if 'COLOR_0' in pr['attributes']:
    colors=array(g,b,pr['attributes']['COLOR_0']);assert np.isfinite(colors).all()
    if colors.shape[1]==4:assert colors[:,3].min()>=0 and colors[:,3].max()<=1.000001
 tech.append(dict(path=f.relative_to(D).as_posix(),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),triangles=sum(g['accessors'][pr['indices']]['count']//3 for m in g['meshes'] for pr in m['primitives']),materials=len(used),primitives=sum(len(m['primitives']) for m in g['meshes']),textures=textures,alpha_modes=sorted({g['materials'][i].get('alphaMode','OPAQUE') for i in used}),transmission=trans,compressed=False,quantized=False))
assert len(tech)==72
g,b=glb(D/'components/Masculine-sidepart-hair259-ombre.glb');flow_proof=[]
for mesh in g['meshes']:
 if 'textured forward Crop' not in mesh['name']:continue
 for pr in mesh['primitives']:
  if g['materials'][pr['material']].get('alphaMode')=='BLEND':continue
  pos=array(g,b,pr['attributes']['POSITION']);color=array(g,b,pr['attributes']['COLOR_0']);luma=color[:,:3]@np.array([.2126,.7152,.0722]);rear=float(luma[pos[:,2]<-.15].mean());front=float(luma[pos[:,2]>.22].mean());assert front>rear*2;flow_proof.append(dict(rear_root_linear_luma=rear,front_end_linear_luma=front))
assert flow_proof
c=load(D/'catalogue259.json');assert c['colors']==c['before258']['colors'];assert c['builds']['Masculine']['hair']['sidepart']['label']=='Crop';refs=set()
def scan(x):
 if isinstance(x,dict):
  for v in x.values():scan(v)
 elif isinstance(x,list):
  for v in x:scan(v)
 elif isinstance(x,str) and x.endswith('.glb'):refs.add((D/x).resolve())
scan(c);assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()==BASE
blobs={line.split('\t',1)[1]:line.split()[2] for line in subprocess.check_output(['git','ls-tree','-r','HEAD'],cwd=R,text=True).splitlines()};deps=[]
for f in sorted(refs):
 assert f.exists() and f.is_relative_to(R.resolve()),f
 if f.is_relative_to(D.resolve()):continue
 raw=f.read_bytes();key=f.relative_to(R).as_posix();assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==blobs[key],key;deps.append(dict(path=key,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
assemblies=load(P/'assemblies259.json')
for row in assemblies.values():shutil.copy2(row['source'],D/row['packed_path'])
review=dict(revision=259,status='New artwork pending owner review',source_passes=4,iterations='Rejected pointed separate-lock fringe, rounded row gaps, then raised shell edge. Final Crop has continuous flow, varied rounded clumps and narrow fitted edges. Taper uses original paths with rounded truncated ends; changed normals rebuilt. Final color pass corrected reversed post-export Ombré flow on Taper/Crop.',source_shape_proof=shape,exported_visual_views=272,covered_visual_views=168,cloth_hidden_views=6,exact120px_images=12,local_browser_checks=137,final_ombre_fit_checks=16,ombre_flow_proof=flow_proof,protected='Taper upper height and six rounded rear banks exact; Curly crown exact. Body/face/wardrobe/skin/palette/Black/studio/headgear and other hairstyle geometry unchanged.',limits='Artwork/browser export checks only. Native alpha rendering and phone performance qualification remain separate.')
handoff=dict(revision=259,baseline_commit=BASE,changed_styles=STYLES,labels=dict(sidepart='Crop',taper='Taper',**{'curly-top':'Curly top'}),geometry='Taper side banks cut shorter along original paths with rounded closures; upper height and six rear banks preserved. New Crop uses a closed crown-to-front sculpt with shallow irregular clumps, slight diagonal drift and no hard part. Curly crown retained.',directional_fade='Actual214 rounded curved fine-direction mesh reused and reseated on the current head; original vertex opacity retained. Smooth258 base field retained without the ripple/white-glint artifact.',rendering='Main hair cores remain OPAQUE. Fade, direction marks and narrow terminal boundaries use BLEND vertex opacity; no transmission/refraction. Preserve COLOR_0 alpha and material separation. A nearest-opaque baker alone cannot reproduce these edges.',colors='Palettes unchanged, including neutral Black#303030. Material shade control retains hairShade258 as a compatibility key. Ombré buffers preserve geometry/UV/indices/normals/transforms and opacity.',coordinates='Shared coordinates and independently selectable/recolorable components preserved. No recentering or per-component resizing.',exports='72 ordinary GLBs:24 hair,24 Ombré,24 seated sprouts. Three packed final-GLB assemblies and30 matched120/512 color/Z pairs.',references='Color and32-bit Z share final geometry/camera/version, alpha threshold0.5. These assembled references are not a complete component/alpha occlusion bake. Regenerate both together when geometry or camera changes.',lighting='Fixed studio/camera/exposure/color management recorded in assemblies259.json. Blender shader/tonemapping effects do not transfer identically through GLB.',controls='Compare258 shows the previous Taper, Side part and Curly side detail.214 directional reference is a matched board; original raised B comparison remains available for bare Taper.',qualification=review['limits'],technical='technical259.json',profile_contract='No wire/profile-byte assignment, mobile renderer or product-repository changes.')
handoff['colors']+=' Taper/Crop Ombré now follows authored root-to-tip flow after the glTF UV flip; roots stay darker and grown ends lighten.'
for name,obj in [('technical259.json',tech),('assemblies259.json',assemblies),('review259.json',review),('handoff259.json',handoff),('dependencies259.json',dict(baseline_commit=BASE,retained_glbs=deps)),('browser259.json',browser),('extra-angles259.json',extra),('ombre-flow259.json',flow_checks),('ombre259.json',load(P/'ombre259.json')),('fits259.json',load(P/'pass4/fits259.json')),('shape259.json',shape),('selected-settings259.json',dict(plan=load(P/'plan259.json'),authors=authors))]:save(name,obj)
for name in ['build259.py','refine259.py','sculpt259.py','finish-sculpt259.py','fits259.py','package259.py','ombre259.py','ombre-flow259.cjs','reference259-final.py','shape259.py','prototype259.cjs','browser259.cjs','extra-angles259.cjs','board259.py','glbcheck259.py','finish259.py']:
 f=P/name
 if f.suffix=='.py':ast.parse(f.read_text(encoding='utf-8-sig'))
 shutil.copy2(f,D/'source'/name)
(D/'README259.txt').write_text('Ravedio259 - Shorter Taper / Crop\n\nTaper side banks have much less downward overhang, while upper height and six rounded rear banks remain exact. Directional detail uses214 curved marks on the current head and the smooth low-glare fade base. Curly top uses the same side treatment.\n\nCrop completely replaces Side part: crown-to-front flow, modest clumped volume, a slightly uneven rounded fringe and shorter sides. No hard part. Use Compare258 for the preceding cuts, and the214 directional board for the line pattern reference. Independent feature/color controls, rotation/zoom, fixed lighting and neutral Black remain.\n\nAll covered/color fits reviewed. Package:72 ordinary GLBs, three packed assemblies,30 matched color/Z pairs, technical reports and source shape proof. Hair cores are opaque; faded sides and narrow terminal edges require correct vertex-alpha blending. Native renderer and phone qualification remain separate. New259 artwork awaits owner review.\n',encoding='utf8',newline='\n')
print('FINISH259_COMPLETE',len(tech),'newGLBs',len(deps),'exact retained dependencies',flush=True)
