import sys,json,shutil,math
from pathlib import Path
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue252')
from common252 import *
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue248/deps313')
import OpenEXR,numpy as np
P=Path('E:/Ravedio-Avatar/catalogue258');D=P.parent/'floating138/mobile-preview/258';CAT=json.loads((D/'catalogue258.json').read_text());out=P/'reference-final';out.mkdir(exist_ok=True);records=[];assemblies={};neutral=((48/255+.055)/1.055)**2.4

def black(s):
 materials=set()
 for ob in [o for o in s.objects if o.type=='MESH' and o.get('component159')=='hair']:
  if ob.data.color_attributes:
   attr=ob.data.color_attributes.active_color or ob.data.color_attributes[0];ar=np.array([list(c.color) for c in attr.data]);l=ar[:,:3]@np.array([.2126,.7152,.0722]);shade=np.clip(np.sqrt(l/max(.001,l.mean())),.70,1.18);ar[:,:3]=shade[:,None];attr.data.foreach_set('color',ar.astype('f').ravel())
  for m in ob.data.materials:
   if m in materials:continue
   materials.add(m);bs=m.node_tree.nodes.get('Principled BSDF');factor=m.get('hairShade258',.88 if 'directional fade' in m.name else .8 if 'recessed roots' in m.name else 1)
   for link in list(m.node_tree.links):
    if link.to_node==bs and link.to_socket==bs.inputs['Base Color']:m.node_tree.links.remove(link)
   color=(neutral*factor,)*3+(1,)
   if ob.data.color_attributes:
    vc=m.node_tree.nodes.new('ShaderNodeVertexColor');mix=m.node_tree.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[2].default_value=color;m.node_tree.links.new(vc.outputs['Color'],mix.inputs[1]);m.node_tree.links.new(mix.outputs[0],bs.inputs['Base Color'])
   else:bs.inputs['Base Color'].default_value=color

for style in ['taper','sidepart','curly-top']:
 build='Masculine';key_style=build+'-'+style;bpy.ops.wm.open_mainfile(filepath=str(P/'pass4/sources'/f'{key_style}-hair258.blend'));s=bpy.context.scene;frozen=protect(s);remove(['hair']);path=CAT['builds'][build]['hair'][style]['path'];imported(D/path,'hair');check(s,frozen);c.gpu();u.tone(s,1);u.camera(s,'front',512,False);s.camera.data.ortho_scale=1.65;s.cycles.samples=24;bpy.ops.outliner.orphans_purge(do_recursive=True);bpy.ops.file.pack_all();src=P/'sources-final'/f'{key_style}-assembly258.blend';assert not src.exists();bpy.ops.wm.save_as_mainfile(filepath=str(src),compress=True);assemblies[key_style]=dict(source=str(src),packed_path='assemblies/'+src.name,packed=True,hair=path,settings=u.settings(s),black_preset=dict(srgb='#303030',linear_rgb=[neutral]*3,method='Normalize vertex RGB shading; retain alpha; multiply the neutral pigment by hairShade258'),other_components_and_shared_coordinates_preserved=True)
 s.view_layers[0].use_pass_z=True;s.view_layers[0].pass_alpha_threshold=.5;s.render.use_compositing=True;g=bpy.data.node_groups.new('Matched color and depth258','CompositorNodeTree');s.compositing_node_group=g;g.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor');layers=g.nodes.new('CompositorNodeRLayers');gout=g.nodes.new('NodeGroupOutput');g.links.new(layers.outputs['Image'],gout.inputs['Image']);node=g.nodes.new('CompositorNodeOutputFile');node.directory=str(out);node.file_output_items.clear();node.file_output_items.new('FLOAT','Depth');node.format.file_format='OPEN_EXR_MULTILAYER';node.format.color_depth='32';node.save_as_render=False;g.links.new(layers.outputs['Depth'],node.inputs['Depth']);cameras=[]
 for color in ['default','black']:
  if color=='black':black(s)
  for skin in ([0,1,3] if color=='default' else [0,3]):
   u.tone(s,skin)
   for size in [120,512]:
    u.camera(s,'front',size,False);s.camera.data.ortho_scale=1.65;s.cycles.samples=24;key=f'{key_style}-{color}-skin{skin}-portrait{size}-paired258';node.file_name=key+'-depth';s.render.filepath=str(out/(key+'-color.png'));bpy.ops.render.render(write_still=True);depths=[f for f in out.rglob('*.exr') if f.name.startswith(key+'-depth')];assert len(depths)==1;depth=depths[0];values=next(iter(OpenEXR.File(str(depth)).channels().values())).pixels;assert values.shape==(size,size);finite=values[np.isfinite(values)&(values>0)&(values<1e8)];assert len(finite)>100;camera=u.settings(s)['camera'];cameras.append(camera['matrix_world']);records.append(dict(build=build,hair=style,hair_color=color,skin=skin,size=size,color='references/'+key+'-color.png',depth='references/'+depth.name,camera=camera,geometry_revision=258,alpha_threshold=.5,finite_depth_range=[float(finite.min()),float(finite.max())]));shutil.copy2(out/(key+'-color.png'),D/'references'/(key+'-color.png'));shutil.copy2(depth,D/'references'/depth.name)
 assert all(x==cameras[0] for x in cameras);check(s,frozen);print('REFERENCE258',style,flush=True)
(P/'assemblies258.json').write_text(json.dumps(assemblies,indent=2)+'\n');(D/'depth258.json').write_text(json.dumps(dict(revision=258,pairs=records,definition='Matched color/32-bit linear Z; identical geometry, camera and version. Alpha threshold0.5; assembled references, not a complete alpha-occlusion compositing solution.'),indent=2)+'\n',encoding='utf8',newline='\n');print('REFERENCE258_COMPLETE',len(records),flush=True)
