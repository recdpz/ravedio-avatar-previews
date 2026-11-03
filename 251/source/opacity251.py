from pathlib import Path
import json,struct,hashlib
P=Path(__file__).parent;D=P.parent/'floating138/mobile-preview/251';records=[]
for directory in [P/'components',D/'components']:
 for f in directory.glob('*.glb'):
  raw=f.read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);binary=raw[28+n:];changed=False;ids=[]
  for i,m in enumerate(g.get('materials',[])):
   if m.get('name','').startswith(('Hair / sculpted afro251','Hair / sculpted curly crown251')):
    assert m.get('pbrMetallicRoughness',{}).get('baseColorFactor',[1,1,1,1])[3]==1;ids.append(i);m['alphaMode']='OPAQUE';changed=True
  if not changed:continue
  for mesh in g['meshes']:
   for prim in mesh['primitives']:
    if prim['material'] not in ids:continue
    a=g['accessors'][prim['attributes']['COLOR_0']];view=g['bufferViews'][a['bufferView']];offset=view.get('byteOffset',0)+a.get('byteOffset',0)
    if a['type']=='VEC4':
     code,sz,full={5126:('f',4,1),5123:('H',2,65535),5121:('B',1,255)}[a['componentType']];stride=view.get('byteStride',sz*4);alpha=[struct.unpack_from('<'+code,binary,offset+i*stride+sz*3)[0]/full for i in range(a['count'])];assert min(alpha)==max(alpha)==1,(f,min(alpha),max(alpha))
    else:assert a['type']=='VEC3'
  text=json.dumps(g,separators=(',',':')).encode();text+=b' '*((-len(text))%4);f.write_bytes(struct.pack('<III',0x46546c67,2,28+len(text)+len(binary))+struct.pack('<II',len(text),0x4e4f534a)+text+struct.pack('<II',len(binary),0x004e4942)+binary);records.append(str(f));assert hashlib.sha256(binary).digest()==hashlib.sha256(raw[28+n:]).digest()
(P/'opacity251.json').write_text(json.dumps(dict(files=records,binary_buffers_unchanged=True,all_vertex_alpha=1,material_factor_alpha=1,mode='OPAQUE',reason='Prevent unnecessary transparency sorting of solid coiled hair'),indent=2)+'\n');print('OPAQUE_COILS251',len(records),'material metadata corrected')
