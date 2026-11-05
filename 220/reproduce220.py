"""blender -b -P reproduce220.py -- --scene scenes/Feminine-cap.blend --choices choices.json --angle profile --output result.png"""
import bpy,sys,json,math,argparse
from pathlib import Path
from mathutils import Vector
P=Path(__file__).parent;sys.path.insert(0,str(P));import parameters220 as params
a=argparse.ArgumentParser();a.add_argument('--scene',default='scenes/Feminine-ponytail.blend');a.add_argument('--choices');a.add_argument('--preset',choices=list(params.CFG['presets']));a.add_argument('--angle',default='front',choices=['front','threequarter','profile','rightprofile','rear','top','underside']);a.add_argument('--output',default='reference220.png');a.add_argument('--size',type=int,default=512);args=a.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
bpy.ops.wm.open_mainfile(filepath=str(P/args.scene));s=bpy.context.scene
choices=json.loads(Path(args.choices).read_text(encoding='utf8')) if args.choices else {}
if args.preset:choices['pony']=params.CFG['presets'][args.preset]
params.apply(s,choices)
target=Vector((0,0,1.88));direction={'front':(0,-8,0),'threequarter':(-4,-8,0),'profile':(-8,0,0),'rightprofile':(8,0,0),'rear':(0,8,0),'top':(0,-4,8),'underside':(0,-4,-8)}[args.angle];s.camera.location=target+Vector(direction);s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=1.5;s.render.resolution_x=s.render.resolution_y=args.size;s.render.resolution_percentage=100;s.render.filepath=str(Path(args.output).resolve());bpy.ops.render.render(write_still=True)
