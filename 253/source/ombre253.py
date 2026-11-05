from pathlib import Path
import json,struct,hashlib,copy,re,sys,io
import numpy as np
from PIL import Image
P=Path(__file__).parent;R=P.parent/'floating138/mobile-preview';OLD=R/'252';D=R/'253';old=json.loads((OLD/'catalogue252.json').read_text());c=json.loads((D/'catalogue253.json').read_text());roles={}
def note(path,b,style,kind):roles.setdefault(path,[]).append((b,style,kind))
for b,bc in old['builds'].items():
 for style,rec in bc['hair'].items():
  note(rec['path'],b,style,'hair')
  for rec in old['fits'][b+'-'+style].values():note(rec['hair'],b,style,'hair')
for mode,values in old['braidLengths'].items():
 for top,path in values.items():note(path,'Feminine','twin-braids','lengths')
paths=set(old['highlights']);assert paths==set(roles),(paths-set(roles),set(roles)-paths)
only=next((x.split('=',1)[1].split(',') for x in sys.argv if x.startswith('--styles=')),None)
if only:paths={p for p in paths if any(st in only for b,st,k in roles[p])}
def acc(g,b,i):
 a=g['accessors'][i];v=g['bufferViews'][a['bufferView']];dt={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1',5122:'<i2'}[a['componentType']];n={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];item=np.dtype(dt).itemsize;q=np.ndarray((a['count'],n),dtype=dt,buffer=b,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',n*item),item)).copy();return q.astype('f')/np.iinfo(dt).max if a.get('normalized') else q
def smooth(x):x=np.clip(x,0,1);return x*x*(3-2*x)
def islands(n,ids):
 parent=np.arange(n)
 def root(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for a,b,d in ids.reshape(-1,3):ra,rb,rd=root(a),root(b),root(d);parent[rb]=ra;parent[rd]=ra
 lab=np.array([root(i) for i in range(n)]);order=np.argsort(lab);return np.split(order,np.flatnonzero(np.diff(lab[order]))+1)
# Broad blended color, without the former highlight ribbons.
w,h=128,1024;u,t=np.meshgrid(np.linspace(0,1,w),np.linspace(0,1,h));v=np.clip(t+.018*np.sin(u*2*np.pi*2)*np.sin(t*np.pi),0,1);root=np.array([.145,.062,.034]);mid=np.array([.32,.17,.078]);tip=np.array([.50,.32,.16]);a=smooth((v-.30)/.37);b=smooth((v-.58)/.36);rgb=root[None,None,:]*(1-a[:,:,None])+mid[None,None,:]*a[:,:,None];rgb=rgb*(1-b[:,:,None])+tip[None,None,:]*b[:,:,None];srgb=np.where(rgb<=.0031308,rgb*12.92,1.055*np.maximum(rgb,0)**(1/2.4)-.055);im=Image.fromarray(np.uint8(np.clip(srgb,0,1)*255));buf=io.BytesIO();im.save(buf,format='PNG');atlas=buf.getvalue();(D/'ombre-gradient253.png').write_bytes(atlas)
C=np.array([0,1.88,-.015]);RAD=np.array([.48,.455,.405]);out=dict(c['ombre']);records=json.loads((P/'ombre253.json').read_text()) if (P/'ombre253.json').exists() else [];records=[r for r in records if r['source'] not in paths]
for no,path in enumerate(sorted(paths)):
 b,style,kind=roles[path][0];src=(OLD/old['highlights'][path]).resolve();raw=src.read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);binary=bytearray(raw[28+n:]);preserved=[];imageids=set();ranges=[]
 def add(data):
  binary.extend(b'\0'*((-len(binary))%4));off=len(binary);binary.extend(data);vi=len(g['bufferViews']);g['bufferViews'].append({'buffer':0,'byteOffset':off,'byteLength':len(data)});return vi
 for mesh in g['meshes']:
  for prim in mesh['primitives']:
   for key,i in sorted(prim['attributes'].items()):
    if key!='TEXCOORD_0':preserved.append((key,i,hashlib.sha256(acc(g,binary,i).tobytes()).hexdigest()))
   preserved.append(('indices',prim['indices'],hashlib.sha256(acc(g,binary,prim['indices']).tobytes()).hexdigest()));mat=g['materials'][prim['material']];name=mat.get('name','')
   if re.search(r'tie|elastic|metal|band|Skin',name,re.I):continue
   pos=acc(g,binary,prim['attributes']['POSITION']);uv=acc(g,binary,prim['attributes']['TEXCOORD_0']);s=uv[:,1].copy();d=pos-C;radius=np.linalg.norm(d,axis=1);ell=np.linalg.norm(d/RAD,axis=1);depth=radius-radius/np.maximum(ell,1e-8)
   if b=='Masculine' and style in ['curly-top','afro'] and not re.search(r'fade coverage|graduation',name,re.I):s=.10+.88*smooth((depth-(.040 if style=='curly-top' else .055))/(.120 if style=='curly-top' else .110))
   elif b=='Feminine' and style in ['curls','box-braids','twin-braids']:
    end=1.10 if style=='twin-braids' else 1.20;start=2.24;s=(start-pos[:,1])/(start-end);s=np.where((depth<.022)&(pos[:,1]>1.85),0,s)
   elif b=='Feminine' and style=='ponytail':
    import heapq
    ids_all=acc(g,binary,prim['indices']).astype('i').ravel()
    for ids in islands(len(pos),ids_all):
     p=pos[ids];center=p.mean(axis=0)
     if len(ids)<100 or center[2]>-.18 or np.percentile(depth[ids],75)<.065:continue
     lookup=np.full(len(pos),-1,dtype='i');lookup[ids]=np.arange(len(ids));tri=lookup[ids_all.reshape(-1,3)];tri=tri[np.all(tri>=0,axis=1)];edges=np.concatenate((tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]]));edges=np.unique(np.sort(edges,axis=1),axis=0);weights=np.linalg.norm(p[edges[:,0]]-p[edges[:,1]],axis=1);ii=np.concatenate((edges[:,0],edges[:,1]));jj=np.concatenate((edges[:,1],edges[:,0]));ww=np.concatenate((weights,weights));dep=depth[ids];seeds=np.flatnonzero(dep<=np.quantile(dep,.01));adj=[[] for _ in ids]
     for aa,bb,weight in zip(ii,jj,ww):adj[aa].append((int(bb),float(weight)))
     dist=np.full(len(ids),np.inf);queue=[]
     for seed in seeds:dist[seed]=0;heapq.heappush(queue,(0,int(seed)))
     while queue:
      distance,aa=heapq.heappop(queue)
      if distance>dist[aa]:continue
      for bb,weight in adj[aa]:
       newdist=distance+weight
       if newdist<dist[bb]:dist[bb]=newdist;heapq.heappush(queue,(newdist,bb))
     assert np.isfinite(dist).all();s[ids]=dist/max(.001,np.quantile(dist,.985))
   elif b=='Feminine' and style=='space-buns':
    for ids in islands(len(pos),acc(g,binary,prim['indices']).astype('i').ravel()):
     p=pos[ids];center=p.mean(axis=0)
     if abs(center[0])>.17 and center[1]>2.18 and np.percentile(depth[ids],75)>.06:s[ids]=.10+.88*smooth((depth[ids]-.025)/.20)
   if re.search(r'fade coverage|graduation|recessed|gathered loc roots',name,re.I):s[:]=0
   if 'buzz edge' in name:s=.25+.11*smooth((pos[:,1]-2.10)/.20)
   uv[:,1]=np.clip(s,0,1);newuv=uv.astype('<f4');vi=add(newuv.tobytes());ai=len(g['accessors']);g['accessors'].append({'bufferView':vi,'componentType':5126,'count':len(pos),'type':'VEC2'});prim['attributes']['TEXCOORD_0']=ai;pbr=mat['pbrMetallicRoughness'];assert pbr['baseColorTexture'].get('texCoord',0)==0
   for key in ['normalTexture','occlusionTexture','emissiveTexture']:
    if key in mat:assert mat[key].get('texCoord',0)!=0,(style,key)
   imageids.add(g['textures'][pbr['baseColorTexture']['index']]['source']);mat['name']=re.sub(r' / flow-aligned highlights252','',name)+' / ombre253';ranges.append([float(uv[:,1].min()),float(uv[:,1].max())])
 imageview=add(atlas)
 for i in imageids:g['images'][i].update(bufferView=imageview,mimeType='image/png',name='Chestnut caramel honey ombre253')
 for key,i,sha in preserved:assert hashlib.sha256(acc(g,binary,i).tobytes()).hexdigest()==sha,(path,key)
 g['buffers'][0]['byteLength']=len(binary);js=json.dumps(g,separators=(',',':')).encode();js+=b' '*((-len(js))%4);binary.extend(b'\0'*((-len(binary))%4));blob=struct.pack('<III',0x46546c67,2,28+len(js)+len(binary))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(binary),0x004e4942)+binary;key=hashlib.sha256(path.encode()).hexdigest()[:12];target='components/Ombre-'+key+'253-hair.glb';(D/target).write_bytes(blob);canonical='../252/'+path if path.startswith('components/') else path;out[canonical]=target;records.append(dict(source=path,previous_color=old['highlights'][path],path=target,roles=roles[path],all_geometry_normals_indices_alpha_transforms_preserved=True,changes='Primary color UV progress and embedded color atlas only',growth_progress_ranges=ranges,bytes=len(blob)))
 if no%12==0:print('OMBRE253',no,len(paths),flush=True)
c['ombre']=out;(D/'catalogue253.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf8',newline='\n');(P/'ombre253.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf8');print('OMBRE253_COMPLETE',len(records))
