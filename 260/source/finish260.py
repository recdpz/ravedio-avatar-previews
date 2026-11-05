from pathlib import Path
import json,hashlib,shutil,subprocess,io,ast,sys
import numpy as np
from PIL import Image,ImageDraw,ImageOps
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue259')
from glbcheck259 import glb,array
P=Path(__file__).parent;R=P.parent/'floating138/mobile-preview';D=R/'260';BASE='f20258331ae04f0965fd6df8043faad352556ff6';selected=json.loads((P/'selected260.json').read_text());c=json.loads((D/'catalogue260.json').read_text());browser=json.loads((P/'browser-verify260.json').read_text());assert len(browser['checks'])==154 and not browser['errors'] and not browser['http'];assert len(list((P/'browser-release2').glob('*.png')))==595
def save(name,data):(D/name).write_text(json.dumps(data,indent=2)+'\n',encoding='utf8',newline='\n')
def paste(im,f,x,y,w,h):
 pic=Image.open(f).convert('RGBA');bg=Image.new('RGBA',pic.size,'#29394c');bg.alpha_composite(pic);pic=ImageOps.contain(bg.convert('RGB'),(w,h));im.paste(pic,(x+(w-pic.width)//2,y))
closed=json.loads((P/'closed-fits260.json').read_text());assert len(closed['checks'])==112 and closed['images']==245 and not closed['errors'] and not closed['http']
patch=json.loads((P/'browser-patch260.json').read_text());assert len(patch['checks'])==62 and patch['images']==170 and not patch['errors'] and not patch['http']
angles=['front','threequarter','profile','rightprofile','rear','rearquarter','top','underside'];S=P/'browser-release2'
for key in selected:
 im=Image.new('RGB',(1200,600),'#29394c');dr=ImageDraw.Draw(im)
 for i,a in enumerate(angles):x=i%4*300;y=i//4*300;paste(im,S/f'{key}-none-{a}.png',x,y,300,275);dr.text((x+5,y+279),a,fill='white')
 im.save(D/'references'/f'{key}-angles260.jpg',quality=94)
 im=Image.new('RGB',(1200,600),'#29394c');dr=ImageDraw.Draw(im)
 for i,(kind,a) in enumerate((kind,a) for kind in ['before','none'] for a in ['front','profile','rightprofile','rear']):x=i%4*300;y=i//4*300;paste(im,S/f'{key}-{kind}-{a}.png',x,y,300,275);dr.text((x+5,y+279),('259' if kind=='before' else '260')+' / '+a,fill='white')
 im.save(D/'references'/f'{key}-comparison260.jpg',quality=94)
 im=Image.new('RGB',(1200,4350),'#29394c');dr=ImageDraw.Draw(im)
 for i,(hat,a) in enumerate((hat,a) for hat in ['cap','beanie','bucket','cowboy','headband','ears','pashmina'] for a in angles):x=i%4*300;y=i//4*300;paste(im,S/f'{key}-{hat}-{a}.png',x,y,300,275);dr.text((x+5,y+279),hat+' / '+a,fill='white')
 for i,a in enumerate(['front','rear']):paste(im,S/f'{key}-hidden-{a}.png',i*300,4200,300,140);dr.text((i*300+5,4337),'Cloth off / '+a,fill='white')
 im.save(D/'references'/f'{key}-covered260.jpg',quality=92)
im=Image.new('RGB',(1000,7*250),'#29394c');dr=ImageDraw.Draw(im)
for j,key in enumerate(selected):
 for i,col in enumerate(['default','black','blonde','ombre']):f=S/(f'{key}-none-threequarter.png' if col=='default' else f'{key}-{col}-none.png');paste(im,f,i*250,j*250,250,225);dr.text((i*250+3,j*250+229),key+' / '+col,fill='white')
im.save(D/'references/colors260.jpg',quality=94)
im=Image.new('RGB',(7*180,340),'#29394c');dr=ImageDraw.Draw(im)
for j,key in enumerate(selected):
 for i,skin in enumerate(['0','3']):paste(im,S/f'{key}-small120-{skin}.png',j*180,i*170,120,120);dr.text((j*180+3,i*170+125),key,fill='white')
im.save(D/'references/small260.jpg',quality=95)
tech=[]
for f in sorted((D/'components').glob('*.glb')):
 raw=f.read_bytes();g,b=glb(f);extensions=g.get('extensionsUsed',[]);assert not any(x in extensions for x in ['EXT_meshopt_compression','KHR_draco_mesh_compression','KHR_mesh_quantization','KHR_materials_transmission','KHR_materials_volume']);used={p['material'] for m in g.get('meshes',[]) for p in m['primitives']};textures=[]
 for img in g.get('images',[]):
  v=g['bufferViews'][img['bufferView']];pic=Image.open(io.BytesIO(b[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']]));textures.append(dict(width=pic.width,height=pic.height,mime=img['mimeType']))
 for mesh in g.get('meshes',[]):
  for pr in mesh['primitives']:
   for k in ['POSITION','NORMAL']:assert np.isfinite(array(g,b,pr['attributes'][k])).all(),(f,k)
   assert np.max(np.abs(np.linalg.norm(array(g,b,pr['attributes']['NORMAL']),axis=1)-1))<.001,f
 tech.append(dict(path=f.relative_to(D).as_posix(),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),triangles=sum(g['accessors'][p['indices']]['count']//3 for m in g.get('meshes',[]) for p in m['primitives']),materials=len(used),primitives=sum(len(m['primitives']) for m in g.get('meshes',[])),textures=textures,alpha_modes=sorted({g['materials'][i].get('alphaMode','OPAQUE') for i in used}),compressed=False,quantized=False,transmission=False))
assert len(tech)==168,len(tech)
assert c['colors']==c['before259']['colors'];refs=set()
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
assemblies=json.loads((P/'assemblies260.json').read_text());assert len(assemblies)==7
for row in assemblies.values():shutil.copy2(row['source'],D/row['packed_path'])
review=dict(revision=260,status='New artwork pending owner review',source_passes=7,fit_passes=4,iteration='Rejected sparse separate-lock source pass; closed coverage, refined Flow S paths, shortened curtain nape, reduced Loc fiber lumps. Close-up female profiles showed the damage extended below the root repair: reconstructed complete temple/middle cross-sections with restrained depth and seated selected Side sweep roots beneath their neighbors. Rejected abrupt hat bands, then coincident radially clamped surfaces; final closed fits preserve layer order with proportional compression. Final female patch supersedes those two styles in earlier capture checks.',checks=len(browser['checks']),closed_fit_checks=len(closed['checks']),final_female_patch_checks=len(patch['checks']),exported_images=595,all_angle_covered_views=392,cloth_hidden_views=14,exact120px_views=14,protected='Bodies, faces, wardrobe, all palettes, fixed studio, headgear and other hairstyle geometry retained byte-identically.',limits='Source/browser artwork verification; native alpha composition and phone performance remain separate.')
handoff=dict(revision=260,baseline_commit=BASE,selected_sources=selected,changes={k:v.get('method',v.get('flow','')) for k,v in selected.items()},coordinates='Shared coordinates and independently addressable/recolorable components retained; no recentering.',exports='168 ordinary GLBs:56 hair,56 OmbrÃ©,56 seated sprouts. Seven packed final-GLB assemblies and28 matched color/Z pairs.',rendering='Hair primarily opaque; preserve material and COLOR_0 alpha where present. OmbrÃ© changes pigment only. No transmission/refraction or compression added.',lighting='Fixed studio/camera/exposure/color settings in assemblies260.json. Blender shader/color-management effects do not transfer identically through GLB.',depth='Color and32-bit Z regenerated together from final GLBs at120/512 with identical camera matrices. Assembled references are not complete alpha-occlusion layer fixtures.',qualification=review['limits'],profile_contract='No profile bytes, wire changes, mobile renderer or product-repository edits.',technical='technical260.json',controls='All independent feature controls, fixed lighting, zoom/rotation and Compare259 retained.')
finalfits=json.loads((P/'fits/fits260.json').read_text());finalfits.update(json.loads((P/'fits3/fits260.json').read_text()));finalfits.update(json.loads((P/'fits4/fits260.json').read_text()));handoff['fit_strategy']='Cap, beanie, bucket and cowboy hair fits use proportional radial compression with a smooth transition below the rim; layer order and relief are retained. Other fitted hair retains the existing covered-root method. Final female variants use the complete repaired temple/middle lengths. Headgear geometry stays unchanged.'
for name,data in [('technical260.json',tech),('assemblies260.json',assemblies),('review260.json',review),('handoff260.json',handoff),('dependencies260.json',dict(baseline_commit=BASE,retained_glbs=deps)),('browser260.json',browser),('closed-fits260.json',closed),('browser-patch260.json',patch),('fits260.json',finalfits),('selected-settings260.json',selected),('ombre260.json',json.loads((P/'ombre260.json').read_text()))]:save(name,data)
for name in ['common260.py','build260.py','female260.py','select260.py','fits260.py','soft-fits260.py','overlay-fits260.py','closed-fits260.cjs','female-fits260.py','overlay-female260.py','browser-patch260.cjs','prepare-female-patch260.py','reference-patch260.py','package260.py','ombre260.py','browser260.cjs','prototype260.cjs','reference260.py','gallery260.py','finish260.py','plan260.json']:
 f=P/name
 if f.suffix=='.py':ast.parse(f.read_text(encoding='utf-8-sig'))
 shutil.copy2(f,D/'source'/name)
(D/'README260.txt').write_text('Ravedio260 - Hairstyle refinements\n\nAfro is slightly lower. Flow has a new off-center part with curved face framing and relaxed ear/nape layers. Locs use fuller mature sections and compact irregular fiber relief rather than thin rods over a painted root layer. Middle part has shorter curtains and a higher layered nape. Straight/Side sweep root rings are repaired as whole cross-sections; exposed internal temple support was removed. Box braids are slightly shorter.\n\nUse Compare259 for matching previous hairstyles. All features/colors remain independent, with rotation/zoom and fixed lighting. Eight-angle source and exported headwear reviews plus color/small checks were performed; first source gaps and root ridges were rejected and iterated.\n\n168 ordinary GLBs, seven packed assemblies and28 matched color/depth pairs. Preserve shared transforms, component/color separation and any vertex opacity. Native/phone qualification is separate; new260 artwork awaits owner review.\n',encoding='utf8',newline='\n');print('FINISH260_COMPLETE',len(tech),len(deps),flush=True)
