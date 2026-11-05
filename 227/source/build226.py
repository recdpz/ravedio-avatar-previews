import bpy,sys,json,time,hashlib
from pathlib import Path
P=Path(__file__).parent;sys.path.insert(0,str(P));sys.path.insert(0,str(P.parent/'refinement224'))
import utils224 as u,sculpt226 as a,rebuild_hair226 as h
for d in ['components','sources','review1','review2','evidence']: (P/d).mkdir(exist_ok=True)
bpy.context.preferences.filepaths.save_version=0
def load(build):
 case='Feminine-uncovered' if build=='Feminine' else 'Masculine-taper';bpy.ops.wm.open_mainfile(filepath=str(P.parent/'refinement224/scenes'/f'{case}.blend'));s=bpy.context.scene;s.cycles.device='CPU';return s
def remove(groups):
 for ob in list(bpy.context.scene.objects):
  if ob.get('component159') in groups:u.delete(ob)
def save_component(s,key,groups):
 # Preserve full source build in one packed file per asset, with reference assembly.
 u.bake(s);bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(P/'sources'/f'{key}.blend'),compress=True)
 result={}
 for group in groups:
  path=P/'components'/f'{key}-{group}.glb';u.export(s,path,group);result[group]='components/'+path.name
 return result
def render(s,key,angles,folder='review1',size=256):
 for angle in angles:
  u.camera(s,angle,size);s.cycles.samples=12 if folder=='review1' else 28;s.render.filepath=str(P/folder/f'{key}-{angle}.png');bpy.ops.render.render(write_still=True)
def main():
 arg=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [];only=arg[0] if arg else 'all';report=json.loads((P/'assets226.json').read_text()) if (P/'assets226.json').exists() else {}
 jobs=[]
 for style in a.HAIR:jobs.append((style,'Feminine' if style in a.HAIR[:6] else 'Masculine','hair'))
 for style in ['beanie','bucket','cowboy','headband','ears','pashmina']:jobs.append((style,'Feminine','headgear'))
 for style in ['reading','wayfarer','cat-eye','heart','wraparound','kaleidoscope']:jobs.append((style,'Feminine','glasses'))
 for style in ['sprout','gems']:jobs.append((style,'Feminine','extra'))
 for style,build,group in jobs:
  if only!='all' and style not in only.split(','):continue
  key=build+'-'+style;s=load(build);protected={k:v for k,v in u.object_geometry(s).items() if s.objects[k].get('component159') not in ['hair','headgear','glasses','lenses','extra']}
  if group=='hair':
   if style in ['curly-top','afro','buzz']:
    for ob in list(s.objects):
     if ob.get('component159')=='hair' and ob.name not in ['Hair / Taper short sides','Hair / Taper fine direction']:u.delete(ob)
   else:remove(['hair'])
   h.build(style)
  elif group=='headgear':
   remove(['hair','headgear']);h.build('straight',covered=style not in ['headband','ears']);a.hat(style)
  elif group=='glasses':a.eyewear(style)
  else:a.extra(style)
  groups=['glasses','lenses'] if group=='glasses' else [group]
  if group=='headgear':groups.append('hair')
  u.bake(s);current=u.object_geometry(s);assert all(current.get(k)==v for k,v in protected.items()),key
  parts=save_component(s,key,groups);report[key]=dict(build=build,style=style,group=group,components=parts,source=f'sources/{key}.blend',protected_geometry_exact=True,review='construction renders pending visual audit')
  u.dump(P/'assets226.json',report);u.dump(P/'progress226.json',dict(state='rendering first pass',case=key,completed=list(report)))
  render(s,key,['front','threequarter','profile','rear','top']);print('ASSET226',key,flush=True)
 u.dump(P/'progress226.json',dict(state='first pass ready',completed=list(report)))
if __name__=='__main__':main()
