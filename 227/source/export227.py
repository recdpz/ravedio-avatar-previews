"""Ordinary shared-coordinate GLBs and independently reopened export evidence."""
import bpy,sys,json,struct
from pathlib import Path
from mathutils import kdtree
P=Path(__file__).parent;O=P/'revision227';sys.path.insert(0,str(P));sys.path.insert(0,str(P.parent/'refinement224'))
import utils224 as u,export226 as ex
HAIR=['straight','curls','side-sweep','flow','curly-top','afro','space-buns','twin-braids','box-braids','locs','buzz']
HATS=['bucket','cowboy','beanie','headband','ears','pashmina']
EYE=['reading','wayfarer','cat-eye','heart','wraparound','kaleidoscope']
def points(s,g):return [o.matrix_world@v.co for o in s.objects if o.type=='MESH' and not o.hide_render and o.get('component159')==g for v in o.data.vertices]
def maxerr(aa,bb):
 tree=kdtree.KDTree(len(bb))
 for i,p in enumerate(bb):tree.insert(p,i)
 tree.balance();return max((tree.find(p)[2] for p in aa),default=0)
def main():
 for d in ['roundtrip','portraits','components']:(O/d).mkdir(exist_ok=True)
 record=json.loads((O/'export-proof.json').read_text()) if (O/'export-proof.json').exists() else {}
 args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
 for source in sorted((O/'sources').glob('*.blend')):
  key=source.stem;build,style=key.split('-',1)
  if args and style not in args[0].split(','):continue
  groups=['hair'] if style in HAIR else ['headgear','hair'] if style in HATS else ['glasses','lenses'] if style in EYE else ['extra']
  bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene
  before={g:points(s,g) for g in groups};parts={};stats={}
  for g in groups:
   path=O/'components'/f'{key}-{g}.glb';ex.export(s,path,g);parts[g]='components/'+path.name
   raw=path.read_bytes();doc=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])
   stats[g]={'bytes':len(raw),'triangles':sum(doc['accessors'][p['indices']]['count']//3 for m in doc['meshes'] for p in m['primitives']),'nodes':len(doc['nodes']),'materials':len(doc.get('materials',[])),'textures':[{k:im.get(k) for k in ['name','mimeType']} for im in doc.get('images',[])],'extensions':doc.get('extensionsUsed',[]),'alpha_modes':[m.get('alphaMode','OPAQUE') for m in doc.get('materials',[])],'transmission':[m.get('extensions',{}).get('KHR_materials_transmission') for m in doc.get('materials',[])]}
  for o in list(s.objects):
   if o.get('component159') in groups:u.delete(o)
  errors={}
  for g,p in parts.items():
   bpy.ops.import_scene.gltf(filepath=str(O/p));after=points(s,g);assert before[g] and after,(key,g)
   err=max(maxerr(before[g],after),maxerr(after,before[g]));assert err<2e-5,(key,g,err);errors[g]=err
  for angle in ['front','threequarter','profile','rightprofile','rear','top','underside']:u.render(s,O/'roundtrip'/f'{key}-{angle}.png',384,angle)
  u.render(s,O/'roundtrip'/f'{key}-body.png',384,'threequarter',True)
  for tone in range(4):u.tone(s,tone);u.render(s,O/'portraits'/f'{key}-tone{tone}.png',128)
  record[key]={'source':str(source),'source_sha256':u.sha(source),'build':build,'style':style,'components':parts,'statistics':stats,'max_bidirectional_world_position_error':errors,'component_sha256':{g:u.sha(O/p) for g,p in parts.items()},'visual_review':'pending; renders are evidence, not a pass'}
  u.dump(O/'export-proof.json',record);print('EXPORT227',key,flush=True)
if __name__=='__main__':main()
