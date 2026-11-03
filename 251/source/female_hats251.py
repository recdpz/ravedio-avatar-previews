import sys
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue251')
from common251 import *
import headwear235 as hats
import bmesh
from math import sin,cos,pi,sqrt

def native_hair(style):
 remove(['hair']);src=P.parent/'catalogue226/revision227/sources'/f'Feminine-{style}.blend'
 with bpy.data.libraries.load(str(src),link=False) as (old,new):new.objects=list(old.objects)
 for ob in new.objects:
  if ob is not None and ob.get('component159')=='hair':bpy.context.scene.collection.objects.link(ob)
  elif ob is not None:u.delete(ob)

def root_braids():
 s,_=load251('Feminine','twin-braids');native_hair('twin-braids')
 for ob in list(s.objects):
  if ob.get('component159')=='hair' and 'twin braid' in ob.name.lower():u.delete(ob)
 u.bake(s);path=P/'components/Feminine-twin-braids-roots251-hair.glb';ex.export(s,path,'hair');return 'components/'+path.name

def broad_torso(s,cloth=False):
 points=[]
 for ob in s.objects:
  if ob.type!='MESH':continue
  n=ob.name.lower();group=ob.get('component159');take=('torso' in n and group=='base') or (group=='top' and len(ob.data.vertices)>900 and not any(x in n for x in ['sleeve','collar','hem','binding','placket','button','lace','string','cord','pocket'])) or (cloth and group=='headgear')
  if take:
   for v in ob.data.vertices:
    p=ob.matrix_world@v.co
    if .75<p.z<1.39:points.append(p)
 assert points;bm=bmesh.new();q=np.array(points);_,ids=np.unique(np.round(q/.005).astype('i'),axis=0,return_index=True)
 for i in ids:bm.verts.new(q[i])
 bmesh.ops.convex_hull(bm,input=list(bm.verts),use_existing_faces=False);bm.verts.ensure_lookup_table();bm.verts.index_update();tr=BVHTree.FromPolygons([v.co for v in bm.verts],[[v.index for v in f.verts] for f in bm.faces]);bm.free();return tr

def braid_lengths(top,hat=False):
 s,_=load251('Feminine','twin-braids','pashmina' if hat else 'none',top);remove(['hair']);support=broad_torso(s,hat);a.setup();a.GROUP='hairLengths';before=set(s.objects);old=h.head_surface;h.head_surface=sp
 for side in [-1,1]:
  pts=[sp(1.20,side*2.0,.025),sp(1.62,side*1.85,.027),Vector((side*.405,-.095,1.57))];last_y=None;contacts=[]
  for z,x in [(1.31,.285),(1.25,.278),(1.17,.265),(1.085,.245)]:
   hit,_,_,_=support.ray_cast(Vector((side*x,-2,z)),Vector((0,1,0)),4);assert hit is not None,(top,z,x);y=hit.y-.049
   if last_y is not None:y=min(y,last_y+.027)
   pts.append(Vector((side*x,y,z)));contacts.append(dict(z=z,garment_front=hit.y,braid_center=y));last_y=y
  h.plait('Hair / seated twin braid251 '+str(side),pts,.064)
 for ob in s.objects:
  if ob not in before and ob.type=='MESH':
   ob['component159']='hairLengths'
   if hat:
    skin=tree([head_object(s)]);cloth_tree=tree([o for o in s.objects if o.type=='MESH' and o.get('component159')=='headgear']);inv=ob.matrix_world.inverted()
    for v in ob.data.vertices:
     p=ob.matrix_world@v.co;w=smooth((p.z-1.43)/.16)
     if w<=0:continue
     d=p-a.C;direction=d.normalized();hit,_,_,cd=cloth_tree.ray_cast(a.C,direction,2);sh,_,_,sd=skin.ray_cast(a.C,direction,2)
     if hit is not None and sh is not None and d.length>cd-.018:v.co=inv@(p.lerp(a.C+direction*max(sd+.006,cd-.022),w))
 h.head_surface=old;u.bake(s);key='Feminine-twin-braids-'+top+('-pashmina' if hat else '')+'-lengths251';path=P/'components'/f'{key}.glb';ex.export(s,path,'hairLengths');remove(['hair']);imported(P/'components/Feminine-twin-braids-roots251-hair.glb','hair');close251(s,key,['front','profile','rear','threequarter'],body=True);return dict(path='components/'+path.name,contact_samples=contacts,method='Whole woven plaits transition from the head to broad selected garment/chest support; lower path bridges small hollows.')

def bucket(b):
 s,_=load251(b,'ponytail' if b=='Feminine' else 'taper');remove(['headgear']);a.setup();a.GROUP='headgear';mat=a.material('Headwear / bucket cotton251',(.075,.12,.17),.72);hem=a.material('Headwear / bucket stitching251',(.24,.29,.31),.73);under=a.material('Headwear / bucket underside251',(.053,.08,.11),.80)
 def crown(u,t):
  ph=u*2*pi;rx=.500-.086*t;ry=.432-.072*t;z=2.075+.055*cos(ph)+.285*t;soft=.004*sin(ph*3+.4)*sin(pi*t);return Vector(((rx+soft)*sin(ph),.015-(ry+soft)*cos(ph),z))
 hats.grid('Bucket / soft crown251',crown,112,30,mat,.007)
 def roof(u,t):
  p=crown(u,1);return Vector((p.x*t,.015+(p.y-.015)*t,2.360+.055*cos(u*2*pi)*t+.009*(1-t*t)))
 hats.grid('Bucket / rounded flat top251',roof,112,24,mat,.007)
 def brim(u,t):
  ph=u*2*pi;return Vector(((.500+.095*t)*sin(ph),.015-(.432+.080*t)*cos(ph),2.075+.055*cos(ph)-(.080-.020*max(0,cos(ph)))*t-.012*t*t+.003*sin(ph*3+.5)*t*t))
 hats.grid('Bucket / short downward brim251',brim,144,24,mat,.009)
 for t in [.52,.75,.96]:a.tube('Bucket / sewn brim row251 '+str(t),[brim(u,t)+Vector((0,0,.0025)) for u in np.linspace(0,1,145)],.0015,.0013,hem,n=145,sides=6,taper=False,group='headgear')
 for angle in [0,.25,.5,.75]:a.tube('Bucket / crown seam251 '+str(angle),[crown(angle,t)+Vector((.0015*sin(angle*2*pi),-.0015*cos(angle*2*pi),0)) for t in np.linspace(.02,.98,36)],.0013,.0010,hem,n=36,sides=6,taper=False,group='headgear')
 u.bake(s);path=P/'components'/f'{b}-bucket251-headgear.glb';ex.export(s,path,'headgear');close251(s,b+'-bucket251',['front','profile','rear','top','underside']);return 'components/'+path.name

def bandana(b,style):
 s,_=load251(b,style);remove(['headgear']);hats.bandana();obs=[o for o in s.objects if o.type=='MESH' and o.get('component159')=='headgear' and 'knot' in o.name.lower()];assert obs;points=[o.matrix_world@v.co for o in obs for v in o.data.vertices];center=sum(points,Vector())/len(points);mat=obs[0].data.materials[0]
 for ob in list(s.objects):
  if ob.get('component159')=='headgear' and any(x in ob.name.lower() for x in ['knot','fabric tie','kerchief tie']):u.delete(ob)
 anchor=center.copy();center.y+=.045
 for side in [-1,1]:
  def gathered(w,t):
   p=anchor.lerp(center,t);p.x+=side*(.044-.032*t);p.z+=(w-.5)*(.048-.018*t);p.y+=.003*sin(pi*w)*sin(pi*t);return p
  hats.grid('Bandana / continuous gathered tie base251 '+str(side),gathered,14,24,mat,.006)
 for side in [-1,1]:
  def fold(w,t):
   x=side*(.061-.122*t);return center+Vector((x,.014+.017*sin(pi*t)+(w-.5)*.012,side*(.023-.046*t)+(w-.5)*.043*(.80+.20*sin(pi*t))))
  hats.grid('Bandana / folded crossing knot251 '+str(side),fold,18,30,mat,.006)
  path=a.sample([center+Vector((side*.017,.015,-.008)),center+Vector((side*.056,.039,-.065)),center+Vector((side*.080,.026,-.18))],42)
  def tie(w,t):
   p=path[min(41,int(t*41))].copy();p.x+=(w-.5)*(.060+.025*sin(pi*t))*(1-.35*t);p.y+=.005*sin(w*pi*2)*sin(pi*t);p.z+=.018*(w-.5)*t;return p
  hats.grid('Bandana / natural hanging tie251 '+str(side),tie,18,41,mat,.005)
 a.tube('Bandana / compressed center fold251',[center+Vector((-.021,.006,.024)),center+Vector((0,.039,.017)),center+Vector((.021,.006,-.024))],.019,.011,mat,n=26,sides=12,taper=False,group='headgear')
 u.bake(s);path=P/'components'/f'{b}-{style}-bandana251-headgear.glb';ex.export(s,path,'headgear');close251(s,b+'-'+style+'-bandana251',['rear','profile','threequarter']);return 'components/'+path.name

def main():
 q=json.loads((P/'female-hats251.json').read_text()) if (P/'female-hats251.json').exists() else {};q['braidRoots']=root_braids();q['braidLengths']={'normal':{},'pashmina':{}}
 for mode in ['normal','pashmina']:
  for top in CAT251['builds']['Feminine']['tops']:q['braidLengths'][mode][top]=braid_lengths(top,mode=='pashmina');(P/'female-hats251.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf8')
 q['bucket']={b:bucket(b) for b in CAT251['builds']};q['bandana']={}
 for b,bc in CAT251['builds'].items():
  for style in bc['hair']:q['bandana'][b+'-'+style]=bandana(b,style);(P/'female-hats251.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf8');print('BANDANA251',b,style,flush=True)
 print('FEMALE_HATS251_COMPLETE',flush=True)
if __name__=='__main__':main()
