from pathlib import Path
import json,struct,hashlib,re,sys
import numpy as np
P=Path(__file__).parent;D=P.parent/'floating138/mobile-preview/252';c=json.loads((D/'catalogue252.json').read_text());paths=set()
for b,bc in c['builds'].items():
 for st,r in bc['hair'].items():
  paths.add(r['path'])
  for fit in c['fits'][b+'-'+st].values():paths.add(fit['hair'])
for v in c['braidLengths'].values():paths.update(v.values())
one=next((x.split('=',1)[1].split(',') for x in sys.argv if x.startswith('--one=')),None)
changed='--changed' in sys.argv or one is not None
selected=one or ['flow','middle-part','buzz','curly-top','afro','locs']
if changed:
 paths={c['builds']['Masculine']['hair'][st]['path'] for st in selected}|{rec['hair'] for st in selected for rec in c['fits']['Masculine-'+st].values()}
if '--bare' in sys.argv:paths={r['path'] for bc in c['builds'].values() for r in bc['hair'].values()}
def acc(g,raw,i):
 a=g['accessors'][i];v=g['bufferViews'][a['bufferView']];dt={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']];n={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];item=np.dtype(dt).itemsize;out=np.ndarray((a['count'],n),dtype=dt,buffer=raw,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',item*n),item)).copy()
 return out.astype('f')/np.iinfo(dt).max if a.get('normalized') else out
def islands(n,ids):
 parent=np.arange(n)
 def root(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for a,b,d in ids.reshape(-1,3):
  ra,rb,rd=root(a),root(b),root(d);parent[rb]=ra;parent[rd]=ra
 labels=np.array([root(i) for i in range(n)]);order=np.argsort(labels);breaks=np.flatnonzero(np.diff(labels[order]))+1
 return np.split(order,breaks)
def field(p):
 mean=p.mean(axis=0);ev,ax=np.linalg.eigh(np.cov((p-mean).T));T=ax[:,-1];v=(p-mean)@T;lo,hi=np.percentile(v,[0,100]);t=(v-lo)/max(.001,hi-lo)
 if p[t<.1,1].mean()<p[t>.9,1].mean():t=1-t;v=-v
 N=mean-np.array([0,1.98,0]);N/=max(1e-8,np.linalg.norm(N));B=np.cross(T,N)
 if np.linalg.norm(B)<.05:B=ax[:,-2]
 B/=max(1e-8,np.linalg.norm(B));side=(p-mean)@B;bins=np.clip((t*48).astype(int),0,47);centers=np.array([np.median(side[bins==i]) if np.any(bins==i) else np.nan for i in range(48)]);valid=np.flatnonzero(np.isfinite(centers));centers=np.interp(np.arange(48),valid,centers[valid]);centers=np.convolve(np.pad(centers,(2,2),mode='edge'),np.ones(5)/5,'valid');local=side-np.interp(t,(np.arange(48)+.5)/48,centers);width=max(.005,np.percentile(np.abs(local),98));u=.5+local/(2*width)
 return u,t,float(ev[-1]/max(ev[-2],1e-10))
# A flow-aligned color texture avoids vertex-color stippling on curved locks.
from PIL import Image
import io,copy
w,h=1024,512;x,y=np.meshgrid(np.linspace(0,1,w),np.linspace(0,1,h));wander=.010*np.sin(y*5);mask=np.zeros_like(x)
for center,width,amp in [(.17,.024,.90),(.29,.019,1.0),(.64,.022,.80),(.80,.026,.95)]:mask=np.maximum(mask,amp*np.exp(-((x-center-wander)/width)**2))
mask*=np.clip((y-.025)/.19,0,1)*.72;hue=.40+.25*np.sin(y*2.8);base=np.array([.125,.048,.026]);gold=np.array([.55,.35,.17]);caramel=np.array([.34,.175,.070]);target=caramel[None,None,:]*(1-hue[:,:,None])+gold[None,None,:]*hue[:,:,None];rgb=base[None,None,:]*(1-mask[:,:,None])+target*mask[:,:,None];srgb=np.where(rgb<=.0031308,rgb*12.92,1.055*np.maximum(rgb,0)**(1/2.4)-.055);im=Image.fromarray(np.uint8(np.clip(srgb,0,1)*255));buf=io.BytesIO();im.save(buf,format='PNG');atlas=buf.getvalue()
records=[r for r in json.loads((P/'highlights252.json').read_text()) if r['source'] not in paths] if changed else [];out=dict(c['highlights']) if changed else {}
for no,path in enumerate(sorted(paths)):
 source=(D/path).resolve();raw=source.read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);binary=bytearray(raw[28+n:]);before=[]
 def add(data,component,typ,count,target=None):
  binary.extend(b'\0'*((-len(binary))%4));offset=len(binary);binary.extend(data);view={'buffer':0,'byteOffset':offset,'byteLength':len(data)}
  if target:view['target']=target
  vi=len(g['bufferViews']);g['bufferViews'].append(view)
  if component is None:return vi
  ai=len(g['accessors']);g['accessors'].append({'bufferView':vi,'componentType':component,'count':count,'type':typ});return ai
 imageview=add(atlas,None,None,None);imageid=len(g.setdefault('images',[]));g['images'].append({'name':'Fine caramel and honey flow252','bufferView':imageview,'mimeType':'image/png'});texid=len(g.setdefault('textures',[]));sampler=len(g.setdefault('samplers',[]));g['samplers'].append({'magFilter':9729,'minFilter':9987,'wrapS':10497,'wrapT':33071});g['textures'].append({'sampler':sampler,'source':imageid})
 for mesh in g['meshes']:
  for prim in mesh['primitives']:
   pos=acc(g,binary,prim['attributes']['POSITION']);before.append(hashlib.sha256(pos.tobytes()).hexdigest());mat=g['materials'][prim['material']];name=mat.get('name','')
   if re.search(r'tie|elastic|metal|band|Skin',name,re.I):continue
   old=acc(g,binary,prim['attributes']['COLOR_0']) if 'COLOR_0' in prim['attributes'] else np.ones((len(pos),4),dtype='f');alpha=old[:,3] if old.shape[1]==4 else np.ones(len(pos));lum=old[:,:3]@np.array([.2126,.7152,.0722]);shade=np.clip(np.sqrt(lum/max(.001,lum.mean())),.83,1.05);uv=acc(g,binary,prim['attributes']['TEXCOORD_0']) if 'TEXCOORD_0' in prim['attributes'] else None;flow=np.zeros((len(pos),2),dtype='<f4');idx=acc(g,binary,prim['indices']).astype('i').ravel()
   for k,ids in enumerate(islands(len(pos),idx)):
    if len(ids)<8:continue
    u,t,elongation=field(pos[ids]);is_cap=len(ids)>14000 or elongation<1.45
    if is_cap and not ('flowing sculpt' in name and uv is not None):
     u=np.full(len(ids),.01);t=np.full(len(ids),.01)
     if 'coil' in name or 'curl' in name:
      norm=acc(g,binary,prim['attributes']['NORMAL'])[ids];rad=pos[ids]-np.array([0,1.98,0]);rad/=np.maximum(1e-8,np.linalg.norm(rad,axis=1))[:,None];facing=np.sum(norm*rad,axis=1);u=np.full(len(ids),.30);t=.035+.075*np.clip((facing-.5)/.48,0,1)
    elif uv is not None and np.ptp(uv[ids,0])>.7 and np.ptp(uv[ids,1])>.8:u,t=uv[ids,0],1-uv[ids,1]
    if re.search('fade coverage|buzz edge|recessed|gathered loc roots',name,re.I):u=np.full(len(ids),.01);t=np.full(len(ids),.01)
    flow[ids]=np.column_stack((u,np.clip(t,0,1)))
   # Keep existing normal-map coordinates while making base color TEXCOORD_0.
   for key in sorted([k for k in prim['attributes'] if k.startswith('TEXCOORD_')],key=lambda k:int(k.split('_')[-1]),reverse=True):prim['attributes']['TEXCOORD_'+str(int(key.split('_')[-1])+1)]=prim['attributes'].pop(key)
   prim['attributes']['TEXCOORD_0']=add(flow.tobytes(),5126,'VEC2',len(pos),34962);col=np.column_stack((shade,shade,shade,alpha)).astype('<f4');prim['attributes']['COLOR_0']=add(col.tobytes(),5126,'VEC4',len(pos),34962)
   new=copy.deepcopy(mat)
   def shift(x):
    if isinstance(x,dict):
     if 'index' in x and set(x)&{'texCoord','scale','strength'}:x['texCoord']=x.get('texCoord',0)+1
     for key,val in x.items():
      if key.endswith('Texture') and isinstance(val,dict):val['texCoord']=val.get('texCoord',0)+1
      elif isinstance(val,(dict,list)):shift(val)
    elif isinstance(x,list):
     for v in x:shift(v)
   shift(new);pbr=new.setdefault('pbrMetallicRoughness',{});factor=pbr.get('baseColorFactor',[1,1,1,1]);pbr['baseColorFactor']=[1,1,1,factor[3]];pbr['baseColorTexture']={'index':texid,'texCoord':0};new['name']=name+' / flow-aligned highlights252';prim['material']=len(g['materials']);g['materials'].append(new)
 g['buffers'][0]['byteLength']=len(binary);js=json.dumps(g,separators=(',',':')).encode();js+=b' '*((-len(js))%4);binary.extend(b'\0'*((-len(binary))%4));blob=struct.pack('<III',0x46546c67,2,28+len(js)+len(binary))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(binary),0x004e4942)+binary
 key=hashlib.sha256(path.encode()).hexdigest()[:12];target='components/Highlights-'+key+'252-hair.glb';(D/target).write_bytes(blob);out[path]=target;after=[hashlib.sha256(acc(g,binary,p['attributes']['POSITION']).tobytes()).hexdigest() for m in g['meshes'] for p in m['primitives']];assert before==after
 records.append(dict(source=path,path=target,position_buffers_unchanged=True,alpha_preserved=True,base_color_uv=0,preserved_texture_coordinates='previous sets moved up one; existing maps updated',atlas=[w,h],bytes=len(blob)))
 if no%12==0:print('HIGHLIGHTS252_PROGRESS',no,len(paths),flush=True)
c['highlights']=out;(D/'catalogue252.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf8',newline='\n');(P/'highlights252.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf8');print('HIGHLIGHTS252_COMPLETE',len(out))
