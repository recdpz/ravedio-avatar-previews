import sys
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue251')
from common251 import *
from fit249 import normalise,move_cloth
from mathutils import Matrix
import bmesh
HAIR=json.loads((P/'hair251.json').read_text());FH=json.loads((P/'female-hats251.json').read_text())
HATS=['cap','beanie','bucket','cowboy','headband','ears','pashmina']

def flatten_buns(s):
 skin=tree([head_object(s)]);count=0
 for ob in [o for o in s.objects if o.type=='MESH' and o.get('component159')=='hair']:
  bm=bmesh.new();bm.from_mesh(ob.data);bm.verts.ensure_lookup_table();seen=set();inv=ob.matrix_world.inverted()
  for v in bm.verts:
   if v.index in seen:continue
   island=[];todo=[v];seen.add(v.index)
   while todo:
    p=todo.pop();island.append(p)
    for edge in p.link_edges:
     other=edge.other_vert(p)
     if other.index not in seen:seen.add(other.index);todo.append(other)
   center=sum((ob.matrix_world@p.co for p in island),Vector())/len(island)
   if center.z>2.20 and abs(center.x)>.20:
    for p in island:
     q=ob.matrix_world@p.co;d=(q-a.C).normalized();hit,_,_,_=skin.ray_cast(a.C,d,2);assert hit is not None;p.co=inv@(hit+d*.014)
    count+=1
  bm.to_mesh(ob.data);bm.free();normalise(ob)
 return count

def tuck_pony(s):
 pieces=[o for o in s.objects if o.type=='MESH' and o.get('component159')=='hair' and any(x in o.name.lower() for x in ['tail220','tie220','chestnut212','fitted tie214'])];ties=[o for o in pieces if 'tie' in o.name.lower()];assert ties,[o.name for o in pieces];tie=ties[0];anchor=sum((tie.matrix_world@v.co for v in tie.data.vertices),Vector())/len(tie.data.vertices);skin=tree([head_object(s)]);target=Vector((anchor.x,0,2.13));hit=skin.ray_cast(Vector((target.x,2,target.z)),Vector((0,-1,0)),4)[0];assert hit is not None;target.y=hit.y+.016;rot=Matrix.Rotation(-.80,3,'X')
 for ob in pieces:
  inv=ob.matrix_world.inverted()
  for v in ob.data.vertices:
   q=target+rot@(ob.matrix_world@v.co-anchor);d=(q-a.C).normalized();hit,_,_,_=skin.ray_cast(a.C,d,2);assert hit is not None;v.co=inv@(hit+d*(.018 if 'tie' not in ob.name.lower() else .025))
  normalise(ob)
 return len(pieces)

def beanie_front(s):
 count=0;skin=tree([head_object(s)])
 for ob in [o for o in s.objects if o.type=='MESH' and o.get('component159')=='hair' and 'front' in o.name.lower()]:
  inv=ob.matrix_world.inverted()
  for v in ob.data.vertices:
   p=ob.matrix_world@v.co;t=smooth((p.z-1.82)/.29)
   if t<=0:continue
   q=p+Vector(((1 if p.x>0 else -1)*.008*t,.018*t,-.035*t));d=q-a.C;hit,_,_,dist=skin.ray_cast(a.C,d.normalized(),2)
   if hit is not None and d.length<dist+.004:q=a.C+d.normalized()*(dist+.004)
   v.co=inv@q;count+=1
  normalise(ob)
 return count

def fit_roots(s,hat):
 if hat=='ears':return 0
 skin=tree([head_object(s)]);cloth=tree([o for o in s.objects if o.type=='MESH' and o.get('component159')=='headgear']);changed=0
 for ob in [o for o in s.objects if o.type=='MESH' and o.get('component159')=='hair']:
  inv=ob.matrix_world.inverted()
  for v in ob.data.vertices:
   p=ob.matrix_world@v.co;w=(smooth((p.y+.25)/.06)*smooth((p.z-1.43)/.25)) if hat=='pashmina' else smooth((p.z-1.85)/.25)
   if w<=0:continue
   dv=p-a.C;direction=dv.normalized();hit,_,_,cd=cloth.ray_cast(a.C,direction,2);sh,_,_,sd=skin.ray_cast(a.C,direction,2)
   if hit is None or sh is None or cd-sd<.015:continue
   target=max(sd+.005,cd-.013)
   if dv.length>target:
    # Covered points that actually pierce fabric are seated fully; smooth
    # transition outside the covered zone keeps free lengths coherent.
    if p.y>-.20 and p.z>1.95:w=1
    q=p.lerp(a.C+direction*target,w);d=q-a.C
    if d.length<sd+.005:q=a.C+direction*(sd+.005)
    v.co=inv@q;changed+=1
  if hat=='beanie':
   limit=max((q.matrix_world@v.co).z for q in s.objects if q.type=='MESH' and q.get('component159')=='headgear' for v in q.data.vertices)-.014
   for v in ob.data.vertices:
    p=ob.matrix_world@v.co
    if p.z>limit:p.z=limit;v.co=inv@p;changed+=1
  normalise(ob)
 return changed

def pony_hoods():
 import common250 as old
 import fit250 as f
 out={}
 for top in CAT251['builds']['Feminine']['tops']:
  s,_=old.load250('Feminine','ponytail',top);f.hood_shape(s,'Feminine','ponytail');ob=next(o for o in s.objects if 'joined hood wrap and ends239' in o.name);n=len(ob.data.vertices)//2;points=[ob.matrix_world@v.co for v in ob.data.vertices];uv={}
  for face in ob.data.polygons:
   if max(face.vertices)>=n:continue
   for li,i in zip(face.loop_indices,face.vertices):uv[i]=ob.data.uv_layers.active.data[li].uv.copy()
  delta={}
  for i,q in uv.items():
   if 0<=q.x<=1.00001 and 0<=q.y<=1.00001 and points[i].z>1.40:
    dz=-.060*math.exp(-((q.x-.46)/.19)**2)*smooth((q.y-.69)/.31)
    if abs(dz)>1e-8:delta[i]=Vector((0,0,dz))
  move_cloth(s,delta,points);path=P/'components'/f'Feminine-ponytail-{top}-pashmina251-headgear.glb';ex.export(s,path,'headgear');out[top]='components/'+path.name
 return out

def case(b,style,hat,hoods):
 s,_=load251(b,style,hat);frozen={k:v for k,v in u.object_geometry(s).items() if s.objects[k].get('component159') not in ['hair','headgear','extra']}
 remove(['hair'])
 if b=='Masculine' and style in HAIR:hp=P/HAIR[style]['path']
 elif b=='Feminine' and style=='twin-braids':hp=P/FH['braidRoots']
 elif b=='Feminine' and style=='ponytail' and hat in ['beanie','bucket','cowboy','headband']:hp=(OLD/CAT251['fits'][b+'-'+style][hat]['hair']).resolve()
 else:hp=(OLD/CAT251['builds'][b]['hair'][style]['path']).resolve()
 imported(hp,'hair');a.setup();reset_head(s);actions=[]
 if hat=='bucket':remove(['headgear']);imported(P/FH['bucket'][b],'headgear')
 if hat=='headband':remove(['headgear']);imported(P/FH['bandana'][b+'-'+style],'headgear')
 if hat=='beanie':
  for ob in [o for o in s.objects if o.type=='MESH' and o.get('component159')=='headgear']:
   inv=ob.matrix_world.inverted()
   for vert in ob.data.vertices:
    q=ob.matrix_world@vert.co;q.z+=.072*smooth((q.z-2.13)/.24);vert.co=inv@q
   normalise(ob)
 if b=='Feminine' and style=='space-buns' and hat!='ears':actions.append(['flattened concealed bun islands',flatten_buns(s)])
 if b=='Feminine' and style=='ponytail' and hat=='beanie':actions.append(['cuff-seated front locks',beanie_front(s)])
 if b=='Feminine' and style=='ponytail' and hat=='pashmina':
  remove(['headgear']);imported(P/hoods['open'],'headgear');actions.append(['folded concealed pony bundle',tuck_pony(s)])
 actions.append(['covered-root seating',fit_roots(s,hat)]);now=u.object_geometry(s);assert all(now.get(k)==v for k,v in frozen.items());key=b+'-'+style+'-'+hat+'251';u.bake(s);paths={}
 for group in ['hair','headgear']:
  path=P/'components'/f'{key}-{group}.glb';ex.export(s,path,group);paths[group]='components/'+path.name
 import accessories235
 sprout=accessories235.sprout();u.bake(s);path=P/'components'/f'{key}-sprout.glb';ex.export(s,path,'extra');sprout['path']='components/'+path.name;remove(['extra'])
 if style=='twin-braids':imported(P/FH['braidLengths']['pashmina' if hat=='pashmina' else 'normal']['open']['path'],'hairLengths')
 gpu();close251(s,key,['front','profile','rear'],size=288)
 if (b,style,hat) in [('Feminine','ponytail','pashmina'),('Masculine','flow','cap')]:
  bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(P/'sources'/f'{key}-assembly.blend'),compress=True)
 return dict(**paths,sprout=sprout,actions=actions,protected_exact=True)

def main():
 out=json.loads((P/'fits251.json').read_text()) if (P/'fits251.json').exists() else {};hoods=json.loads((P/'pony-hoods251.json').read_text()) if (P/'pony-hoods251.json').exists() else pony_hoods();(P/'pony-hoods251.json').write_text(json.dumps(hoods,indent=2)+'\n',encoding='utf8');looks=[]
 for style in HAIR:
  for hat in HATS:looks.append(('Masculine',style,hat))
 for style in CAT251['builds']['Feminine']['hair']:
  for hat in HATS:
   if style in ['space-buns','twin-braids'] or hat in ['bucket','headband','beanie'] or (style=='ponytail' and hat in ['beanie','pashmina']):looks.append(('Feminine',style,hat))
 looks += [('Masculine','sidepart','bucket'),('Masculine','sidepart','headband'),('Masculine','sidepart','beanie')]
 for b,style,hat in looks:
  key=b+'-'+style+'-'+hat
  if '--resume' in sys.argv and key in out:continue
  out[key]=case(b,style,hat,hoods);(P/'fits251.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8');print('FIT251',key,flush=True)
 print('FIT251_COMPLETE',len(out),flush=True)
if __name__=='__main__':main()
