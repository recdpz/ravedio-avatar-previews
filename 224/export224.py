"""Export an already baked packed scene or one independent component group."""
import bpy,sys,argparse
from pathlib import Path
P=Path(__file__).parent;sys.path.insert(0,str(P));import utils224 as u
p=argparse.ArgumentParser();p.add_argument('--scene',required=True);p.add_argument('--output',required=True);p.add_argument('--group');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);bpy.ops.wm.open_mainfile(filepath=str(Path(a.scene).resolve()));u.export(bpy.context.scene,Path(a.output).resolve(),a.group)
