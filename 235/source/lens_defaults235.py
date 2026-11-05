from pathlib import Path
import struct,json
P=Path(__file__).parent
def linear(v):v=v/255;return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
for path in (P/'components').glob('*-lenses.glb'):
 if '--' in path.name:continue
 raw=path.read_bytes();n=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+n]);reading='-reading-' in path.name
 for m in d['materials']:
  p=m['pbrMetallicRoughness'];p['baseColorFactor']=[linear(x) for x in ([220,233,235] if reading else [28,32,41])]+[.075 if reading else .84];m['alphaMode']='BLEND';m.setdefault('extensions',{}).pop('KHR_materials_transmission',None)
 text=json.dumps(d,separators=(',',':')).encode();text+=b' '*((-len(text))%4);binary=raw[28+n:];path.write_bytes(struct.pack('<III',0x46546c67,2,28+len(text)+len(binary))+struct.pack('<II',len(text),0x4e4f534a)+text+struct.pack('<II',len(binary),0x004e4942)+binary)
print('Lens asset defaults: Reading clear, all other styles dark')
