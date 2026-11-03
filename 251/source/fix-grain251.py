from pathlib import Path
import json,struct,hashlib
P=Path(__file__).parent;D=P.parent/'floating138/mobile-preview/251';fixed=[]
for parent in [P/'components',D/'components']:
 for f in parent.glob('*.glb'):
  if f.name.startswith('Highlights-'):continue
  raw=f.read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);changed=False
  for mat in g.get('materials',[]):
   pbr=mat.get('pbrMetallicRoughness',{})
   if mat.get('name','').startswith('Hair / clipped grain251') and 'baseColorTexture' in pbr:
    factor=pbr.get('baseColorFactor',[1,1,1,1]);pbr['baseColorFactor']=[.095,.037,.019,factor[3]];changed=True
  if changed:
   doc=json.dumps(g,separators=(',',':')).encode();doc+=b' '*((-len(doc))%4);binary=raw[28+n:];out=struct.pack('<III',0x46546c67,2,28+len(doc)+len(binary))+struct.pack('<II',len(doc),0x4e4f534a)+doc+struct.pack('<II',len(binary),0x004e4942)+binary;f.write_bytes(out);fixed.append(str(f));assert hashlib.sha256(raw[28+n:]).digest()==hashlib.sha256(binary).digest()
q=json.loads((P/'proof251.json').read_text())
q={k:v for k,v in q.items() if not any(k.startswith('Masculine-'+style+'-') for style in ['taper','buzz','curly-top'])};(P/'proof251.json').write_text(json.dumps(q,indent=2));(P/'grain-tint251.json').write_text(json.dumps(dict(files=fixed,binary_buffers_unchanged=True,fix='Explicit PBR multiplier for exported neutral grain texture'),indent=2));print('GRAIN_TINT251',len(fixed),'material-only corrections')
