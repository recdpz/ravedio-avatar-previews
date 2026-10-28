"""Static context variants and actual assembled fit evidence, no runtime fitting."""
import bpy,sys,json,math,hashlib
from pathlib import Path
from mathutils import Vector
P=Path(__file__).parent;sys.path.insert(0,str(P));sys.path.insert(0,str(P.parent/'refinement224'));import utils224 as u,build226 as b,sculpt226 as a,rebuild_hair226 as h
HATS=['none','cap','beanie','bucket','cowboy','headband','ears','pashmina']
def import_group(path,groups):
 with bpy.data.libraries.load(str(path),link=False) as(src,dst):dst.objects=list(src.objects)
 for o in dst.objects:
  if o.get('component159') in groups:bpy.context.scene.collection.objects.link(o)
  else:u.delete(o)
def fitted(s):
 changed=0
 for ob in s.objects:
  if ob.type!='MESH' or ob.get('component159')!='hair':continue
  inv=ob.matrix_world.inverted()
  for v in ob.data.vertices:
   p=ob.matrix_world@v.co
   if p.z<1.96:continue
   t=min(1,max(0,(p.z-1.96)/.065));t=t*t*(3-2*t);dv=p-h.a.C
   size=(.493,.418,.473);norm=math.sqrt(sum((dv[i]/size[i])**2 for i in range(3)))
   if norm>1:
    q=h.a.C+dv/norm;p=p.lerp(q,t);v.co=inv@p;changed+=1
 return changed
def build():
 (P/'fits').mkdir(exist_ok=True);(P/'fit-review').mkdir(exist_ok=True)
 assets=json.loads((P/'assets226.json').read_text());report={};arg=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [];only=arg[0].split(',') if arg else None
 for key,info in assets.items():
  if info['group']!='hair' or (only and info['style'] not in only):continue
  bpy.ops.wm.open_mainfile(filepath=str(P/info['source']));s=bpy.context.scene
  if info['style']=='space-buns':
   b.remove(['hair']);h.build('space-buns',True);u.bake(s)
  n=fitted(s);bpy.ops.wm.save_as_mainfile(filepath=str(P/'fits'/f'{key}-covered.blend'),compress=True);u.export(s,P/'components'/f'{key}-covered-hair.glb','hair');report[key]=dict(changed_root_vertices=n,free_lengths_below_196_unchanged=True,component=f'components/{key}-covered-hair.glb',source=f'fits/{key}-covered.blend')
 u.dump(P/'covered226.json',report)
def review():
 assets=json.loads((P/'assets226.json').read_text());covered=json.loads((P/'covered226.json').read_text());records=[]
 for key,info in assets.items():
  if info['group']!='hair':continue
  for hat in HATS[1:]:
   covered_hat=hat in ['cap','beanie','bucket','cowboy'];path=P/(covered[key]['source'] if covered_hat else info['source']);bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene
   if hat=='cap':import_group(P.parent/'refinement224/scenes'/('Feminine-cap.blend' if info['build']=='Feminine' else 'Masculine-details.blend'),['headgear'])
   else:import_group(P/'sources'/f'Feminine-{hat}.blend',['headgear'])
   name=key+'--'+hat
   for angle in ['front','profile','rear','top']:
    u.camera(s,angle,200);s.render.filepath=str(P/'fit-review'/f'{name}-{angle}.png');bpy.ops.render.render(write_still=True)
   records.append(dict(hair=key,hat=hat,source=str(path),state='renders ready; visual audit required'));u.dump(P/'fit-matrix226.json',records)
   print('FIT226',name,flush=True)
if __name__=='__main__':
 if '--' in sys.argv and sys.argv[-1]=='review':review()
 else:build()
