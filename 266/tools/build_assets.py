from pathlib import Path
import json,struct,numpy as np,hashlib
R=Path(__file__).resolve().parents[1];ROOT=R.parent;C=json.loads((ROOT/'263/catalogue263.json').read_text(encoding='utf8'));center=np.array([0,1.88,-.015]);radius=.48

def decode(p):
 raw=p.read_bytes();n=struct.unpack_from('<I',raw,12)[0];return json.loads(raw[20:20+n]),bytearray(raw[28+n:])
def arr(g,b,i):
 a=g['accessors'][i];v=g['bufferViews'][a['bufferView']];dt=np.dtype({5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']]);w={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];return np.ndarray((a['count'],w),dt,buffer=b,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',w*dt.itemsize),dt.itemsize))
g,b=decode(ROOT/'264/components/Feminine-base264.glb');head=next(n for n in g['nodes'] if n.get('name')=='Skin / soft oval head');h=arr(g,b,g['meshes'][head['mesh']]['primitives'][0]['attributes']['POSITION']);v=h-center;rr=np.linalg.norm(v,axis=1);dirs=v/rr[:,None];powers=[(x,y,z) for x in range(7) for y in range(7-x) for z in range(7-x-y)]
def terms(u):return np.stack([u[:,0]**x*u[:,1]**y*u[:,2]**z for x,y,z in powers],axis=1)
coef=np.linalg.lstsq(terms(dirs),rr,rcond=1e-10)[0]
def morph(points,cloth=False):
 q=points-center;length=np.linalg.norm(q,axis=1);unit=q/np.maximum(length[:,None],1e-8);rhead=terms(unit)@coef;outside=np.maximum(0,length-rhead);t=np.clip((outside-.12)/.36,0,1);fade=1-t*t*(3-2*t)
 if cloth:
  t=np.clip((points[:,1]-1.50)/.25,0,1);fade*=t*t*(3-2*t)
 out=points+unit*((radius-rhead)*fade)[:,None]
 if cloth:
  weight=np.exp(-((out[:,1]-1.43)/.075)**2)*np.exp(-(out[:,0]/.27)**4);out[:,1]-=.025*weight
 return out
entries={};builds={};fixed={};maps={}
def use(path,role,build):
 if not path:return None
 source=(ROOT/'263'/path).resolve();rel='../'+source.relative_to(ROOT).as_posix();entries.setdefault(rel,{'source':rel,'role':role,'build':build});return rel
for build,hairs in [('Feminine',['ponytail','straight','curls']),('Masculine',['taper','flow','middle-part'])]:
 c=C['builds'][build];s={'base':use(c['base'],'base',build),'pantsBase':use(c['pantsBases']['clothed'],'base',build)}
 for key,selected in [('hair',hairs),('tops',['tank','tshirt','jersey','open','buttonup','sweatshirt']),('bottoms',['shorts','pants','skirt']),('eyes',list(c['eyes'])),('mouths',['line']),('grooms',list(c['grooms']))]:
  role={'tops':'top','bottoms':'bottom','grooms':'groom','mouths':'mouth'}.get(key,key);s[key]={k:{'label':c[key][k]['label'],'path':use(c[key][k]['path'],role,build)} for k in selected if k in c[key]}
 s['lashes']={k:use(z['path'],'lashes',build) for k,z in c.get('lashes',{}).items()};s['fits']={};s['pashmina']={}
 for hair in hairs:
  s['fits'][hair]={}
  for hat in ['cap','pashmina']:
   s['fits'][hair][hat]={k:use(z,k,build) for k,z in C['fits'][build+'-'+hair][hat].items()}
  s['pashmina'][hair]={top:use(C['pashminaVariants'][build][hair][top],'headgear',build) for top in s['tops']}
 s['glasses']={'none':{'label':'None'},'rectangular':{'label':'Rectangular',**{k:use(z,k,build) for k,z in c['rectangular'].items()}},'reading':{'label':'Reading','glasses':use(C['glasses']['reading']['path'],'glasses',build),'lenses':use(C['glasses']['reading']['lenses'],'lenses',build)}}
 builds[build]=s
reports=[]
for i,(rel,item) in enumerate(entries.items()):
 role=item['role'];source=ROOT/rel.removeprefix('../');g,b=decode(source);original=g.copy();original_bytes=bytes(b);changed=[]
 if role in ['top','bottom']:continue
 for node in g['nodes']:
  if 'mesh' not in node:continue
  ishead=node.get('name')=='Skin / soft oval head'
  if role=='base' and not ishead:continue
  if any(k in node for k in ('matrix','translation','rotation','scale')):raise ValueError('Transform '+str(node))
  cloth=role=='headgear' and 'pashmina' in source.name
  for pr in g['meshes'][node['mesh']]['primitives']:
   p=pr['attributes']['POSITION'];pos=arr(g,b,p);old=pos.copy();new=center+(old-center)/np.linalg.norm(old-center,axis=1)[:,None]*radius if ishead else morph(old,cloth);pos[:]=new;g['accessors'][p]['min']=pos.min(axis=0).tolist();g['accessors'][p]['max']=pos.max(axis=0).tolist()
   if 'NORMAL' in pr['attributes']:
    normal=arr(g,b,pr['attributes']['NORMAL'])
    if ishead:normal[:]=(new-center)/radius
    else:
     eps=.00015;ref=np.zeros_like(old);ref[:,0]=1;ref[abs(normal[:,0])>.9]=[0,1,0];t1=np.cross(normal,ref);t1/=np.maximum(np.linalg.norm(t1,axis=1)[:,None],1e-9);t2=np.cross(normal,t1);nn=np.cross(morph(old+t1*eps,cloth)-new,morph(old+t2*eps,cloth)-new);normal[:]=nn/np.maximum(np.linalg.norm(nn,axis=1)[:,None],1e-9)
   if role=='mouth':
    # Subpixel stroke support: retain smile path and add a small, even tube expansion.
    nn=arr(g,b,pr['attributes']['NORMAL']);rad=pos-center;rad/=np.linalg.norm(rad,axis=1)[:,None];pos[:]+=nn*.0004+rad*.0003;g['accessors'][p]['min']=pos.min(axis=0).tolist();g['accessors'][p]['max']=pos.max(axis=0).tolist()
   assert np.isfinite(pos).all()
  changed.append(node.get('name'))
 if not changed:raise ValueError('No changed head '+rel)
 name=item['build']+'-'+source.stem+'-'+hashlib.sha256(rel.encode()).hexdigest()[:8]+'.glb';target=R/'assets'/name;js=json.dumps(g,separators=(',',':'),ensure_ascii=False).encode();js+=b' '*((-len(js))%4);b+=b'\0'*((-len(b))%4);target.write_bytes(struct.pack('<III',0x46546c67,2,28+len(js)+len(b))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(b),0x004e4942)+b);maps[rel]='./assets/'+name
 reports.append({'source':rel,'output':maps[rel],'role':role,'build':item['build'],'changed':changed,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'bytes':target.stat().st_size})
(R/'fixtures.json').write_text(json.dumps({'builds':builds,'sphere':maps,'scope':'Focused spherical fit evaluation; original263 catalogue retained. Three hairstyles per build; all six existing masculine facial-hair styles; five tops per build; cap/pashmina/clear and tinted glasses; four eyes and skins.'},indent=2),encoding='utf8')
(R/'verification/assets.json').write_text(json.dumps(reports,indent=2),encoding='utf8');print('ASSETS266_COMPLETE',len(reports),'MB',round(sum(r['bytes'] for r in reports)/1e6,2))
