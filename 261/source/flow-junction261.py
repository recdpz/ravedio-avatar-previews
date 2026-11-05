import sys,json
from pathlib import Path
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue261');from repair261 import *
P=Path('E:/Ravedio-Avatar/catalogue261');sel=json.loads((P/'selected261.json').read_text());row=sel['Masculine-flow'];bpy.ops.wm.open_mainfile(filepath=row['source']);s=bpy.context.scene;frozen=protect(s);c.reset_head(s)
mat=next(o for o in s.objects if o.type=='MESH' and o.get('component159')=='hair' and 'Flow260 layered' in o.name).data.materials[0]
ps=[]
for t in np.linspace(0,1,80):
 y=-.27+.55*t;p=c.surf(.13*(1-.35*smooth((y+.05)/.34)),y,.035+.028*sin(pi*t));ps.append(p)
ob=old.lock('Flow261 buried crown junction',ps,[.018,.041,.043,.034,.015],[.013,.023,.026,.021,.009],mat=mat,n=80,sides=32,grain=.0012)
for uv in ob.data.uv_layers.active.data:uv.uv.y=1-uv.uv.y
check(s,frozen);u.bake(s);W=P/'pass3';(W/'sources').mkdir(parents=True,exist_ok=True);(W/'components').mkdir(exist_ok=True);src=W/'sources/Masculine-flow-hair261.blend';out=W/'components/Masculine-flow-hair261.glb';bpy.ops.outliner.orphans_purge(do_recursive=True);bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(src),compress=True);ex.export(s,out,'hair');prev258.patch258(out,s);row.update(source=str(src),path=str(out),buried_crown_junction=True);(P/'selected261.json').write_text(json.dumps(sel,indent=2));print('FLOW_JUNCTION261_COMPLETE')
