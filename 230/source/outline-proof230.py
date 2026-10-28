import bpy,sys,json
from pathlib import Path
P=Path(__file__).parent
proof={}
for build in ['Feminine','Masculine']:
 data=[]
 for rev in [228,230]:
  bpy.ops.wm.open_mainfile(filepath=str(P.parent/f'refinement{rev}/output/sources/{build}-soft-squint.blend'))
  eyes=sorted([o for o in bpy.context.scene.objects if o.name.startswith('Eye / soft squint')],key=lambda o:o.name)
  data.append([[tuple(o.matrix_world@v.co) for v in o.data.vertices] for o in eyes])
 assert len(data[0])==len(data[1])==2
 delta=0
 for before,after in zip(*data):
  assert len(before)==len(after)
  delta=max(delta,max(max(abs(a[0]-b[0]),abs(a[2]-b[2])) for a,b in zip(before,after)))
 assert delta==0
 proof[build]={'front_outline_and_spacing_exact':True,'max_x_z_delta':delta,'depth_change':'Only rounded eye dome; outline preserved'}
(P/'output/outline-proof230.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf8')
