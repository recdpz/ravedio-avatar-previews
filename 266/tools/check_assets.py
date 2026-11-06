from pathlib import Path
import json,struct,numpy as np
R=Path(__file__).resolve().parents[1];ROOT=R.parent;reports=json.loads((R/'verification/assets.json').read_text(encoding='utf8'))
def dec(p):
 raw=p.read_bytes();n=struct.unpack_from('<I',raw,12)[0];return json.loads(raw[20:20+n]),raw[28+n:]
def arr(g,b,i):
 a=g['accessors'][i];v=g['bufferViews'][a['bufferView']];dt=np.dtype({5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']]);w={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];return np.ndarray((a['count'],w),dt,buffer=b,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',w*dt.itemsize),dt.itemsize))
checked=[]
for it in reports:
 s,sb=dec(ROOT/it['source'].removeprefix('../'));g,b=dec(R/it['output']);assert s['nodes']==g['nodes'] and s.get('materials')==g.get('materials') and s.get('images')==g.get('images');radius_error=None;mincloth=99;insidecloth=0;body_exact=True
 for node in g['nodes']:
  if 'mesh' not in node:continue
  for p in g['meshes'][node['mesh']]['primitives']:
   inds=arr(g,b,p['indices']);assert np.array_equal(inds,arr(s,sb,p['indices']));pts=arr(g,b,p['attributes']['POSITION']);assert np.isfinite(pts).all();n=arr(g,b,p['attributes']['NORMAL']);assert np.isfinite(n).all() and np.max(abs(np.linalg.norm(n,axis=1)-1))<.003,(it['source'],node['name'],np.linalg.norm(n,axis=1).min(),np.linalg.norm(n,axis=1).max())
   for k,i in p['attributes'].items():
    if k not in ['POSITION','NORMAL']:assert np.array_equal(arr(g,b,i),arr(s,sb,i))
   if it['role']=='base' and node['name']!='Skin / soft oval head':
    for i in p['attributes'].values():assert np.array_equal(arr(g,b,i),arr(s,sb,i))
   if node['name']=='Skin / soft oval head':radius_error=float(np.max(abs(np.linalg.norm(pts-[0,1.88,-.015],axis=1)-.48)));assert radius_error<2e-7
   if it['role']=='headgear' and 'pashmina' in it['source']:
    tri=pts[inds.reshape(-1,3)];samples=np.concatenate([pts,tri.mean(axis=1),(tri[:,0]+tri[:,1])/2,(tri[:,1]+tri[:,2])/2,(tri[:,2]+tri[:,0])/2]);clear=np.linalg.norm(samples-[0,1.88,-.015],axis=1)-.48;mincloth=min(mincloth,float(clear.min()));insidecloth+=int((clear<0).sum())
 if mincloth<99:assert mincloth>0,(it['source'],mincloth,insidecloth)
 checked.append({'file':it['output'],'role':it['role'],'head_radius_error':radius_error,'pashmina_sampled_clearance':mincloth if mincloth<99 else None,'body_materials_topology_other_attributes_preserved':True})
(R/'verification/invariants.json').write_text(json.dumps(checked,indent=2),encoding='utf8');print('INVARIANTS266_COMPLETE',len(checked),'min cloth',min(x['pashmina_sampled_clearance'] for x in checked if x['pashmina_sampled_clearance'] is not None))
