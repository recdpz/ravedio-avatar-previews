import sys,json,math
from pathlib import Path
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue261');from repair261 import *
P=Path('E:/Ravedio-Avatar/catalogue261');sel=json.loads((P/'selected261.json').read_text());row=sel['Feminine-curls'];bpy.ops.wm.open_mainfile(filepath=row['source']);s=bpy.context.scene;frozen=protect(s);c.reset_head(s);ob=next(o for o in s.objects if o.get('component159')=='hair' and 'continuous recessed' in o.name);nu,nv=256,64;inv=ob.matrix_world.inverted()
for j in range(nu):
 ph=2*pi*j/nu;d=(ob.matrix_world@ob.data.vertices[1+(nv-1)*nu+j].co-a.C);q=Vector((d.x/.48,d.y/.405,d.z/.455));th=math.acos(max(-1,min(1,q.normalized().z)));ang=abs((ph+pi)%(2*pi)-pi);end=min(th,.70+1.02*smooth((ang-.62)/1.0))
 for i in range(1,nv+1):
  N=surface_dir(i/nv*end,ph);hit=c.HEAD.ray_cast(a.C,N,2)[0];ob.data.vertices[1+(i-1)*nu+j].co=inv@(hit+N*.0025)
clean_normals(ob);check(s,frozen);u.bake(s);W=P/'pass4';(W/'sources').mkdir(parents=True,exist_ok=True);(W/'components').mkdir(exist_ok=True);src=W/'sources/Feminine-curls-hair261.blend';out=W/'components/Feminine-curls-hair261.glb';bpy.ops.outliner.orphans_purge(do_recursive=True);bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(src),compress=True);ex.export(s,out,'hair');prev258.patch258(out,s);row.update(source=str(src),path=str(out),front_support_stops_beneath_first_curl_bank=True);(P/'selected261.json').write_text(json.dumps(sel,indent=2));print('CURL_COVERAGE261_COMPLETE')
