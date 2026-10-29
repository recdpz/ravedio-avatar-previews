"""Make constant pigment in beard density PNGs recolorable; retain alpha exactly."""
from pathlib import Path
import json,struct,io,hashlib
from PIL import Image
P=Path(__file__).parent;R=P.parent/'floating138/mobile-preview';cat=json.loads((R/'234/catalogue234.json').read_text());records={}
def linear(c):
 c=c/255;return c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4
for style,item in cat['builds']['Masculine']['grooms'].items():
 if not item['path']:continue
 source=(R/'234'/item['path']).resolve();raw=source.read_bytes();n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n]);binary=bytearray(raw[28+n:]);changes=[];images={}
 for mat in doc['materials']:
  pbr=mat.get('pbrMetallicRoughness',{});tex=pbr.get('baseColorTexture')
  if not tex:continue
  image_id=doc['textures'][tex['index']]['source'];iminfo=doc['images'][image_id];view=doc['bufferViews'][iminfo['bufferView']];image=Image.open(io.BytesIO(binary[view.get('byteOffset',0):view.get('byteOffset',0)+view['byteLength']])).convert('RGBA');ext=image.getextrema();assert all(a==b for a,b in ext[:3]),(style,'Pigment not constant',ext)
  rgb=[x[0] for x in ext[:3]];base=pbr.get('baseColorFactor',[1,1,1,1]);pbr['baseColorFactor']=[base[i]*linear(rgb[i]) for i in range(3)]+[base[3]]
  if image_id not in images:
   alpha=image.getchannel('A');white=Image.new('RGBA',image.size,(255,255,255,255));white.putalpha(alpha);buf=io.BytesIO();white.save(buf,format='PNG');data=buf.getvalue();binary.extend(b'\0'*((-len(binary))%4));off=len(binary);binary.extend(data);idx=len(doc['bufferViews']);doc['bufferViews'].append(dict(buffer=0,byteOffset=off,byteLength=len(data)));iminfo['bufferView']=idx;images[image_id]=True
  changes.append(dict(material=mat['name'],original_rgb=rgb,alpha_exact=True,new_base_factor=pbr['baseColorFactor']))
 doc['buffers'][0]['byteLength']=len(binary);text=json.dumps(doc,separators=(',',':')).encode();text+=b' '*((-len(text))%4);binary+=b'\0'*((-len(binary))%4);out=P/'components'/f'Masculine-groom-{style}.glb';out.write_bytes(struct.pack('<III',0x46546c67,2,28+len(text)+len(binary))+struct.pack('<II',len(text),0x4e4f534a)+text+struct.pack('<II',len(binary),0x004e4942)+binary)
 records[style]=dict(path='components/'+out.name,source=str(source),source_sha256=hashlib.sha256(raw).hexdigest(),changes=changes,geometry_and_alpha_unchanged=True)
(P/'groom235.json').write_text(json.dumps(records,indent=2)+'\n');print('GROOM235',len(records))
