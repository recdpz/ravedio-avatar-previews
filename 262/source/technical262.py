from pathlib import Path
import json,sys,hashlib,io,subprocess
import numpy as np
from PIL import Image
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue259');from glbcheck259 import glb,array
P=Path('E:/Ravedio-Avatar/catalogue262');R=P.parent/'floating138/mobile-preview';D=R/'262';c=json.loads((D/'catalogue262.json').read_text());tech=[]
def active(g):
 seen=set()
 def visit(i):
  if i in seen:return
  seen.add(i)
  for j in g['nodes'][i].get('children',[]):visit(j)
 for n in g['scenes'][g.get('scene',0)].get('nodes',[]):visit(n)
 return seen
for f in sorted(list((D/'components').glob('*.glb'))+list((D/'assemblies').glob('*.glb'))):
 g,bb=glb(f);ids=active(g);active_meshes=set(g['nodes'][i]['mesh']for i in ids if'mesh'in g['nodes'][i]);tri=0;nv=0;stored=0
 for mi,m in enumerate(g['meshes']):
  for pr in m['primitives']:
   pos=array(g,bb,pr['attributes']['POSITION']);n=array(g,bb,pr['attributes']['NORMAL']);assert np.isfinite(pos).all()and np.isfinite(n).all();assert np.abs(np.linalg.norm(n,axis=1)-1).max()<.001;ix=array(g,bb,pr['indices']).reshape(-1,3).astype('i');assert ix.min()>=0 and ix.max()<len(pos);stored+=len(ix)
   if mi in active_meshes:nv+=len(pos);tri+=len(ix)
 ext=g.get('extensionsUsed',[]);assert not set(ext)&{'EXT_meshopt_compression','KHR_draco_mesh_compression','KHR_mesh_quantization'}
 textures=[]
 for im in g.get('images',[]):
  bv=g['bufferViews'][im['bufferView']];pic=Image.open(io.BytesIO(bb[bv.get('byteOffset',0):bv.get('byteOffset',0)+bv['byteLength']]));textures.append({'width':pic.width,'height':pic.height,'mime':im['mimeType']})
 mats=[{'name':m.get('name'),'alphaMode':m.get('alphaMode','OPAQUE'),'doubleSided':m.get('doubleSided',False),'transmission':m.get('extensions',{}).get('KHR_materials_transmission',{}),'ior':m.get('extensions',{}).get('KHR_materials_ior',{}),'volume':m.get('extensions',{}).get('KHR_materials_volume',{})}for m in g.get('materials',[])]
 tech.append({'path':f.relative_to(D).as_posix(),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'active_triangles':tri,'stored_triangles':stored,'active_vertices':nv,'active_meshes':len(active_meshes),'materials':len(mats),'textures':textures,'material_requirements':mats,'extensions':ext,'finite_positions_unit_normals_valid_indices':True,'compression_quantization':False})
assert len(tech)==8
# Active pants bases retain exact BIN payload and every retained node transform/material/accessor from the original.
variants=json.loads((P/'base-variants262.json').read_text())
for key,r in variants.items():
 g,bb=glb((R/'261'/r['source']).resolve());name=r['path'].replace('fix262-','');q,bq=glb(D/'components'/name);assert bb==bq
 for k in ['meshes','materials','accessors','bufferViews','buffers']:assert g.get(k)==q.get(k),key+' '+k
 for x,y in zip(g['nodes'],q['nodes']):assert {k:v for k,v in x.items()if k!='children'}=={k:v for k,v in y.items()if k!='children'}
 assert not any('leg blob'in q['nodes'][i].get('name','').lower()for i in active(q));r['public_path']='components/'+name;r['verified_geometry_materials_transforms_exact']=True
# Referenced prior GLBs must still match the frozen261 commit; enumerate all references, including comparison sources.
refs=set()
def walk(x):
 if isinstance(x,dict):
  for k,v in x.items():walk(k);walk(v)
 elif isinstance(x,list):
  for y in x:walk(y)
 elif isinstance(x,str)and x.endswith('.glb')and not x.startswith(('http:','https:')):refs.add((D/x).resolve())
walk(c);tracked={}
for line in subprocess.check_output(['git','ls-tree','-r','b0a1a1215617e93f30af14108c58929c37f26e2d'],cwd=R,text=True).splitlines():
 meta,path=line.split('\t',1);tracked[path]=meta.split()[2]
deps=[]
for f in sorted(refs):
 assert f.exists(),str(f)
 if D in f.parents:continue
 rel=f.relative_to(R).as_posix();data=f.read_bytes();blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest();assert tracked[rel]==blob,rel;deps.append({'path':rel,'bytes':len(data),'git_blob':blob,'exact_frozen261':True})
(D/'technical262.json').write_text(json.dumps({'revision':262,'assets':tech,'pants_variants':variants,'note':'Active/stored counts differ intentionally in explicit pants bases: unreachable original leg data is retained byte-exact, not presented as optimized. Native importer must honor active scene graph; Blender packed fixtures omit excluded leg nodes.'},indent=2)+'\n',encoding='utf8');(D/'dependencies262.json').write_text(json.dumps({'baseline':'b0a1a1215617e93f30af14108c58929c37f26e2d','retained_glbs':deps},indent=2)+'\n',encoding='utf8');print('TECHNICAL262_COMPLETE',len(tech),'newGLBs',len(deps),'exact prior dependencies')
