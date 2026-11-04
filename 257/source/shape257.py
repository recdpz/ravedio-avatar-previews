import bpy,json,hashlib
import numpy as np
from pathlib import Path
P=Path(__file__).parent
def capture(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));return {o.name:np.array([tuple(o.matrix_world@v.co) for v in o.data.vertices]) for o in bpy.context.scene.objects if o.type=='MESH' and o.get('component159')=='hair' and len(o.data.vertices)==2530}
before=capture(P.parent/'catalogue256/pass2/sources/Masculine-taper-hair256.blend');after=capture(P/'pass3/sources/Masculine-taper-hair257.blend');assert before.keys()==after.keys();rows=[]
for name,a in before.items():
 b=after[name];mask=np.array([(0 if i==0 else 80 if i==2529 else (i-1)//32+1)/80<=.70 for i in range(2530)]);delta=np.linalg.norm(a-b,axis=1);assert np.max(delta[mask])<1e-7,(name,np.max(delta[mask]));rows.append(dict(name=name,protected_upper_vertices=int(mask.sum()),upper_positions_exact=True,terminal_vertices_changed=int((delta>1e-7).sum()),max_terminal_shift=float(delta.max())))
(P/'shape257.json').write_text(json.dumps(dict(basis=256,upper_B_shape_preserved=True,tip_start=.70,locks=rows),indent=2)+'\n');print('UPPER_B_SHAPE257_COMPLETE',len(rows),flush=True)
