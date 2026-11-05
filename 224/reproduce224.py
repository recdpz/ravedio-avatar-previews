"""Portable source reproduction. No historical drive imports or network needed."""
import bpy,sys,argparse
from pathlib import Path
P=Path(__file__).parent;sys.path.insert(0,str(P));import utils224 as u
p=argparse.ArgumentParser();p.add_argument('--scene',required=True);p.add_argument('--output',required=True);p.add_argument('--size',type=int,default=512);p.add_argument('--angle',default='front',choices=['front','threequarter','profile','rightprofile','rear','top','underside']);p.add_argument('--body',action='store_true');p.add_argument('--glb');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);bpy.ops.wm.open_mainfile(filepath=str(Path(a.scene).resolve()));s=bpy.context.scene
if a.glb:
 for o in list(s.objects):
  if o.type in ['MESH','CURVE'] and o.get('component159')!='studio':u.delete(o)
 bpy.ops.import_scene.gltf(filepath=str(Path(a.glb).resolve()))
s.cycles.device='CPU';u.render(s,Path(a.output).resolve(),a.size,a.angle,a.body)
