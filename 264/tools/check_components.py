import json
from pathlib import Path
import numpy as np
from verify_assets import glb,array,D
rows=json.loads((D/'components.json').read_text(encoding='utf8'));results=[]
for row in rows:
 g,b=glb(D/'assets'/f"{row['build']}-optimized264.glb");q,c=glb(D/row['file'])
 source={n['name']:n for n in g['nodes']if 'mesh'in n};count=0
 for node in q['nodes']:
  if 'mesh'not in node:continue
  n=source[node['name']];assert {k:v for k,v in node.items()if k!='mesh'}=={k:v for k,v in n.items()if k!='mesh'}
  for p,z in zip(g['meshes'][n['mesh']]['primitives'],q['meshes'][node['mesh']]['primitives']):
   assert g['materials'][p['material']]==q['materials'][z['material']]
   for key,i in p['attributes'].items():assert np.array_equal(array(g,b,i),array(q,c,z['attributes'][key]))
   assert np.array_equal(array(g,b,p['indices']),array(q,c,z['indices']));count+=g['accessors'][p['indices']]['count']//3
 assert count==row['triangles'];results.append(dict(file=row['file'],triangles=count,attributes_and_transforms_exact=True))
for build in ['Feminine','Masculine']:
 g,b=glb(D/'assets'/f'{build}-optimized264.glb');assert sum(r['triangles']for r in rows if r['build']==build)==sum(g['accessors'][p['indices']]['count']//3 for m in g['meshes']for p in m['primitives'])
(D/'verification/components.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf8');print('COMPONENT_REASSEMBLY264_COMPLETE',len(results))
