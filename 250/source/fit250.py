"""Authored worn shell: concealed hair gathers to actual-head-safe cloth support."""
import sys
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue250')
from common250 import *
from fit249 import normalise,move_cloth
import bmesh
from mathutils import Matrix

def volume_class(build,style):
 if style in ['curls','afro','box-braids']:return 'full'
 if style in ['straight','side-sweep','bob','flow','locs','middle-part']:return 'draped'
 return 'compact'

def hood_shape(s,build,style):
 ob=next(o for o in s.objects if 'joined hood wrap and ends239' in o.name);n=len(ob.data.vertices)//2;old=[ob.matrix_world@v.co for v in ob.data.vertices];uv={}
 for f in ob.data.polygons:
  if max(f.vertices)>=n:continue
  for li,i in zip(f.loop_indices,f.vertices):uv[i]=ob.data.uv_layers.active.data[li].uv.copy()
 skin=tree([head_object(s)]);kind=volume_class(build,style);margin={'compact':.056,'draped':.070,'full':.085}[kind];delta={}
 for i,q in uv.items():
  p=old[i]
  if not (0<=q.x<=1.00001 and 0<=q.y<=1.00001 and p.z>1.40):continue
  weight=smooth((q.y-.065)/.17)*smooth(min(q.x,1-q.x)/.075)
  if weight<1e-7:continue
  dv=p-a.C;direction=dv.normalized();hit,_,_,distance=skin.ray_cast(a.C,direction,2)
  if hit is None:continue
  rear=smooth((p.y-.02)/.25);lower=1-smooth((p.z-1.47)/.34)
  # Deliberate cloth reserve around the head, not a hull of individual locks.
  target=distance+margin+.030*rear+.095*lower
  wanted=a.C+direction*target
  # A rounded cowl lower edge rather than a rigid outward bell/flat shelf.
  d=(wanted-p)*weight
  if style=='ponytail' and build=='Feminine':
   d.z+=.060*math.exp(-((q.x-.46)/.19)**2)*smooth((q.y-.69)/.31)
  if d.length>1e-8:delta[i]=d
 move_cloth(s,delta,old)
 return dict(family=kind,margin=margin,modified_outer_vertices=len(delta),max_displacement=max((v.length for v in delta.values()),default=0),preserved_front_crossing=True)

def hood_tree(s):
 ob=next(o for o in s.objects if 'joined hood wrap and ends239' in o.name);n=len(ob.data.vertices)//2;verts=[ob.matrix_world@v.co for v in ob.data.vertices];faces=[]
 for f in ob.data.polygons:
  if max(f.vertices)>=n:continue
  uv=[ob.data.uv_layers.active.data[li].uv for li in f.loop_indices]
  if all(-.001<=q.x<=1.001 and -.001<=q.y<=1.001 for q in uv):faces.append(list(f.vertices))
 return BVHTree.FromPolygons(verts,faces)

def fit_hair(s,build,style):
 if style=='ponytail' and build=='Feminine':
  pieces=[o for o in s.objects if o.type=='MESH' and any(k in o.name for k in ['chestnut212','fitted tie214'])]
  tie=next(o for o in pieces if 'fitted tie214' in o.name);anchor=sum((tie.matrix_world@v.co for v in tie.data.vertices),Vector())/len(tie.data.vertices);target=anchor+Vector((0,0,-.12));skin_root=tree([head_object(s)]);hit=skin_root.ray_cast(Vector((target.x,2,target.z)),Vector((0,-1,0)),4)[0];assert hit is not None;target.y=hit.y+.008;rotation=Matrix.Rotation(-.70,3,'X')
  for ob in pieces:
   inv=ob.matrix_world.inverted()
   for v in ob.data.vertices:v.co=inv@(target+rotation@(ob.matrix_world@v.co-anchor))
 skin=tree([head_object(s)]);cloth=hood_tree(s);stats=[]
 for ob in [o for o in s.objects if o.type=='MESH' and o.get('component159')=='hair']:
  if any(x in ob.name for x in ['rounded tail220','tie220','ties226','fitted tie214']) or (style=='ponytail' and 'chestnut212' in ob.name):continue
  inv=ob.matrix_world.inverted();modified=0;maxmove=0;preserved=0
  for v in ob.data.vertices:
   p=ob.matrix_world@v.co;weight=smooth((p.y+.18)/.18)*smooth((p.z-1.34)/.29)
   if style=='afro' and p.y>-.25:weight=max(weight,smooth((p.y+.25)/.035)*smooth((p.z-1.34)/.29))
   if weight<1e-7:preserved+=1;continue
   dv=p-a.C;direction=dv.normalized();hit,_,_,sd=skin.ray_cast(a.C,direction,2)
   if hit is None:continue
   ch,_,_,cd=cloth.ray_cast(a.C,direction,2)
   if ch is None:continue
   # Keep a positive skin-to-hair shell; never project coverage into the head.
   room=max(.010,cd-sd-.023);thickness=max(.008,dv.length-sd)
   packed=.012+thickness*(.50 if style in ['curls','afro'] else .40)
   target=sd+max(.007,min(room,packed,thickness))
   desired=p+(a.C+direction*target-p)*weight
   d=desired-a.C
   if d.length<sd+.006:desired=a.C+direction*(sd+.006)
   movement=(desired-p).length
   if movement>1e-7:v.co=inv@desired;modified+=1;maxmove=max(maxmove,movement)
  if modified:normalise(ob)
  stats.append(dict(name=ob.name,modified=modified,max_displacement=maxmove,front_and_tips_preserved=preserved))
 return stats

def build(build,style,top=None,export=False):
 s,paths=load250(build,style,top);top=top or ('open' if build=='Feminine' else 'tank');frozen={k:v for k,v in u.object_geometry(s).items() if s.objects[k].get('component159') not in ['hair','headgear']}
 hood=hood_shape(s,build,style);hair=fit_hair(s,build,style);now=u.object_geometry(s);assert all(now.get(k)==v for k,v in frozen.items())
 key=build+'-'+style+'-'+top;item=dict(build=build,style=style,top=top,hood=hood,hair_changes=hair,paths=paths,protected_exact=True)
 if export:
  u.bake(s);bpy.ops.file.pack_all();src=P/'sources'/f'{key}-pashmina250.blend';bpy.ops.wm.save_as_mainfile(filepath=str(src),compress=True);item['source']=str(src)
  for group in ['hair','headgear']:
   path=P/'components'/f'{key}-pashmina250-{group}.glb';ex.export(s,path,group);item[group]='components/'+path.name
 if export:
  import accessories235
  anchor=accessories235.sprout();path=P/'components'/f'{build}-{style}-pashmina250-sprout.glb';u.bake(s);ex.export(s,path,'extra');item['sprout']={'path':'components/'+path.name,**anchor}
  for o in list(s.objects):
   if o.get('component159')=='extra':u.delete(o)
 close(s,key,['front','profile','rightprofile','rear','threequarter','top','underside'])
 return item

if __name__=='__main__':
 styles=next((x.split('=',1)[1].split(',') for x in sys.argv if x.startswith('--styles=')),['straight','curls','ponytail']);builds=next((x.split('=',1)[1].split(',') for x in sys.argv if x.startswith('--builds=')),['Feminine']);out=json.loads((P/'fits250.json').read_text()) if (P/'fits250.json').exists() else {}
 for b in builds:
  for style in (list(CAT250['builds'][b]['hair']) if '--all-styles' in sys.argv else styles):
   key=b+'-'+style+'-'+('open' if b=='Feminine' else 'tank')
   if '--resume' in sys.argv and key in out and out[key].get('sprout'):continue
   item=build(b,style,export='--export' in sys.argv);out[b+'-'+style+'-'+item['top']]=item;(P/'fits250.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8');print('FIT250',b,style,item['hood'],flush=True)
 print('FIT250_COMPLETE',len(out),flush=True)
