"""Context-lit color/Z layers for the two fixed fixtures; not a general compositor.
Blender --background --python tools/bake_layers.py -- [Feminine|Masculine]
Other components remain in reflection/shadow rays. Lenses require separate handling.
"""
import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
D=Path(__file__).resolve().parent.parent;palette=json.loads((D/'palette.json').read_text(encoding='utf8'));out=D/'layers';out.mkdir(exist_ok=True)
builds=sys.argv[sys.argv.index('--')+1:] if '--'in sys.argv else ['Feminine','Masculine']
groups={'body-face':['base','eyes','mouth','lashes'],'hair':['hair'],'headgear':['headgear'],'top':['top'],'frames':['glasses'],'detail':['extra'],'lenses':['lenses']}
for build in builds:
 bpy.ops.wm.open_mainfile(filepath=str(D/'assets'/f'{build}-optimized264.blend'));s=bpy.context.scene
 try:
  p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='CUDA';p.get_devices()
  for dev in p.devices:dev.use=dev.type=='CUDA'
  s.cycles.device='GPU' if any(d.type=='CUDA'for d in p.devices)else'CPU'
 except Exception:s.cycles.device='CPU'
 s.render.film_transparent=True;s.cycles.samples=24;s.cycles.seed=42;s.camera.location=(0,-8,1.88);s.camera.rotation_euler=(Vector((0,0,1.88))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=1.65
 node=next(n for n in s.compositing_node_group.nodes if n.type=='OUTPUT_FILE');node.directory=str(out);rows=[]
 for skin in [0,3]:
  for m in bpy.data.materials:
   if not m.use_nodes:continue
   bs=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
   k='skin'if m.name.startswith('Skin')else'ink'if m.name.startswith('Face / ink209')else'lip'if m.name.startswith('Face / lip209')else None
   if k and bs:bs.inputs['Base Color'].default_value=(*palette[k][skin],1)
  for size in [120,512]:
   s.render.resolution_x=s.render.resolution_y=size;s.render.resolution_percentage=100
   for group,roles in groups.items():
    s.view_layers[0].pass_alpha_threshold=0 if group=='lenses'else .5
    for ob in s.objects:
     if ob.type=='MESH':ob.visible_camera=ob.get('component159')in roles
    name=f'{build}-{group}-skin{skin}-{size}';node.file_name=name+'-depth';s.render.filepath=str(out/(name+'-color.png'));bpy.ops.render.render(write_still=True);depths=list(out.glob(name+'-depth*.exr'));assert len(depths)==1
    rows.append(dict(build=build,skin=skin,size=size,group=group,roles=roles,color='layers/'+name+'-color.png',depth='layers/'+depths[0].name,geometry_sha256=hashlib.sha256((D/'assets'/f'{build}-optimized264.glb').read_bytes()).hexdigest(),camera={'position':[0,-8,1.88],'target':[0,0,1.88],'orthographic_span':1.65,'up':'Z','near':s.camera.data.clip_start,'far':s.camera.data.clip_end},alpha_threshold=s.view_layers[0].pass_alpha_threshold,requires_alpha_compositing=group in ['hair','lenses'],context='Other objects camera-invisible but retained in shadow/reflection rays. Context-specific diagnostic layer, not a universal interchangeable lighting solution. These lenses use BLEND alpha, IOR1 and zero transmission. A nearest-opaque compositor cannot represent them.'))
 (D/'verification'/f'{build}-layers.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf8');print('LAYERS264_COMPLETE',build,len(rows),flush=True)
