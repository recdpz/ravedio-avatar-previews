from pathlib import Path
import json,struct,numpy as np
P=Path(__file__).parent;R=P.parent/'floating138/mobile-preview';D=R/'250';old=json.loads((R/'249/catalogue249.json').read_text());new=json.loads((D/'catalogue250.json').read_text());rows=[]
def positions(f,kind):
 raw=f.read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);binary=raw[28+n:];ps=[]
 assert all(not any(k in node for k in ['matrix','translation','rotation','scale']) for node in g.get('nodes',[]))
 for m in g['meshes']:
  for p in m['primitives']:
   a=g['accessors'][p['attributes']['POSITION']];v=g['bufferViews'][a['bufferView']];arr=np.ndarray((a['count'],3),dtype='<f4',buffer=binary,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',12),4));mask=(arr[:,2]>.255)&(arr[:,1]<1.62) if kind=='cloth' else arr[:,2]>=.25;ps.extend(map(tuple,np.round(arr[mask],5)))
 return set(ps)
for b,bc in new['builds'].items():
 for style in bc['hair']:
  a=positions((R/'249'/old['fits'][b+'-'+style]['pashmina']['hair']).resolve(),'hair');z=positions((D/new['fits'][b+'-'+style]['pashmina']['hair']).resolve(),'hair');assert a==z,(b,style,'exposed hair changed',len(a-z),len(z-a));rows.append(dict(build=b,style=style,kind='visible front hair',points=len(a),unchanged=True))
  for top in bc['tops']:
   a=positions((R/'249'/old['pashminaVariants'][b][style][top]).resolve(),'cloth');z=positions((D/new['pashminaVariants'][b][style][top]).resolve(),'cloth');assert a==z,(b,style,top,'accepted crossing changed',len(a-z),len(z-a));rows.append(dict(build=b,style=style,top=top,kind='accepted front crossing',points=len(a),unchanged=True))
(P/'boundary250.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf8');print('BOUNDARY250',len(rows),'front hair/crossing boundaries preserved')
