"""Blender 5.2: reproduce packed-source, source-GLB and optimized references.
Run: blender --background --python tools/render_blender.py -- [Feminine|Masculine]
Uses only files in this package. No external source checkout or add-ons.
"""
import bpy, json, math, sys, hashlib
from pathlib import Path
from mathutils import Vector
D=Path(__file__).resolve().parent.parent
palette=json.loads((D/'palette.json').read_text(encoding='utf8'))
builds=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['Feminine','Masculine']
angles=dict(front=(0,0),threequarter=(-.464,0),profile=(-math.pi/2,0),rightprofile=(math.pi/2,0),rear=(math.pi,0),rearquarter=(-2.498,0),top=(0,1.07),underside=(0,-1.05))
def tone(s,index):
 for m in bpy.data.materials:
  if not m.use_nodes:continue
  bs=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
  if not bs:continue
  name=m.name;k='skin' if name.startswith('Skin') else 'ink' if name.startswith('Face / ink209') else 'lip' if name.startswith('Face / lip209') else None
  if k:bs.inputs['Base Color'].default_value=(*palette[k][index],1)
  if name.startswith('Chest / shade191'):
   try:f=float(name.split(' ')[-1]);bs.inputs['Base Color'].default_value=(*[x*f for x in palette['skin'][index]],1)
   except ValueError:pass
def camera(s,angle,size,span,target):
 yaw,pitch=angles[angle];s.camera.data.type='ORTHO';s.camera.data.ortho_scale=span
 s.camera.location=(8*math.sin(yaw)*math.cos(pitch),-8*math.cos(yaw)*math.cos(pitch),target+8*math.sin(pitch))
 s.camera.rotation_euler=(Vector((0,0,target))-s.camera.location).to_track_quat('-Z','Y').to_euler()
 s.render.resolution_x=s.render.resolution_y=size;s.render.resolution_percentage=100
 bpy.context.view_layer.update()
 return dict(matrix_world=[list(row)for row in s.camera.matrix_world],ortho_scale=span,target=[0,0,target],angle=angle,size=size,clip_start=s.camera.data.clip_start,clip_end=s.camera.data.clip_end)
def setup(s):
 s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.seed=42;s.cycles.use_denoising=True
 try:
  p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='CUDA';p.get_devices()
  for dev in p.devices:dev.use=dev.type=='CUDA'
  s.cycles.device='GPU' if any(dev.type=='CUDA'for dev in p.devices) else 'CPU'
 except Exception:s.cycles.device='CPU'
 s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8'
 s.view_layers[0].use_pass_z=True;s.view_layers[0].pass_alpha_threshold=.5;s.render.use_compositing=True
 g=bpy.data.node_groups.new('Paired color and Z264','CompositorNodeTree');s.compositing_node_group=g;g.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor')
 layers=g.nodes.new('CompositorNodeRLayers');out=g.nodes.new('NodeGroupOutput');g.links.new(layers.outputs['Image'],out.inputs['Image'])
 node=g.nodes.new('CompositorNodeOutputFile');node.directory=str(D/'references');node.file_output_items.clear();node.file_output_items.new('FLOAT','Depth');node.format.file_format='OPEN_EXR_MULTILAYER';node.format.color_depth='32';node.save_as_render=False;g.links.new(layers.outputs['Depth'],node.inputs['Depth']);return node
for build in builds:
 records=[]
 for variant in ['artwork','source-glb','optimized']:
  bpy.ops.wm.open_mainfile(filepath=str(D/'sources'/f'{build}-hoodie-pants-cap263.blend'));s=bpy.context.scene
  if variant!='artwork':
   for o in list(s.objects):
    if o.type in ['MESH','CURVE'] and o.name!='Studio floor':bpy.data.objects.remove(o,do_unlink=True)
   file=D/('sources' if variant=='source-glb' else 'assets')/(f'{build}-hoodie-pants-cap263.glb' if variant=='source-glb' else f'{build}-optimized264.glb')
   bpy.ops.import_scene.gltf(filepath=str(file))
   source_hash=hashlib.sha256(file.read_bytes()).hexdigest()
  else:source_hash=hashlib.sha256((D/'sources'/f'{build}-hoodie-pants-cap263.blend').read_bytes()).hexdigest()
  node=setup(s);tone(s,1);camera(s,'front',512,1.65,1.88)
  if variant=='optimized':
   s['derivative264']='Attribute-aware meshoptimizer; source263, pass2; shared coordinates, original material roles.'
   node.directory='//../references';s.render.filepath='//../references/render.png'
   bpy.ops.outliner.orphans_purge(do_recursive=True);bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(D/'assets'/f'{build}-optimized264.blend'),compress=True);node.directory=str(D/'references')
  cases=[('reference','front',skin,size,1.65,1.88)for skin in [0,3]for size in [120,512]]
  if variant!='artwork':cases += [('angles',angle,1,512,2.7,1.28)for angle in angles]
  if variant=='optimized':cases += [('chat','front',skin,size,1.35,1.90)for skin in [0,3]for size in [32,48,64,120]]
  for preset,angle,skin,size,span,target in cases:
   # The studio floor would completely occlude a camera beneath the avatar.
   # Disable its camera visibility for this diagnostic angle only; keep other rays.
   for ob in s.objects:
    if ob.name=='Studio floor':ob.visible_camera=angle!='underside'
   tone(s,skin);cam=camera(s,angle,size,span,target);name=f'{build}-{variant}-{preset}-{angle}-skin{skin}-{size}'
   node.file_name=name+'-depth';s.render.filepath=str(D/'references'/(name+'-color.png'));bpy.ops.render.render(write_still=True)
   depths=list((D/'references').glob(name+'-depth*.exr'));assert len(depths)==1,(name,depths)
   records.append(dict(build=build,variant=variant,preset=preset,skin=skin,size=size,angle=angle,color='references/'+name+'-color.png',depth='references/'+depths[0].name,camera=cam,floor_camera_visible=angle!='underside',geometry_sha256=source_hash,alpha_threshold=.5,color_management={'view_transform':s.view_settings.view_transform,'look':s.view_settings.look,'exposure':s.view_settings.exposure,'gamma':s.view_settings.gamma},cycles={'samples':24,'seed':42,'denoising':True}))
   print('PAIR264',name,flush=True)
 (D/'verification'/f'{build}-blender-pairs.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf8')
 print('BLENDER264_COMPLETE',build,len(records),flush=True)
