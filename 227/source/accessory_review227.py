import bpy,sys,json
from pathlib import Path
P=Path(__file__).parent;sys.path.insert(0,str(P));sys.path.insert(0,str(P.parent/'refinement224'))
import utils224 as u,build226 as b,hair227 as h,sculpt226 as a,accessories227 as acc,fit226
O=P/'revision227'
def main():
 args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['bucket,cowboy,beanie,headband,ears,reading,wayfarer,cat-eye,heart,wraparound,kaleidoscope,gems,sprout']
 for style in args[0].split(','):
  s=b.load('Feminine');before={k:v for k,v in u.object_geometry(s).items() if s.objects[k].get('component159') not in ['hair','headgear','glasses','lenses','extra']}
  if style in ['bucket','cowboy','beanie','headband','ears','pashmina']:
   b.remove(['hair']);h.build('straight');u.bake(s)
   if style in ['bucket','cowboy','beanie']:fit226.fitted(s)
   acc.hat(style)
  elif style in ['gems','sprout']:
   if style=='gems':acc.gems()
   else:a.extra(style)
  else:acc.eyewear(style)
  u.bake(s);after=u.object_geometry(s);assert all(after.get(k)==v for k,v in before.items()),style
  bpy.ops.wm.save_as_mainfile(filepath=str(O/'sources'/f'Feminine-{style}.blend'),compress=True)
  for angle in ['front','threequarter','profile','rear','top']:u.render(s,O/'renders'/f'Feminine-{style}-{angle}.png',384,angle)
  print('ACCESSORY227',style,flush=True)
if __name__=='__main__':main()
