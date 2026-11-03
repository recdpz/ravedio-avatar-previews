import sys
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue251')
from common251 import *
from hair235 import lock
from math import sin,cos,pi,sqrt
import bmesh

def mats():
 a.setup();a.GROUP='hair';a.M['hair']=a.material('Hair / main251',(.120,.047,.026),.31);a.M['shine']=a.material('Hair / accent251',(.145,.062,.035),.30);a.M['dark']=a.material('Hair / recessed roots251',(.080,.027,.014),.38)
def accent(k):return a.M['shine'] if k%5 in [1,3] else a.M['hair']
def boundary(ph):
 angle=abs((ph+pi)%(2*pi)-pi)
 if angle<.95:return .96-.040*sin(angle)**2
 return .94+.84*smooth((angle-.95)/.60)+.04*smooth((angle-1.6)/1.2)
def foundation(mode='dense',edge=None,volume=0,height=None):
 nu,nv=(256,80) if mode=='buzz' else (144,58);verts=[];faces=[];cols=[];uvs=[]
 for j in range(nv+1):
  t=j/nv
  for i in range(nu):
   ph=i/nu*2*pi;end=min(edge(ph),boundary(ph)) if edge else boundary(ph);th=.003+t*end;dist=end-th
   if mode=='fade':density=.06+.94*smooth(dist/(.36 if cos(ph)<.55 else .07));alpha=density*(.62 if cos(ph)<.58 and th>1.02 else 1)*smooth((1-t)/.014);lift=.003+.010*density
   elif mode=='buzz':density=.31+.13*smooth(dist/.40);alpha=density*smooth((1-t)/.012);lift=.003+.005*density+.00065*cos(ph*96+th*23)*sin(pi*t)
   else:alpha=smooth((1-t)/.018);lift=.009+volume*(.7+.3*cos(th))
   if mode=='dense' and height:lift=height(th,ph)
   if mode=='dense':lift+=.0012*sin(ph*33+th*3)*sin(pi*t)
   verts.append(tuple(sp(th,ph,lift)));cols.append((1,1,1,alpha))
 for j in range(nv):
  for i in range(nu):k=j*nu+i;l=j*nu+(i+1)%nu;faces.append((k,l,l+nu,k+nu))
 faces.append(tuple(range(nu-1,-1,-1)));mat=a.material('Hair / clipped grain251' if mode!='dense' else 'Hair / recessed roots251',(.095,.037,.019) if mode!='dense' else (.080,.027,.014),.64 if mode=='buzz' else .48 if mode!='dense' else .35);ob=a.mesh('Hair / clean bounded '+mode+'251',verts,faces,mat,'hair');rgba(ob,cols)
 if mode!='dense':
  tex=mat.node_tree.nodes.new('ShaderNodeTexImage');im=bpy.data.images.get('Hair / neutral fine grain251')
  if im is None:
   rng=np.random.default_rng(251);p=np.ones((512,512,4),dtype='f');p[:,:,:3]=rng.uniform(.69,1.0,(512,512,1));im=bpy.data.images.new('Hair / neutral fine grain251',width=512,height=512);im.pixels.foreach_set(p.ravel());im.pack()
  tex.image=im;mix=mat.node_tree.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[2].default_value=(.095,.037,.019,1);mat.node_tree.links.new(tex.outputs['Color'],mix.inputs[1]);mat.node_tree.links.new(mix.outputs[0],mat.node_tree.nodes['Principled BSDF'].inputs['Base Color']);uv=ob.data.uv_layers.new(name='Short cut flow UV251')
  for face in ob.data.polygons:
   seam=any(v%nu>nu*.9 for v in face.vertices)
   for li,v in zip(face.loop_indices,face.vertices):row,col=divmod(v,nu);uv.data[li].uv=(1 if seam and col==0 else col/nu,row/nv)
 if mode in ['fade','buzz']:cut_grain(mode)
 return ob
def cut_grain(mode):
 rng=random.Random(3251 if mode=='buzz' else 4251);vv=[];ff=[]
 for k in range(2400 if mode=='buzz' else 1600):
  ph=rng.random()*2*pi;angle=abs((ph+pi)%(2*pi)-pi);end=boundary(ph);th=math.acos(1-rng.random()*(1-cos(end-.025)))
  if mode=='fade' and (angle<1.0 or th<1.10):continue
  density=.3+.7*smooth((end-th)/.35)
  if rng.random()>density:continue
  length=(.008 if mode=='buzz' else .014)+(.010 if mode=='buzz' else .018)*density;rad=(.00065 if mode=='buzz' else .0009)*(1+.4*density);start=len(vv)
  for j in range(3):
   t=j/2;theta=min(end-.012,th+t*length);p=sp(theta,ph,.0055);N=(p-a.C).normalized();B=Vector((cos(ph),sin(ph),0));T=N.cross(B).normalized();r=rad*(.65+.35*sin(pi*t))
   for q in range(4):vv.append(tuple(p+B*(r*cos(q*pi/2))+N*(r*.60*sin(q*pi/2))))
  for j in range(2):
   for q in range(4):a1=start+j*4+q;b=start+j*4+(q+1)%4;ff.append((a1,b,b+4,a1+4))
  ff.extend([(start+3,start+2,start+1,start),(start+8,start+9,start+10,start+11)])
 mat=a.material('Hair / close cut strokes251',(.09,.031,.016),.52);a.mesh('Hair / bounded short strokes251',vv,ff,mat,'hair')
def taper():
 foundation('fade')
 # Restore the liked153 sweep proportions without the rejected235 fibers/scalp.
 parts=json.loads(Path('E:/Ravedio-Avatar/refinement153/Taper-geometry.json').read_text());skin=tree([head_object(bpy.context.scene)])
 for part in parts:
  if part['material']!='hair':continue
  verts=[Vector(v) for v in part['position']]
  if 'crown' in part['name'].lower() or 'short sweep' in part['name'].lower() or 'top' in part['name'].lower():
   for i,p in enumerate(verts):
    weight=max(smooth((2.17-p.z)/.22),smooth((p.y-.18)/.16)*.90);d=p-a.C
    if weight>0:
     hit,_,_,dist=skin.ray_cast(a.C,d.normalized(),2)
     if hit is not None and d.length>dist+.026:verts[i]=p.lerp(a.C+d.normalized()*(dist+.026),weight*.82)
  ob=a.mesh('Hair / refined153 '+part['name'],[tuple(v) for v in verts],np.asarray(part['index']).reshape(-1,3).tolist(),a.M['hair'],'hair');ob.data.materials.append(a.M['shine']);ob.data.materials.append(a.M['hair'])
  for f,tone in zip(ob.data.polygons,part['triangle_tone']):f.material_index=int(tone)
def flow():
 foundation('dense',lambda ph:.88+.91*(1-max(0,cos(ph))**2.2),.033)
 for side in [-1,1]:
  for j in range(9):
   ph=side*(.70+j*.285);root=surf(side*.012,-.27+j*.058,.030);pts=[root,sp(.48,ph*.80,.052),sp(.95,ph,.074),sp(1.40,ph+side*.06,.058)]
   z=1.62+.033*sin(j*2.2+side);end=Vector((side*.46*sin(abs(ph)),.015-.385*cos(ph),z))
   if j<2:end=Vector((side*(.43+.015*j),-.13+.11*j,1.74-.04*j))
   wave=Vector((side*(.024+.010*sin(j*1.8)),.014*cos(j),0));pts += [end+wave+Vector((0,-.025,.21)),end-wave*.5+Vector((0,.018,.075)),Vector((end.x*.92,end.y+.035,end.z-.025))]
   lock('Hair / wavy flow layered251 '+str(side)+' '+str(j),pts,[.030,.054,.074,.071,.052,.029,.017],[.010,.023,.030,.027,.023,.012,.007],j*.9+side,mat=accent(j+(side>0)),n=82,sides=22,tip=.14)
 for j in range(7):
  x=-.28+j*.093;pts=[surf(x*.35,.19,.024),Vector((x*.76,.32,2.24+.015*sin(j))),Vector((x,.445,2.04)),Vector((x+.022*sin(j),.46,1.78)),Vector((x*.92,.43,1.57+.025*sin(j*1.6)))]
  lock('Hair / flowing nape251 '+str(j),pts,[.025,.066,.071,.054,.004],[.012,.028,.030,.024,.003],j,mat=accent(j),n=72,sides=20,tip=.14)
 for side in [-1,1]:
  for j in range(3):
   pts=[surf(.055+side*.014,-.29+j*.025,.024),sp(.64,side*(.50+j*.04),.042),sp(.90,side*(.85+j*.035),.052),sp(1.30,side*(1.12+j*.025),.038),sp(1.55,side*(1.40+j*.02),.027)]
   lock('Hair / loose flow fringe251 '+str(side)+' '+str(j),pts,[.014,.047,.058,.034,.004],[.009,.024,.026,.017,.003],j+side,mat=accent(j),n=64,sides=20,tip=.16)
def curls(afro=False):
 from mathutils import kdtree
 if not afro:foundation('fade')
 rng=random.Random(6251 if afro else 7251);count=135 if afro else 65
 def edge(ph):return (1.26-.30*max(0,cos(ph))**2 if afro else .99)+.027*sin(ph*13)+.012*sin(ph*27+.4)
 def height(th,ph):return (.033+.17*max(0,cos(th))**2.4) if afro else (.031+.044*max(0,cos(th)))
 def seat(p):
  q=Vector(((p.x-a.C.x)/a.R.x,(p.y-a.C.y)/a.R.y,(p.z-a.C.z)/a.R.z)).normalized();th=math.acos(max(-1,min(1,q.z)));ph=math.atan2(q.x,-q.y);return sp(th,ph,height(th,ph))
 centers=[];guides=[];maxth=1.23 if afro else .96
 for k in range(count):
  ph=k*pi*(3-sqrt(5))+rng.uniform(-.08,.08);th=math.acos(1-(k+.5)/count*(1-cos(maxth)))
  if th>edge(ph)-.018:continue
  p=sp(th,ph,height(th,ph));centers.append(p);N=(p-a.C).normalized();B=Vector((cos(ph),sin(ph),0));T=N.cross(B).normalized();q=rng.random()*2*pi;A=B*cos(q)+T*sin(q);D=N.cross(A);r=rng.uniform(.030,.044) if afro else rng.uniform(.044,.064)
  for t in np.linspace(0,1,30):
   angle=(t-.1)*1.55*pi;guides.append(seat(p+A*r*sin(angle)+D*r*.85*cos(angle)))
 kd=kdtree.KDTree(len(guides));kc=kdtree.KDTree(len(centers))
 for i,p in enumerate(guides):kd.insert(p,i)
 for i,p in enumerate(centers):kc.insert(p,i)
 kd.balance();kc.balance();nu,nv=256,100;verts=[];faces=[];colors=[]
 for j in range(nv+1):
  t=j/nv
  for i in range(nu):
   ph=i/nu*2*pi;th=.003+t*edge(ph);p=sp(th,ph,height(th,ph));distance=kd.find(p)[2];dc=kc.find(p)[2];relief=.015*math.exp(-(distance/.011)**2)-.003*math.exp(-((distance-.020)/.008)**2)+.007*math.exp(-(dc/.036)**2);N=(p-a.C).normalized();w=smooth((1-t)/.055);skin=sp(th,ph,.005);p=skin.lerp(p+N*relief,w);verts.append(tuple(p));shade=.86+.14*math.exp(-(distance/.018)**2);colors.append((shade,shade,shade,1))
 for j in range(nv):
  for i in range(nu):x=j*nu+i;y=j*nu+(i+1)%nu;faces.append((x,y,y+nu,x+nu))
 faces.append(tuple(range(nu-1,-1,-1)));mat=a.material('Hair / sculpted '+('afro' if afro else 'curly crown')+'251',(.12,.047,.026),.40);ob=a.mesh('Hair / continuous coiled '+('afro' if afro else 'top')+'251',verts,faces,mat,'hair');rgba(ob,colors);sol=ob.modifiers.new('Seated curl boundary251','SOLIDIFY');sol.thickness=.012;sol.offset=-1
def locs():
 a.M['hair']=a.material('Hair / loc main251',(.12,.047,.026),.63);a.M['shine']=a.material('Hair / loc accent251',(.145,.062,.035),.59)
 foundation('dense',lambda ph:.86+.86*(1-max(0,cos(ph))**2.5));rng=random.Random(451);k=0
 for ring,(theta,count) in enumerate([(.22,5),(.53,8),(.84,10),(1.13,11)]):
  for j in range(count):
   ph=2*pi*(j+.38*(ring%2))/count;th=min(theta,boundary(ph)-.14);root=sp(th,ph,.014);mid=sp(min(1.55,th+.47),ph+.055,.050);front=cos(ph)>.52;end=sp(min(1.82,th+.86),ph+.085,.056)
   if front:
    end=sp(1.03+.025*sin(j*1.9),ph+.04,.045);mid=sp((th+1.03)/2,ph+.035,.045)
   else:end.z=1.76+.055*sin(j*2.4+ring);end.y+=.012
   pts=[root,sp(min(1.1 if front else 1.4,th+.17),ph+.035*sin(k),.026),mid,mid.lerp(end,.72),end];r=rng.uniform(.033,.041);ob=lock('Hair / natural loc251 '+str(k),pts,[r*.88,r,r*.99,r*.91,r*.55],[r*.80,r*.90,r*.91,r*.85,r*.53],k*.8,mat=accent(k),n=64,sides=16,root=.88,tip=.045,rough=True);k+=1
def flow_banks():
 # Low continuous part banks support the roots; no separate crown patch.
 for side in [-1,1]:
  def bank(w,t):return surf(side*(.004+.036*w),-.27+.48*t,.023+.007*sin(pi*w))
  a.grid('Hair / loose crown root support251 '+str(side),bank,12,44,a.M['hair'],.003,group='hair')

def middle():
 # Retain the liked front curtains and nearest banks from the native235 source.
 original=Path('E:/Ravedio-Avatar/catalogue235/sources/Masculine-middle-part.blend')
 with bpy.data.libraries.load(str(original),link=False) as (src,dst):dst.objects=list(src.objects)
 for ob in dst.objects:
  if ob is None:continue
  name=ob.name;keep='soft front curtain235' in name or ('center part235' in name and name.rsplit(' ',1)[-1] in ['0','1','2','3'])
  if keep:bpy.context.scene.collection.objects.link(ob);ob['component159']='hair'
  else:u.delete(ob)
 foundation('dense',lambda ph:.88+.88*(1-max(0,cos(ph))**2.5))
 for side in [-1,1]:
  for j in range(5):
   y=.01+j*.052;root=surf(side*.011,y,.016);ph=side*(1.95+j*.25);pts=[root,sp(.55,ph,.044),sp(1.0,ph,.050),sp(1.45,ph,.043),sp(1.79,ph,.024)]
   lock('Hair / simplified middle crown251 '+str(side)+' '+str(j),pts,[.019,.059,.064,.048,.004],[.009,.024,.027,.020,.003],j,mat=accent(j),n=64,sides=20,tip=.17)
 for j in range(7):
  x=-.25+j*.083;pts=[surf(x*.28,.19,.018),Vector((x*.65,.36,2.18)),Vector((x,.436,1.99)),Vector((x*.95+.008*sin(j),.42,1.80+.018*sin(j*2)))]
  lock('Hair / middle nape flow251 '+str(j),pts,[.019,.054,.057,.004],[.008,.023,.025,.003],j,mat=accent(j),n=60,sides=20,tip=.18)
 for side in [-1,1]:
  def bank(w,t):return surf(side*(.004+.045*w),-.26+.49*t,.013+.004*sin(pi*w))
  a.grid('Hair / narrow center support251 '+str(side),bank,12,38,a.M['dark'],.003,group='hair')
def build(style):
 s,_=load251('Masculine',style);frozen=protect(s);remove(['hair']);mats()
 if style=='taper':taper()
 elif style=='buzz':foundation('buzz')
 elif style=='curly-top':curls(False)
 elif style=='afro':curls(True)
 elif style=='flow':flow();flow_banks()
 elif style=='locs':locs()
 elif style=='middle-part':middle()
 check(s,frozen);u.bake(s);bpy.ops.file.pack_all();src=P/'sources'/f'Masculine-{style}-hair251.blend';bpy.ops.wm.save_as_mainfile(filepath=str(src),compress=True);path=P/'components'/f'Masculine-{style}-hair251.glb';ex.export(s,path,'hair');close251(s,'Masculine-'+style,['front','threequarter','profile','rightprofile','rear','top','underside']);return dict(path='components/'+path.name,source=str(src),protected_exact=True,head_support='actual retained head BVH; bounded hairline; no scattered cut-fiber quads')
if __name__=='__main__':
 styles=next((x.split('=',1)[1].split(',') for x in sys.argv if x.startswith('--styles=')),['taper','buzz','curly-top','afro','flow','locs','middle-part']);out=json.loads((P/'hair251.json').read_text()) if (P/'hair251.json').exists() else {}
 for style in styles:
  out[style]=build(style);(P/'hair251.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8');print('HAIR251',style,flush=True)
 print('HAIR251_COMPLETE',len(out),flush=True)
