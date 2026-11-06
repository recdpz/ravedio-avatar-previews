"""Extract independent semantic components without changing coordinates or attributes."""
import json,struct,hashlib,copy
from pathlib import Path
D=Path(__file__).resolve().parent.parent
def read(file):
 raw=file.read_bytes();n=struct.unpack_from('<I',raw,12)[0];return json.loads(raw[20:20+n]),raw[28+n:]
def write(g,b,file):
 j=json.dumps(g,separators=(',',':')).encode();j+=b' '*((-len(j))%4);b+=b'\0'*((-len(b))%4)
 file.write_bytes(struct.pack('<5I',0x46546c67,2,28+len(j)+len(b),len(j),0x4e4f534a)+j+struct.pack('<2I',len(b),0x004e4942)+b)
def subset(g,b,role):
 q=copy.deepcopy(g);keep={i for i,n in enumerate(g['nodes'])if n.get('extras',{}).get('component159')==role};parents={c:i for i,n in enumerate(g['nodes'])for c in n.get('children',[])}
 for i in list(keep):
  while i in parents:i=parents[i];keep.add(i)
 ids=sorted(keep);nm={old:new for new,old in enumerate(ids)};q['nodes']=[q['nodes'][i]for i in ids]
 for n in q['nodes']:
  if 'children'in n:n['children']=[nm[i]for i in n['children']if i in nm]
 for s in q['scenes']:s['nodes']=[nm[i]for i in s.get('nodes',[])if i in nm]
 mids=sorted({n['mesh']for n in q['nodes']if 'mesh'in n});mm={x:i for i,x in enumerate(mids)};q['meshes']=[q['meshes'][i]for i in mids]
 for n in q['nodes']:
  if 'mesh'in n:n['mesh']=mm[n['mesh']]
 ps=[p for m in q['meshes']for p in m['primitives']];aids=sorted({i for p in ps for i in [p['indices'],*p['attributes'].values()]});am={x:i for i,x in enumerate(aids)};q['accessors']=[q['accessors'][i]for i in aids]
 for p in ps:p['indices']=am[p['indices']];p['attributes']={k:am[v]for k,v in p['attributes'].items()}
 mats=sorted({p['material']for p in ps});mt={x:i for i,x in enumerate(mats)};q['materials']=[q['materials'][i]for i in mats]
 for p in ps:p['material']=mt[p['material']]
 texture_infos=[]
 def scan(x):
  if isinstance(x,dict):
   for k,v in x.items():
    if k.endswith('Texture')and isinstance(v,dict)and'index'in v:texture_infos.append(v)
    else:scan(v)
  elif isinstance(x,list):
   for v in x:scan(v)
 scan(q['materials']);tids=sorted({x['index']for x in texture_infos});tm={x:i for i,x in enumerate(tids)};q['textures']=[q.get('textures',[])[i]for i in tids]
 for x in texture_infos:x['index']=tm[x['index']]
 imids=sorted({t['source']for t in q['textures']});immap={x:i for i,x in enumerate(imids)};q['images']=[q.get('images',[])[i]for i in imids]
 for t in q['textures']:t['source']=immap[t['source']]
 sids=sorted({t['sampler']for t in q['textures']if'sampler'in t});sm={x:i for i,x in enumerate(sids)};q['samplers']=[q.get('samplers',[])[i]for i in sids]
 for t in q['textures']:
  if 'sampler'in t:t['sampler']=sm[t['sampler']]
 vids=sorted({a['bufferView']for a in q['accessors']}|{im['bufferView']for im in q['images']});vm={x:i for i,x in enumerate(vids)};views=[];data=bytearray()
 for i in vids:
  v=copy.deepcopy(g['bufferViews'][i]);data.extend(b'\0'*((-len(data))%4));offset=v.get('byteOffset',0);chunk=b[offset:offset+v['byteLength']];v['byteOffset']=len(data);v['buffer']=0;data.extend(chunk);views.append(v)
 for a in q['accessors']:a['bufferView']=vm[a['bufferView']]
 for im in q['images']:im['bufferView']=vm[im['bufferView']]
 q['bufferViews']=views;q['buffers']=[{'byteLength':len(data)}]
 for k in ['textures','images','samplers']:
  if not q[k]:del q[k]
 q['asset']['generator']='Ravedio264 semantic component extraction; original shared coordinates';return q,bytes(data)
out=D/'components';out.mkdir(exist_ok=True);rows=[]
for build in ['Feminine','Masculine']:
 g,b=read(D/'assets'/f'{build}-optimized264.glb');roles=sorted({n.get('extras',{}).get('component159')for n in g['nodes']if'mesh'in n});assert None not in roles
 for role in roles:
  q,c=subset(g,b,role);file=out/f'{build}-{role}264.glb';write(q,c,file)
  rows.append(dict(build=build,role=role,file='components/'+file.name,bytes=file.stat().st_size,sha256=hashlib.sha256(file.read_bytes()).hexdigest(),nodes=[n['name']for n in q['nodes']if'mesh'in n],triangles=sum(q['accessors'][p['indices']]['count']//3 for m in q['meshes']for p in m['primitives']),materials=[m.get('name')for m in q['materials']],fit='Selected cap fit; same source263 world coordinates'))
(D/'components.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf8');print('COMPONENTS264_COMPLETE',len(rows))
