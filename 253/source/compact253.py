from pathlib import Path
import json,struct,hashlib,copy
P=Path(__file__).parent;D=P.parent/'floating138/mobile-preview/253'
def signature(g,b):
 result=[]
 for m in g['meshes']:
  for p in m['primitives']:
   for key,i in sorted(p['attributes'].items()):
    a=g['accessors'][i];v=g['bufferViews'][a['bufferView']];item={5120:1,5121:1,5122:2,5123:2,5125:4,5126:4}[a['componentType']];n={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']];size=item*n;start=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',size);h=hashlib.sha256()
    for j in range(a['count']):h.update(b[start+j*stride:start+j*stride+size])
    result.append((key,a['count'],a['type'],a['componentType'],h.hexdigest()))
   i=p['indices'];a=g['accessors'][i];v=g['bufferViews'][a['bufferView']];start=v.get('byteOffset',0)+a.get('byteOffset',0);size={5121:1,5123:2,5125:4}[a['componentType']]*a['count'];result.append(('indices',hashlib.sha256(b[start:start+size]).hexdigest()))
 return result
records=[]
for f in sorted((D/'components').glob('*.glb')):
 r=f.read_bytes();n=struct.unpack_from('<I',r,12)[0];g=json.loads(r[20:20+n]);binary=r[28+n:];assert len(g['buffers'])==1 and not g.get('animations') and not g.get('skins');before=signature(g,binary);used=set()
 for m in g['meshes']:
  for p in m['primitives']:
   used.update(p['attributes'].values());used.add(p['indices'])
   for t in p.get('targets',[]):used.update(t.values())
 remap={old:new for new,old in enumerate(sorted(used))};accessors=[g['accessors'][i] for i in sorted(used)]
 for m in g['meshes']:
  for p in m['primitives']:
   p['attributes']={k:remap[v] for k,v in p['attributes'].items()};p['indices']=remap[p['indices']]
   for t in p.get('targets',[]):
    for k,v in list(t.items()):t[k]=remap[v]
 views={a['bufferView'] for a in accessors};assert all('sparse' not in a for a in accessors);views.update(i['bufferView'] for i in g.get('images',[]));viewmap={old:new for new,old in enumerate(sorted(views))};newbin=bytearray();newviews=[]
 for i in sorted(views):
  v=copy.deepcopy(g['bufferViews'][i]);newbin.extend(b'\0'*((-len(newbin))%4));offset=len(newbin);start=v.get('byteOffset',0);newbin.extend(binary[start:start+v['byteLength']]);v['byteOffset']=offset;newviews.append(v)
 for a in accessors:a['bufferView']=viewmap[a['bufferView']]
 for i in g.get('images',[]):i['bufferView']=viewmap[i['bufferView']]
 mats={p['material'] for m in g['meshes'] for p in m['primitives']};matmap={old:new for new,old in enumerate(sorted(mats))}
 for m in g['meshes']:
  for p in m['primitives']:p['material']=matmap[p['material']]
 g['materials']=[g['materials'][i] for i in sorted(mats)];g['accessors']=accessors;g['bufferViews']=newviews;g['buffers'][0]['byteLength']=len(newbin);assert before==signature(g,newbin),f
 js=json.dumps(g,separators=(',',':')).encode();js+=b' '*((-len(js))%4);newbin.extend(b'\0'*((-len(newbin))%4));out=struct.pack('<III',0x46546c67,2,28+len(js)+len(newbin))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(newbin),0x004e4942)+newbin;assert len(out)<=len(r),f;f.write_bytes(out);records.append(dict(path=f.relative_to(D).as_posix(),before=len(r),after=len(out),all_attribute_and_index_values_identical=True,geometry_simplified=False,compressed_or_quantized=False))
(P/'compact253.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf8');print('COMPACT253',len(records),'before',sum(x['before'] for x in records),'after',sum(x['after'] for x in records),'all geometry, UV, normal and color values identical')
