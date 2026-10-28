import bpy,sys,json
from pathlib import Path
P=Path(__file__).parent;O=P/'revision227';sys.path.insert(0,str(P));sys.path.insert(0,str(P.parent/'refinement224'))
import utils224 as u,fit226 as f,build226 as b,hair227 as h,export226 as ex
from mathutils.bvhtree import BVHTree
from mathutils import Vector
import math
HATS=['cap','beanie','bucket','cowboy','headband','ears','pashmina']

def soft_covered(s):
 n=0
 for ob in s.objects:
  if ob.type!='MESH' or ob.get('component159')!='hair' or 'bun ' in ob.name.lower():continue
  inv=ob.matrix_world.inverted()
  for v in ob.data.vertices:
   p=ob.matrix_world@v.co
   if p.z<1.78:continue
   t=max(0,min(1,(p.z-1.78)/.31));t=t*t*(3-2*t);dv=p-h.a.C;unit=Vector((dv.x/h.a.R.x,dv.y/h.a.R.y,dv.z/h.a.R.z)).normalized();th=math.acos(max(-1,min(1,unit.z)));ph=math.atan2(unit.x,-unit.y);seated=h.head_surface(th,ph,.012)
   if dv.length>(seated-h.a.C).length:v.co=inv@p.lerp(seated,t);n+=1
 return n

def compressed_curls(s):
 """A pressure-fit curl mass, without the previous flat brim-height shelf."""
 n=0
 for ob in s.objects:
  if ob.type!='MESH' or ob.get('component159')!='hair':continue
  inv=ob.matrix_world.inverted()
  for v in ob.data.vertices:
   p=ob.matrix_world@v.co;dv=p-h.a.C;unit=Vector((dv.x/h.a.R.x,dv.y/h.a.R.y,dv.z/h.a.R.z)).normalized();th=math.acos(max(-1,min(1,unit.z)));ph=math.atan2(unit.x,-unit.y);surface=h.head_surface(th,ph,0);length=(surface-h.a.C).length;excess=max(0,dv.length-length)
   v.co=inv@(h.a.C+dv.normalized()*(length+min(excess,.003)+max(0,excess-.003)*.26));n+=1
 return n

def cloth_fit(s,drape_only=True):
 vertices=[];faces=[]
 for ob in s.objects:
  if ob.type!='MESH' or ob.get('component159')!='headgear' or (drape_only and 'settled head drape' not in ob.name):continue
  start=len(vertices);vertices.extend(ob.matrix_world@v.co for v in ob.data.vertices);faces.extend([start+k for k in p.vertices] for p in ob.data.polygons)
 tree=BVHTree.FromPolygons(vertices,faces);changed=0
 for ob in s.objects:
  if ob.type!='MESH' or ob.get('component159')!='hair':continue
  inverse=ob.matrix_world.inverted()
  for v in ob.data.vertices:
   p=ob.matrix_world@v.co
   if p.z<(1.65 if drape_only else 1.90):continue
   direction=(p-h.a.C).normalized();hit,normal,_,distance=tree.ray_cast(h.a.C,direction,1.4)
   if hit is not None and (p-h.a.C).length>distance-.014:
    v.co=inverse@(h.a.C+direction*max(.1,distance-.014));changed+=1
 return changed
def main():
 for d in ['fits','fit-review']:(O/d).mkdir(exist_ok=True)
 records=json.loads((O/'fit-proof.json').read_text()) if (O/'fit-proof.json').exists() else {};proof=json.loads((O/'export-proof.json').read_text());args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
 for key,item in proof.items():
  if set(item['components'])!={'hair'}:continue
  if args and item['style'] not in args[0].split(','):continue
  source=Path(item['source']);bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene
  if item['style']=='space-buns':b.remove(['hair']);h.gathered('space-buns',True);u.bake(s)
  changed=compressed_curls(s) if item['style'] in ['afro','curly-top'] else soft_covered(s);fit=O/'fits'/f'{key}-covered.blend';bpy.ops.wm.save_as_mainfile(filepath=str(fit),compress=True);glb=O/'components'/f'{key}-covered-hair.glb';ex.export(s,glb,'hair')
  records[key]={'source':str(fit),'component':'components/'+glb.name,'changed_crown_vertices':changed,'free_lengths_below_z178_unchanged':item['style'] not in ['space-buns','afro','curly-top'],'context':'Low gathered buns' if item['style']=='space-buns' else 'Compressed short curls' if item['style'] in ['afro','curly-top'] else 'Gradually seated crown; free lengths below1.78 retained','combinations':{}}
  for hat in HATS:
   covered=hat not in ['headband','ears'];bpy.ops.wm.open_mainfile(filepath=str(fit if covered else source));s=bpy.context.scene
   if hat=='cap':donor=P.parent/'refinement224/scenes'/('Feminine-cap.blend' if item['build']=='Feminine' else 'Masculine-details.blend')
   else:donor=O/'sources'/f'Feminine-{hat}.blend'
   f.import_group(donor,['headgear']);name=key+'--'+hat
   specific=None
   if hat=='pashmina':
    n=cloth_fit(s);specific=O/'components'/f'{key}-pashmina-hair.glb';ex.export(s,specific,'hair');bpy.ops.wm.save_as_mainfile(filepath=str(O/'fits'/f'{key}-pashmina.blend'),compress=True)
   elif covered and item['style'] in ['afro','curly-top']:
    n=cloth_fit(s,False);specific=O/'components'/f'{key}-{hat}-hair.glb';ex.export(s,specific,'hair');bpy.ops.wm.save_as_mainfile(filepath=str(O/'fits'/f'{key}-{hat}.blend'),compress=True)
   rendered_component=specific if specific else glb if covered else O/item['components']['hair']
   b.remove(['hair']);bpy.ops.import_scene.gltf(filepath=str(rendered_component))
   for angle in ['front','profile','rear','top']:u.render(s,O/'fit-review'/f'{name}-{angle}.png',192,angle)
   records[key]['combinations'][hat]={'rendered':True,'visual_review':'pending','covered_variant':covered,'specific_component':'components/'+specific.name if specific else None,'rendered_hair_sha256':u.sha(rendered_component),'hair_export_reopened':True}
   u.dump(O/'fit-proof.json',records)
  print('FIT227',key,flush=True)
if __name__=='__main__':main()
