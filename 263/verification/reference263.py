import sys,json,shutil,math
from pathlib import Path
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue262')
from common262 import *
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue248/deps313');import OpenEXR
P=Path('E:/Ravedio-Avatar/catalogue263');D=R/'263';N=json.loads((D/'catalogue263.json').read_text());out=P/'reference';out.mkdir(exist_ok=True);records=[];assemblies={}
for build,hair,glasses in [('Feminine','ponytail','reading'),('Masculine','taper','rectangular')]:
 s=load262(build,'sweatshirt','pants',hair)
 for o in list(s.objects):
  if o.get('component159') in ['base','hair','top']:u.delete(o)
 bc=N['builds'][build];paths={'base':bc['pantsBases']['clothed'],'top':bc['tops']['sweatshirt']['path'],'hair':N['fits'][build+'-'+hair]['cap']['hair'],'headgear':N['fits'][build+'-'+hair]['cap']['headgear'],'extra':bc['hot']}
 paths.update(bc['rectangular'] if glasses=='rectangular' else {'glasses':N['glasses'][glasses]['path'],'lenses':N['glasses'][glasses]['lenses']})
 for group,path in paths.items():imported((D/path).resolve(),group)

 # Select the same black-frame control as the browser, while preserving separate source lenses.
 frame_hex=next(r[2] for r in N['colors']['frames'] if r[0]=='black').lstrip('#')
 frame_rgb=[int(frame_hex[i:i+2],16)/255 for i in [0,2,4]]
 frame_linear=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in frame_rgb]
 for ob in s.objects:
  if ob.type!='MESH' or ob.get('component159')!='glasses':continue
  for mat in ob.data.materials:
   if mat and mat.use_nodes:
    bs=mat.node_tree.nodes.get('Principled BSDF')
    if bs:bs.inputs['Base Color'].default_value=(*frame_linear,1);bs.inputs['Metallic'].default_value=.08;bs.inputs['Roughness'].default_value=.28
 u.tone(s,1);a.setup();c.reset_head(s);c.gpu();u.camera(s,'front',512,False);s.camera.data.ortho_scale=1.65;s.cycles.samples=24;u.bake(s);key=build+'-hoodie-pants-cap';s['revision263']=True;s['fixture263']=key;s['settings263']=json.dumps({'build':build,'hair':hair,'top':'sweatshirt','bottom':'pants','headwear':'cap','eyes':'original','nose':'none','mouth':'line','glasses':glasses,'detail':'hot','groom':'none','frameColor':'black','lensTint':'clear' if glasses=='reading' else 'dark','skin':1,'colors':'authored originals'})
 bpy.ops.outliner.orphans_purge(do_recursive=True);bpy.ops.file.pack_all();src=D/'assemblies'/(key+'263.blend');bpy.ops.wm.save_as_mainfile(filepath=str(src),compress=True);u.export(s,D/'assemblies'/(key+'263.glb'))
 assemblies[key]={'source':'assemblies/'+src.name,'glb':'assemblies/'+key+'263.glb','selection':json.loads(s['settings263']),'components':paths,'settings':u.settings(s),'requirements':u.requirements(s),'packed':True,'coordinates':'Shared source world coordinates; no per-component centering/resizing','lens_note':'Actual source lens material. Transmission remains separate from alpha. Browser uses a sharp alpha approximation; native transparency still requires qualification.'}
 s.view_layers[0].use_pass_z=True;s.view_layers[0].pass_alpha_threshold=.5;s.render.use_compositing=True;g=bpy.data.node_groups.new('Matched color and depth263','CompositorNodeTree');s.compositing_node_group=g;g.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor');layers=g.nodes.new('CompositorNodeRLayers');gout=g.nodes.new('NodeGroupOutput');g.links.new(layers.outputs['Image'],gout.inputs['Image']);node=g.nodes.new('CompositorNodeOutputFile');node.directory=str(out);node.file_output_items.clear();node.file_output_items.new('FLOAT','Depth');node.format.file_format='OPEN_EXR_MULTILAYER';node.format.color_depth='32';node.save_as_render=False;g.links.new(layers.outputs['Depth'],node.inputs['Depth'])
 for preset,sizes,span,target in [('reference',[120,512],1.65,1.88),('chat',[32,48,64,120],1.35,1.90)]:
  for skin in [0,3]:
   u.tone(s,skin)
   for size in sizes:
    u.camera(s,'front',size,False);s.camera.data.ortho_scale=span;s.camera.location.z+=target-1.88;s.cycles.samples=24;name=f'{key}-{preset}-skin{skin}-{size}-paired263';node.file_name=name+'-depth';s.render.filepath=str(out/(name+'-color.png'));bpy.ops.render.render(write_still=True);depths=[f for f in out.rglob('*.exr') if f.name.startswith(name+'-depth')];assert len(depths)==1;depth=depths[0];values=next(iter(OpenEXR.File(str(depth)).channels().values())).pixels;assert values.shape==(size,size);finite=values[np.isfinite(values)&(values>0)&(values<1e8)];assert len(finite)>100;camera=u.settings(s)['camera'];camera['portrait_target']=[0,0,target];camera['preset']=preset;records.append(dict(build=build,fixture=key,skin=skin,size=size,preset=preset,color='references/'+name+'-color.png',depth='references/'+depth.name,camera=camera,geometry_revision=263,alpha_threshold=.5,finite_depth_range=[float(finite.min()),float(finite.max())]));shutil.copy2(out/(name+'-color.png'),D/'references'/(name+'-color.png'));shutil.copy2(depth,D/'references'/depth.name)
 print('REFERENCE263',key,flush=True)
(D/'assemblies263.json').write_text(json.dumps(assemblies,indent=2)+'\n',encoding='utf8');(D/'depth263.json').write_text(json.dumps({'revision':263,'pairs':records,'definition':'Matched color and32-bit linear Z from final actual GLBs. Same geometry/camera/version per pair. Depth describes the nearest surface, not transmitted/refracted light; lens qualification remains separate.'},indent=2)+'\n',encoding='utf8');print('REFERENCE263_COMPLETE',len(records),flush=True)
