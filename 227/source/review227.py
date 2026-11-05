import bpy,sys,json
from pathlib import Path
P=Path(__file__).parent;sys.path.insert(0,str(P));sys.path.insert(0,str(P.parent/'refinement224'))
import utils224 as u,build226 as b,hair227 as h
O=P/'revision227';O.mkdir(exist_ok=True)
for d in ['sources','renders','components']:(O/d).mkdir(exist_ok=True)
def main():
 args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['straight,curls,curly-top']
 for style in args[0].split(','):
  build='Masculine' if style in ['curly-top','afro','flow','buzz','locs'] else 'Feminine'
  s=b.load(build);before={k:v for k,v in u.object_geometry(s).items() if s.objects[k].get('component159')!='hair'}
  for ob in list(s.objects):
   if ob.get('component159')=='hair' and not (style in ['curly-top','afro','buzz'] and ob.name in ['Hair / Taper short sides','Hair / Taper fine direction']):u.delete(ob)
  h.build(style);u.bake(s);after=u.object_geometry(s);assert all(after.get(k)==v for k,v in before.items()),style
  bpy.ops.wm.save_as_mainfile(filepath=str(O/'sources'/f'{build}-{style}.blend'),compress=True)
  for angle in ['front','threequarter','profile','rear','top']:u.render(s,O/'renders'/f'{build}-{style}-{angle}.png',384,angle)
  print('REVIEW227',style,flush=True)
if __name__=='__main__':main()
