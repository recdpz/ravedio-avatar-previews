import sys,json,math
from pathlib import Path
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue261');from repair261 import *
P=Path('E:/Ravedio-Avatar/catalogue261');sel=json.loads((P/'selected261.json').read_text());W=P/'pass5';(W/'sources').mkdir(parents=True,exist_ok=True);(W/'components').mkdir(exist_ok=True)
for key in ['Feminine-bob','Feminine-straight','Feminine-side-sweep','Feminine-curls']:
 row=sel[key];bpy.ops.wm.open_mainfile(filepath=row['source']);s=bpy.context.scene;frozen=protect(s);c.reset_head(s);ob=next(o for o in s.objects if o.get('component159')=='hair' and 'continuous recessed' in o.name);nu,nv=256,64;inv=ob.matrix_world.inverted();maximum=2.38 if key=='Feminine-bob' else 2.66
 for j in range(nu):
  ph=2*pi*j/nu;ang=abs((ph+pi)%(2*pi)-pi)
  if ang<=1.52:continue
  d=ob.matrix_world@ob.data.vertices[1+(nv-1)*nu+j].co-a.C;q=Vector((d.x/.48,d.y/.405,d.z/.455));th=math.acos(max(-1,min(1,q.normalized().z)));end=max(th,1.72+(maximum-1.72)*smooth((ang-1.52)/.75))
  for i in range(1,nv+1):
   theta=i/nv*end;N=surface_dir(theta,ph);hit=c.HEAD.ray_cast(a.C,N,2)[0];relief=.0015*(.5+.5*cos(ph*22+.2*sin(theta*6)))*smooth((theta-1.3)/.5)*smooth((ang-1.52)/.45);ob.data.vertices[1+(i-1)*nu+j].co=inv@(hit+N*(.0025+relief))
 clean_normals(ob);check(s,frozen);u.bake(s);src=W/'sources'/f'{key}-hair261.blend';out=W/'components'/f'{key}-hair261.glb';bpy.ops.outliner.orphans_purge(do_recursive=True);bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(src),compress=True);ex.export(s,out,'hair');prev258.patch258(out,s);row.update(source=str(src),path=str(out),rear_coverage_extended_beneath_locks=True,main_lock_positions_retained_from_previous_pass=True);print('REAR_COVERAGE261',key,flush=True)
(P/'selected261.json').write_text(json.dumps(sel,indent=2));print('REAR_COVERAGE261_COMPLETE')
