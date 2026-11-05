import sys,json,shutil
from pathlib import Path
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue258')
from refine258 import *
P=Path('E:/Ravedio-Avatar/catalogue258');W=P/'pass4'
for d in [W/'sources',W/'components',W/'renders']:d.mkdir(parents=True,exist_ok=True)
out=json.loads((P/'pass2/hair258.json').read_text())
for style in ['taper','sidepart','curly-top']:
 bpy.ops.wm.open_mainfile(filepath=str(P/'pass2/sources'/f'Masculine-{style}-hair258.blend'));s=bpy.context.scene;frozen=protect(s)
 for ob in [o for o in s.objects if o.type=='MESH' and o.get('component159')=='hair']:
  if style=='taper' and 'Side part crown' in ob.name:
   inv=ob.matrix_world.inverted()
   for vertex in ob.data.vertices:
    point=ob.matrix_world@vertex.co;point.y-=.010;point.z-=.012;vertex.co=inv@point
  if style=='sidepart' and 'Recessed roots' in ob.name:
   m=ob.data.materials[0].copy();m.name='Hair258 / recessed roots';bs=m.node_tree.nodes['Principled BSDF'];col=bs.inputs['Base Color'].default_value;bs.inputs['Base Color'].default_value=(*[x*.8 for x in list(col)[:3]],1);bs.inputs['Roughness'].default_value=.44;bs.inputs['Coat Weight'].default_value=.03;m['hairShade258']=.8
   for link in list(m.node_tree.links):
    if link.to_node==bs and link.to_socket==bs.inputs['Normal']:m.node_tree.links.remove(link)
   ob.data.materials.clear();ob.data.materials.append(m)
 check(s,frozen);u.bake(s);source=W/'sources'/f'Masculine-{style}-hair258.blend';target=W/'components'/f'Masculine-{style}-hair258.glb';assert not source.exists() and not target.exists();bpy.ops.outliner.orphans_purge(do_recursive=True);bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True);ex.export(s,target,'hair');patch258(target,s);out[style].update(path=str(target),source=str(source),export_pass='Smooth rounded banks; lower rear bridge; separate recessed-root material');c.gpu()
 for angle in ['front','threequarter','profile','rightprofile','rear','rearquarter','top','underside']:
  u.camera(s,'rear' if angle=='rearquarter' else angle,512,False)
  if angle=='rearquarter':
   target_camera=Vector((0,0,1.88));s.camera.location=target_camera+Vector((-4,8,0));s.camera.rotation_euler=(target_camera-s.camera.location).to_track_quat('-Z','Y').to_euler()
  s.camera.data.ortho_scale=1.65;s.cycles.samples=24;s.render.filepath=str(W/'renders'/f'{style}-{angle}.png');floor=s.objects.get('Studio floor');hidden=floor.hide_render if floor else False
  if floor and angle=='underside':floor.hide_render=True
  try:bpy.ops.render.render(write_still=True)
  finally:
   if floor:floor.hide_render=hidden
 (W/'hair258.json').write_text(json.dumps(out,indent=2)+'\n');print('EXPORT258',style,flush=True)
shutil.copy2(__file__,W/'final258.py');(W/'settings.json').write_text(json.dumps(CFG,indent=2)+'\n');print('EXPORT258_COMPLETE3',flush=True)
