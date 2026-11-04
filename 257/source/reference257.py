import sys,json,hashlib,shutil
from pathlib import Path
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue252')
from common252 import *
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue248/deps313')
import OpenEXR
P=Path('E:/Ravedio-Avatar/catalogue257');D=P.parent/'floating138/mobile-preview/257';CAT=json.loads((D/'catalogue257.json').read_text());out=P/'reference-final';out.mkdir(exist_ok=True);records=[];assemblies={}
for build,style in [('Masculine','taper'),('Masculine','curly-top')]:
 key_style=build+'-'+style
 bpy.ops.wm.open_mainfile(filepath=str(P/'pass3/sources'/f'{build}-{style}-hair257.blend'));s=bpy.context.scene;frozen=protect(s);remove(['hair']);canonical=CAT['builds'][build]['hair'][style]['path'];path=canonical;imported(D/path,'hair');check(s,frozen);c.gpu();u.tone(s,1);u.camera(s,'front',512,False);s.camera.data.ortho_scale=1.65;s.cycles.samples=24;s.render.filepath='//'+build+'-reference257.png';bpy.ops.outliner.orphans_purge(do_recursive=True);bpy.ops.file.pack_all();src=P/'sources-final'/f'{key_style}-assembly257.blend';bpy.ops.wm.save_as_mainfile(filepath=str(src),compress=True);assemblies[key_style]=dict(source=str(src),packed_path='assemblies/'+src.name,packed=True,hair=path,canonical_hair=canonical,settings=u.settings(s),other_components_and_shared_coordinates_preserved=True)
 s.view_layers[0].use_pass_z=True;s.view_layers[0].pass_alpha_threshold=.5;s.render.use_compositing=True;g=bpy.data.node_groups.new('Matched ombre color and depth257','CompositorNodeTree');s.compositing_node_group=g;g.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor');layers=g.nodes.new('CompositorNodeRLayers');gout=g.nodes.new('NodeGroupOutput');g.links.new(layers.outputs['Image'],gout.inputs['Image']);node=g.nodes.new('CompositorNodeOutputFile');node.directory=str(out);node.file_output_items.clear();node.file_output_items.new('FLOAT','Depth');node.format.file_format='OPEN_EXR_MULTILAYER';node.format.color_depth='32';node.save_as_render=False;g.links.new(layers.outputs['Depth'],node.inputs['Depth'])
 cameras=[]
 for skin in [0,1,3]:
  u.tone(s,skin)
  for size in [120,512]:
   u.camera(s,'front',size,False);s.camera.data.ortho_scale=1.65;s.cycles.samples=24;key=f'{key_style}-skin{skin}-portrait{size}-paired257';node.file_name=key+'-depth';s.render.filepath=str(out/(key+'-color.png'));bpy.ops.render.render(write_still=True);depths=[f for f in out.rglob('*.exr') if f.name.startswith(key+'-depth')];assert len(depths)==1;depth=depths[0];values=next(iter(OpenEXR.File(str(depth)).channels().values())).pixels;assert values.shape==(size,size);finite=values[np.isfinite(values)&(values>0)&(values<1e8)];assert len(finite)>100;camera=u.settings(s)['camera'];cameras.append(camera['matrix_world']);records.append(dict(build=build,hair=style,skin=skin,size=size,color='references/'+key+'-color.png',depth='references/'+depth.name,camera=camera,geometry_revision=257,alpha_threshold=.5,finite_depth_range=[float(finite.min()),float(finite.max())]))
   for f in [out/(key+'-color.png'),depth]:shutil.copy2(f,D/'references'/f.name)
 assert all(x==cameras[0] for x in cameras);check(s,frozen);print('REFERENCE257',key_style,flush=True)
(P/'assemblies257.json').write_text(json.dumps(assemblies,indent=2)+'\n',encoding='utf8');(D/'depth257.json').write_text(json.dumps(dict(revision=257,pairs=records,definition='Same-render color and32-bit float linear Z; identical geometry, camera and version. Assembled reference, not a component occlusion bake or lens/alpha solution.'),indent=2)+'\n',encoding='utf8',newline='\n');print('REFERENCE257_COMPLETE',len(records),flush=True)
