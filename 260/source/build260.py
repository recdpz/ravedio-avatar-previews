import sys
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue260')
from common260 import *
from math import sin,cos,pi,sqrt
import random,bmesh
STAGE='pass4'

def mat260(name,rough=.35):
 m=a.material('Hair260 / '+name,(.120,.047,.026),rough);old.normal_texture(m,'long');bs=m.node_tree.nodes['Principled BSDF'];bs.inputs['Specular IOR Level'].default_value=.34;bs.inputs['Coat Weight'].default_value=.045
 for n in m.node_tree.nodes:
  if n.type=='NORMAL_MAP':n.inputs['Strength'].default_value=.18
 return m

def sphere_lerp(root,tip,t):
 A=(root-a.C).normalized();B=(tip-a.C).normalized();ang=math.acos(max(-1,min(1,A.dot(B))));d=(A*sin((1-t)*ang)+B*sin(t*ang))/max(.0001,sin(ang));return d.normalized()

def rooted(ps,widths,depths,name,m,j):
 ob=old.lock(name,ps,widths,depths,phase=j*.63,mat=m,n=80,sides=32,grain=.0019)
 # Authored Blender UV0 y grows root-to-tip; glTF flips it.
 for uv in ob.data.uv_layers.active.data:uv.uv.y=1-uv.uv.y
 return ob

def flow_underfill(long,part,m):
 # A recessed continuation of the same groom closes coverage between raised
 # locks. Its edge stops before the visible lock ends, rather than forming a rim.
 for side in [-1,1]:
  nu,nv=112,120;vv=[];ff=[];uvs=[]
  for j in range(nv+1):
   v=j/nv;y=-.29+.575*v;root=c.surf(part*(1-.35*smooth((y+.05)/.34))+side*.001,y,.003);ph=side*(.74+6*.365*v);endth=(1.47+.35*smooth((v*6-.3)/5.2) if long else 1.24+.14*sin(abs(ph)))-.10;end=c.sp(endth,ph,.003)
   for i in range(nu+1):
    t=i/nu;D=sphere_lerp(root,end,t);hit=c.HEAD.ray_cast(a.C,D,2)[0];phase=v*6+.12*sin(t*5+v*3);lift=.004+.009*sin(pi*t)**.7+.004*(.5+.5*cos(phase*2*pi))*sin(pi*t);p=hit+D*lift
    vv.append(tuple(p));uvs.append((v*6,1-t))
  for j in range(nv):
   for i in range(nu):k=j*(nu+1)+i;ff.append((k,k+1,k+nu+2,k+nu+1))
  ob=a.mesh('Hair260 / recessed layered continuation '+str(side),vv,ff,m,'hair');uv=ob.data.uv_layers.new(name='Root to tip260')
  for f in ob.data.polygons:
   for li,k in zip(f.loop_indices,f.vertices):uv.data[li].uv=uvs[k]

def flowing(style):
 for ob in list(bpy.context.scene.objects):
  if ob.get('component159')=='hair':u.delete(ob)
 long=style=='flow';part=.13 if long else 0.;ys=[-.29,-.21,-.105,.015,.13,.23,.285];m=mat260('layered '+style);created=[];flow_underfill(long,part,m)
 for side in [-1,1]:
  for j,y in enumerate(ys):
   root=c.surf(part*(1-.35*smooth((y+.05)/.34))+side*.012,y,.014)
   ph=(.74+j*.365)*side
   endth=1.47+.35*smooth((j-.3)/5.2) if long else 1.24+.14*sin(abs(ph))
   end=c.sp(endth,ph,.035);ps=[]
   for t in np.linspace(0,1,80):
    D=sphere_lerp(root,end,min(1,t/.88));hit=c.HEAD.ray_cast(a.C,D,2)[0];lift=.016+(.052 if long else .040)*sin(pi*t)**.85
    p=hit+D*lift
    if long:
     # Loose planar S: the forelock curves across, then turns back near the ear.
     w=sin(pi*t)**1.4;p.x+=side*(.028*sin(t*2*pi+j*.25)+.009*sin(t*4*pi+j*.8))*w;p.y+=.023*sin(t*2*pi+.4+j*.2)*w
    else:p.x+=side*.010*sin(t*2*pi+j*.3)*sin(pi*t)
    if t>.72:
     q=smooth((t-.72)/.28);p.y+=(.055 if long else .020)*q*sin(abs(ph));p.z-=((.06 if long else .006)+(.022 if long else .014)*sin(j*1.7+side*.6))*q
     p.x+=side*(.025 if long else -.006)*sin(q*pi*.7)*sin(abs(ph))
    ps.append(p)
   if long and j<3:
    # Face framing sections turn over the forehead, fall at the temple, then
    # reverse toward the ear in a loose S instead of straight curtain plates.
    if side<0:
     pts=[root,c.surf(.04,-.29+j*.065,.065),c.sp(.89,-.58-j*.20,.066),c.sp(1.18,-.86-j*.21,.064),c.sp(1.49,-1.18-j*.23,.050),Vector((-.49+j*.015,.005+j*.095,1.70+.025*sin(j*1.6))),Vector((-.455+j*.020,.075+j*.10,1.74+.035*sin(j*1.4)))];ps=old.spline(pts,80)
    else:
     pts=[root,c.sp(.78,.69+j*.23,.058),c.sp(1.16,1.06+j*.25,.055),c.sp(1.46,1.36+j*.25,.046),Vector((.49-j*.012,.08+j*.11,1.73+.025*sin(j))),Vector((.46-j*.013,.16+j*.11,1.76+.023*sin(j)))];ps=old.spline(pts,80)
   width=(.112 if long else .100)*(1+.08*sin(j*1.9));rooted(ps,[.047,width*.95,width,width*.98,width*.78,.029],[.009,.027,.034 if long else .027,.028,.022,.009],'Flow260 layered '+str(side)+' '+str(j) if long else 'Curtains260 '+str(side)+' '+str(j),m,j)
   created.append((side,j))
 # Crown joins grow backward without carrying the part seam to the nape.
 for j,x in enumerate([-.24,-.12,0,.12,.24]):
  ps=[]
  for t in np.linspace(0,1,80):
   p=c.sp(.42+(1.30 if long else .95)*t,pi+(x/.25)*.48,.020+.025*sin(pi*t));p.x+=x*.34*sin(pi*t);p.z-=(.04 if long else 0)*smooth((t-.65)/.35);ps.append(p)
  rooted(ps,[.035,.085,.091,.084,.053,.022],[.008,.021,.025,.022,.018,.009],'Flow260 nape '+str(j) if long else 'Curtains260 nape '+str(j),m,j+15)
 return dict(method='Individual crown-to-length locks; no mirrored two-bank sheet',part_x=part,flow='Off-center curved overlapping sweep, longer relaxed ear/nape layers' if long else 'Short split curtains, varied side and nape endings; no continuous bowl hem',banks=len(created)+5)

def locs260():
 for ob in list(bpy.context.scene.objects):
  if ob.get('component159')=='hair':u.delete(ob)
 m=mat260('mature compact locs',.48);bs=m.node_tree.nodes['Principled BSDF'];bs.inputs['Specular IOR Level'].default_value=.29;bs.inputs['Coat Weight'].default_value=.025
 rng=random.Random(260);guides=[]
 # Dense interlocking roots with the same compact fiber relief. No alpha tint,
 # flat painted cells or exposed straight cap edge.
 nu,nv=224,88;vv=[];ff=[];uvs=[]
 for j in range(nv+1):
  t=j/nv
  for i in range(nu):
   ph=2*pi*i/nu;th=.001+t*(1.06+.49*smooth((1-cos(ph))/.85));lift=.007+(.026+.003*sin(ph*39+th*17)+.002*sin(ph*61-th*29))*sin(pi*t)**.35;vv.append(tuple(c.sp(th,ph,lift)));uvs.append((ph/(2*pi)*14,1-t))
 for j in range(nv):
  for i in range(nu):k=j*nu+i;n=j*nu+(i+1)%nu;ff.append((k,n,n+nu,k+nu))
 ob=a.mesh('Hair260 / compact section-root continuation',vv,ff,m,'hair');uv=ob.data.uv_layers.new(name='Root fiber260')
 for f in ob.data.polygons:
  for li,k in zip(f.loop_indices,f.vertices):uv.data[li].uv=uvs[k]
 for ring,(th,count) in enumerate([(.19,3),(.48,7),(.81,13),(1.15,18)]):
  for j in range(count):
   ph=2*pi*(j+.45*(ring%2))/count+rng.uniform(-.06,.06)
   if ring==3 and cos(ph)>.65:continue
   start=c.sp(th,ph,.012);front=cos(ph)>.60;endth=(1.05 if front else 1.65)+rng.uniform(-.05,.07);outph=ph+.10*sin(ph+.5);ps=[];radius=.050+rng.uniform(-.004,.006)
   for t in np.linspace(0,1,80):
    angle=th+(endth-th)*t;p=c.sp(angle,ph+(outph-ph)*smooth(t),.019+.038*sin(pi*t)**.75)
    p.x+=.012*sin(t*2*pi+ph)*sin(pi*t);p.y+=.012*sin(t*2*pi+ring*.7)*sin(pi*t)
    if t>.68:p.z-=(.024 if front else .066)*smooth((t-.68)/.32)
    ps.append(p)
   ob=rooted(ps,[radius*.65,radius,radius*.99,radius*.96,radius*.92,radius*.84],[radius*.62,radius*.83,radius*.88,radius*.86,radius*.80,radius*.72],'Loc260 '+str(ring)+' '+str(j),m,len(guides))
   # Coarse irregular compacted fibers, not smooth cylinders or spiral ropes.
   for i,v in enumerate(ob.data.vertices):
    row,col=divmod(i,32);t=row/79;q=2*pi*col/32;center=ps[row];off=v.co-center;v.co=center+off*(1+.017*sin(t*38+ph+sin(q*3))+.021*cos(q*7+t*25))
   guides.append(dict(root_theta=th,phi=ph,radius=radius))
 return dict(method='Separate fuller rooted mature locs, compact fiber relief and rounded tips; no painted root sheet',count=len(guides),sections=guides)

def afro260(s):
 rows=[]
 for ob in s.objects:
  if ob.type!='MESH' or ob.get('component159')!='hair':continue
  inv=ob.matrix_world.inverted();before=max((ob.matrix_world@v.co).z for v in ob.data.vertices)
  for v in ob.data.vertices:
   p=ob.matrix_world@v.co;p.z-=.035*smooth((p.z-2.09)/.36);v.co=inv@p
  rows.append(dict(before_top=before,after_top=max((ob.matrix_world@v.co).z for v in ob.data.vertices)))
 return dict(method='Upper crown lowered smoothly, lower coverage and width retained',bounds=rows)

def female_source(s,style):
 for ob in list(s.objects):
  if ob.get('component159')=='hair':u.delete(ob)
 src=P.parent/('catalogue252/sources/Feminine-straight-hair252.blend' if style=='straight' else 'catalogue226/revision227/sources/Feminine-'+style+'.blend')
 with bpy.data.libraries.load(str(src),link=False) as (src,dst):dst.objects=list(src.objects)
 for ob in dst.objects:
  if ob is None:continue
  if ob.type=='MESH' and ob.get('component159')=='hair':s.collection.objects.link(ob)
  else:u.delete(ob)
 return [ob for ob in s.objects if ob.type=='MESH' and ob.get('component159')=='hair']

if __name__=='__main__':
 for build,styles in STYLES.items():
  for style in styles:
   if build=='Feminine':continue
   arg=next((x.split('=',1)[1].split(',') for x in sys.argv if x.startswith('--styles=')),None)
   if arg and style not in arg:continue
   s=load260(build,style);frozen=protect(s);report=afro260(s) if style=='afro' else locs260() if style=='locs' else flowing(style);check(s,frozen);save260(s,build,style,STAGE,report)
 print('MALE260_COMPLETE',flush=True)
