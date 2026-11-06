from pathlib import Path
import json,struct,numpy as np,hashlib
R=Path(__file__).resolve().parents[1]; source=R.parent/'264/assets'; center=np.array([0,1.88,-.015]); radius=.48
roles={'hair','eyes','mouth','lashes','headgear','glasses','lenses','extra'}
def decode(p):
 b=p.read_bytes(); n=struct.unpack_from('<I',b,12)[0];return json.loads(b[20:20+n]),bytearray(b[28+n:])
def arr(g,b,i):
 a=g['accessors'][i];v=g['bufferViews'][a['bufferView']];d={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']];w={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];dt=np.dtype(d);return np.ndarray((a['count'],w),dt,buffer=b,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',w*dt.itemsize),dt.itemsize))
reports=[]
for build in ('Feminine','Masculine'):
 p=source/(build+'-optimized264.glb');g,b=decode(p);head=next(n for n in g['nodes'] if n.get('name')=='Skin / soft oval head');hp=g['meshes'][head['mesh']]['primitives'][0];h=arr(g,b,hp['attributes']['POSITION']).copy();v=h-center;rr=np.linalg.norm(v,axis=1);dirs=v/rr[:,None]
 # Fit a smooth directional radius field; discrete nearest-sample fields cause ripples.
 powers=[(x,y,z) for x in range(7) for y in range(7-x) for z in range(7-x-y)]
 def terms(u):return np.stack([u[:,0]**x*u[:,1]**y*u[:,2]**z for x,y,z in powers],axis=1)
 coef=np.linalg.lstsq(terms(dirs),rr,rcond=1e-10)[0]
 def morph(points):
  q=points-center;length=np.linalg.norm(q,axis=1);unit=q/np.maximum(length[:,None],1e-8);rhead=terms(unit)@coef
  outside=np.maximum(0,length-rhead);t=np.clip((outside-.12)/.36,0,1);fade=1-t*t*(3-2*t);return points+unit*((radius-rhead)*fade)[:,None]
 changed=[];untouched=[];seen=set()
 for n in g['nodes']:
  if 'mesh' not in n:continue
  ishead=n.get('name')=='Skin / soft oval head';role=n.get('extras',{}).get('component159');change=ishead or role in roles
  if not change:untouched.append(n.get('name'));continue
  if any(k in n for k in ('matrix','translation','rotation','scale')):raise ValueError('Unexpected transformed node '+n.get('name',''))
  for pr in g['meshes'][n['mesh']]['primitives']:
   pi=pr['attributes']['POSITION']
   if pi in seen:continue
   seen.add(pi);pos=arr(g,b,pi);old=pos.copy();new=center+(old-center)/np.linalg.norm(old-center,axis=1)[:,None]*radius if ishead else morph(old)
   pos[:]=new;a=g['accessors'][pi];a['min']=pos.min(axis=0).tolist();a['max']=pos.max(axis=0).tolist()
   if 'NORMAL' in pr['attributes']:
    normal=arr(g,b,pr['attributes']['NORMAL']);
    if ishead:normal[:]=(new-center)/radius
    else:
     # Preserve authored split normals, transporting them through the radial fit.
     eps=.00015;ref=np.zeros_like(old);ref[:,0]=1;ref[abs(normal[:,0])>.9]=[0,1,0];t1=np.cross(normal,ref);t1/=np.maximum(np.linalg.norm(t1,axis=1)[:,None],1e-9);t2=np.cross(normal,t1);base=new;nn=np.cross(morph(old+t1*eps)-base,morph(old+t2*eps)-base);normal[:]=nn/np.maximum(np.linalg.norm(nn,axis=1)[:,None],1e-9)
   if not np.isfinite(pos).all():raise ValueError('Nonfinite')
  changed.append(n.get('name'))
 js=json.dumps(g,separators=(',',':'),ensure_ascii=False).encode();js+=b' '*((-len(js))%4);b+=b'\0'*((-len(b))%4);out=struct.pack('<III',0x46546c67,2,28+len(js)+len(b))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(b),0x004e4942)+b
 target=R/'assets'/(build+'-sphere265.glb');target.write_bytes(out)
 rad=np.linalg.norm(arr(g,b,hp['attributes']['POSITION'])-center,axis=1);reports.append(dict(build=build,radius=radius,center=center.tolist(),max_radius_error=float(abs(rad-radius).max()),changed=changed,untouched=untouched,source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),output_sha256=hashlib.sha256(out).hexdigest()))
(R/'verification/geometry.json').write_text(json.dumps(reports,indent=2),encoding='utf8');print('SPHERE_COMPLETE',[(r['build'],r['max_radius_error']) for r in reports])
