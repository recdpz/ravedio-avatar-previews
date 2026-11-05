"""Matched assembly color/Z references; not a native component-layer bake."""
import sys,json,hashlib,shutil
from pathlib import Path
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue235')
import common235 as c
c.P=Path(__file__).parent
from common235 import *
sys.path.insert(0,str(P/'deps313'))
import OpenEXR
D=R/'248';out=P/'depth';out.mkdir(exist_ok=True);records=[]
for build in ['Feminine','Masculine']:
 bpy.ops.wm.open_mainfile(filepath=str(P/'sources'/f'{build}-pashmina-assembly248.blend'));s=bpy.context.scene
 s.view_layers[0].use_pass_z=True;s.view_layers[0].pass_alpha_threshold=.5;s.render.use_compositing=True
 g=bpy.data.node_groups.new('Matched color and physical depth248','CompositorNodeTree');s.compositing_node_group=g
 g.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor');layers=g.nodes.new('CompositorNodeRLayers');groupout=g.nodes.new('NodeGroupOutput');g.links.new(layers.outputs['Image'],groupout.inputs['Image'])
 node=g.nodes.new('CompositorNodeOutputFile');node.directory=str(out);node.file_output_items.clear();node.file_output_items.new('FLOAT','Depth');node.format.file_format='OPEN_EXR_MULTILAYER';node.format.color_depth='32';node.save_as_render=False;g.links.new(layers.outputs['Depth'],node.inputs['Depth'])
 for size in [120,512]:
  u.camera(s,'front',size,False);s.cycles.samples=32;key=f'{build}-portrait{size}-paired248';node.file_name=key+'-depth';s.render.filepath=str(out/(key+'-color.png'));before=set(out.glob('*.exr'));bpy.ops.render.render(write_still=True)
  files=[f for f in out.rglob('*.exr') if f.name.startswith(key+'-depth')];assert len(files)==1,files;depth=files[0];exr=OpenEXR.File(str(depth));channels=exr.channels();assert len(channels)==1
  values=next(iter(channels.values())).pixels;assert values.shape==(size,size),values.shape;finite=values[np.isfinite(values)&(values>0)&(values<1e8)];assert len(finite)>100
  item=dict(build=build,size=size,color='references/'+key+'-color.png',depth='references/'+depth.name,format='32-bit float OpenEXR Z pass; linear scene-distance units',camera=u.settings(s)['camera'],alpha_threshold=.5,finite_depth_range=[float(finite.min()),float(finite.max())],geometry_revision=248,interpretation='Assembled Blender reference only. Not a component-layer occlusion map and not a transparency solution.')
  for f in [out/(key+'-color.png'),depth]:shutil.copy2(f,D/'references'/f.name)
  records.append(item)
record=dict(revision=248,matched_color_and_depth=records,source='Same render, geometry, camera and version for every color/depth pair.',validation_dependency='OpenEXR3.5.2 Python reader; isolated local deps directory, not bundled into the app.',limits='No glasses in these fixtures. Opacity uses Blender pass alpha threshold0.5; transmission/refraction and native component composition require separate tests.')
(P/'depth248.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf8');(D/'depth248.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf8')
print('DEPTH248 four matched assembly color/Z pairs validated',flush=True)
