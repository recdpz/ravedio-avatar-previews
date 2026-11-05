"""Authored broad-lock construction; no separate visible scalp shell for loose hair."""
import bpy, math, random
import numpy as np
from mathutils import Vector
from math import sin,cos,pi,sqrt
import sculpt226 as a
import rebuild_hair226 as old

_support_cache=None
def head_surface(theta,phi,extra=.02):
 """Follow the retained head surface, including its authored temple shaping."""
 global _support_cache
 from mathutils.bvhtree import BVHTree
 head=next((o for o in bpy.context.scene.objects if o.name=='Skin / soft oval head'),None)
 if head is None:return a.polar(theta,phi,extra)
 key=head.as_pointer()
 if _support_cache is None or _support_cache[0]!=key:
  vertices=[head.matrix_world@v.co for v in head.data.vertices]
  _support_cache=(key,BVHTree.FromPolygons(vertices,[list(f.vertices) for f in head.data.polygons]))
 d=(a.polar(theta,phi,0)-a.C).normalized();hit,normal,_,_= _support_cache[1].ray_cast(a.C+d*1.2,-d,2.)
 return hit+d*extra if hit is not None else a.polar(theta,phi,extra)

def smooth(t):
 t=max(0,min(1,t));return t*t*(3-2*t)

def lock(name,points,widths,depths,phase=0,root=.5,detail=True):
 ps=a.sample(points,96);v=[];f=[];prev=None
 for i,p in enumerate(ps):
  t=i/(len(ps)-1);T=(ps[min(i+1,len(ps)-1)]-ps[max(i-1,0)]).normalized()
  # Tangent frame follows the head in the root zone, then the hanging mass.
  outward=Vector((p.x/.50**2,(p.y-.015)/.43**2,max(0,p.z-1.82)/.48**2)).normalized()
  N=outward-T*outward.dot(T)
  if N.length<.1:N=Vector((0,-1,0))-T*T.dot(Vector((0,-1,0)))
  N.normalize();B=T.cross(N).normalized()
  if prev is not None and B.dot(prev)<0:B=-B;N=-N
  prev=B
  w=float(np.interp(t,np.linspace(0,1,len(widths)),widths));d=float(np.interp(t,np.linspace(0,1,len(depths)),depths))
  w*=min(1,root+t*9)*max(.018,min(1,(1-t)/.065))**.55
  d*=max(.025,min(1,(1-t)/.06))**.5
  for j in range(32):
   q=2*pi*j/32;across=cos(q);front=max(0,sin(q))
   # Shallow incised channels in the same surface, not extra floating ropes.
   ridges=(.0014*cos(across*17+phase+.3*sin(t*6))+.0006*cos(across*39+phase))*front**3 if detail else 0
   p2=p+B*(w*across)+N*(d*sin(q)+ridges)
   v.append(tuple(p2))
 for i in range(95):
  for j in range(32):k=i*32+j;n=i*32+(j+1)%32;f.append((k,n,n+32,k+32))
 f += [tuple(range(31,-1,-1)),tuple(95*32+j for j in range(32))]
 return a.mesh(name,v,f,a.M['hair'],'hair')

def loose(style):
 a.setup();a.GROUP='hair';rng=random.Random(227)
 curls=style=='curls';short=style=='flow';sweep=style=='side-sweep';part=.105 if sweep else .025
 # Each crown section transitions directly into its own falling length.
 # Irregular root spacing and swept paths prevent the old ladder-like crown.
 for side in [-1,1]:
  ys=[-.322,-.223,-.105,.025,.155,.275]
  for j,y in enumerate(ys):
   root=a.surface(part,y,.020);ph=(.69+j*.405)*side
   endz=(1.54 if short else 1.17)+.04*sin(j*1.9+side)
   pts=[root,a.polar(.48,ph*.72,.047),a.polar(.90,ph*.88,.057),a.polar(1.35,ph,.055),a.polar(1.80,ph,.041)]
   front=j<2
   endx=side*(.36 if front else .40)*sin(abs(ph))
   ylower=-.245 if front else (.19+.15*(-cos(ph)))
   pts += [Vector((side*.47*sin(abs(ph)),(-.20 if front else .31*(-cos(ph))),1.48)),Vector((endx,ylower,endz+.08)),Vector((endx-side*.018,ylower+.01,endz))]
   ps=a.sample(pts,96)
   for k,p in enumerate(ps):
    t=k/95;env=smooth((t-.18)/.35)*sin(pi*t)**.35
    wave=(.038 if curls else .009)*env
    angle=t*(5.5*pi if curls else 2*pi)+j*.65+side*.35
    p.x+=side*wave*sin(angle);p.y+=wave*.65*cos(angle)
   width=.075 if j<4 else .082
   lock('Hair / '+style+' shaped layer '+str(side)+' '+str(j),ps,[.045,width,width*.94,width*.85,.037],[.012,.030,.026,.022,.010],j*.7)
 # Central nape coverage grows backwards from the crown, never a slit or blunt seam.
 for j in range(5):
  x=-.26+j*.13;endz=(1.55 if short else 1.23)+.028*cos(j*1.8)
  pts=[a.surface(x*.5,.22,.026),Vector((x*.85,.36,2.20)),Vector((x,.445,1.98)),Vector((x,.445,1.69)),Vector((x*.94,.38,1.44)),Vector((x*.90,.32,endz))]
  ps=a.sample(pts,96)
  if curls:
   for k,p in enumerate(ps):
    t=k/95;p.x+=.028*sin(t*5.5*pi+j*.8)*sin(pi*t);p.y+=.022*cos(t*5.5*pi+j*.8)*sin(pi*t)
  lock('Hair / '+style+' rear layer '+str(j),ps,[.035,.076,.079,.073,.045],[.013,.028,.024,.023,.010],j)
 if sweep:
  for j in range(3):
   pts=[a.surface(.11,-.25+j*.046,.035),Vector((.02,-.36+j*.018,2.26+j*.017)),Vector((-.18,-.395+j*.025,2.19+j*.025)),Vector((-.35,-.31+j*.028,2.05)),Vector((-.44,-.18+j*.04,1.81)),Vector((-.41,-.20+j*.045,1.48))]
   lock('Hair / rooted side fringe '+str(j),pts,[.025,.054,.053,.046,.024],[.009,.026,.024,.020,.010],j)

def curly_top(afro=False):
 a.setup();a.GROUP='hair';old.taper_donor();rng=random.Random(330)
 # Broad coherent clusters with shallow interlocking open curls; buried stems.
 count=58 if afro else 34
 for k in range(count):
  ph=k*pi*(3-sqrt(5));th=math.acos(1-(k+.5)/count*(1.10 if afro else .72))
  p=a.polar(th,ph,.055 if afro else .028);N=(p-a.C).normalized();A=Vector((cos(ph),sin(ph),0));B=N.cross(A).normalized()
  turn=rng.uniform(.9,1.55)*pi;start=rng.uniform(-pi,pi);r=rng.uniform(.052,.078)*(1 if afro else 1.06)
  pts=[]
  for t in np.linspace(0,1,18):
   q=start+turn*t;offset=A*(r*cos(q))+B*(r*.75*sin(q));lift=(.020 if afro else .008)+.032*sin(pi*t)
   pts.append(p+offset+N*lift)
  lock('Hair / interlocked curl '+str(k),pts,[.018,.042,.044,.032,.008],[.012,.026,.030,.024,.006],k*.71,root=.7)
 # Smaller curls lower down make the transition gradual rather than a large rim.
 for k in range(23):
  ph=2*pi*(k+.2)/23;th=(1.43 if afro else 1.22)-.13*max(0,cos(ph));p=a.polar(th,ph,.016);N=(p-a.C).normalized();A=Vector((cos(ph),sin(ph),0));B=N.cross(A)
  pts=[p+A*(.034*cos(q))+B*(.028*sin(q))+N*(.014*sin(i*pi/17)) for i,q in enumerate(np.linspace(-.9,2.1,18))]
  lock('Hair / transition curl '+str(k),pts,[.009,.022,.024,.017,.003],[.005,.013,.015,.011,.003],k,root=.5)

def build(style):
 if style in ['straight','curls','side-sweep','flow']:developed_loose(style)
 elif style in ['curly-top','afro']:clustered_curls(style=='afro')
 elif style in ['space-buns','twin-braids']:gathered(style)
 elif style in ['box-braids','locs']:braid_fall(style)
 elif style=='buzz':close_crop()
 else:old.build(style)

def developed_loose(style):
 """Use established cartoon root topology; reconstruct the falling silhouette."""
 from pathlib import Path
 import utils224 as u
 source=Path(__file__).parent.parent/'refinement224/baseline/Feminine-fair.blend'
 with bpy.data.libraries.load(str(source),link=False) as(src,dst):dst.objects=list(src.objects)
 for ob in dst.objects:
  if ob.get('component159')=='hair':bpy.context.scene.collection.objects.link(ob)
  else:u.delete(ob)
 u.bake(bpy.context.scene)
 curly=style=='curls';short=style=='flow';sweep=style=='side-sweep'
 for ob in list(bpy.context.scene.objects):
  if ob.get('component159')!='hair' or ob.type!='MESH':continue
  ob['catalogue226']=True;ob['source227']='209 cartoon root topology; reconstructed falling layers'
  inv=ob.matrix_world.inverted()
  try:section=int(ob.name.rsplit(' ',1)[1])
  except ValueError:section=0
  if curly and len(ob.data.vertices)==2018:
   # Round the flattened cross-section without inflating the whole silhouette.
   for ring in range(63):
    ids=list(range(1+ring*32,1+(ring+1)*32));points=np.array([(ob.matrix_world@ob.data.vertices[k].co)[:] for k in ids]);center=points.mean(0);off=points-center;values,axes=np.linalg.eigh(np.cov(off.T,bias=True));major=axes[:,-1];minor=axes[:,-2];weight=smooth((2.28-center[2])/.45)
    for k,delta in zip(ids,off):
     delta=delta-major*np.dot(delta,major)*.10*weight+minor*np.dot(delta,minor)*.38*weight;ob.data.vertices[k].co=inv@Vector(center+delta)
  for v in ob.data.vertices:
   p=ob.matrix_world@v.co;z=p.z;x=p.x;y=p.y
   f=smooth((1.94-z)/.34)
   extension=.06 if short else (.27 if curly else .34)
   p.z-=extension*f
   p.x*=1-(.08 if curly else .15)*f;p.y=.015+(p.y-.015)*(1-.19*f)
   if curly:
    w=smooth((2.40-z)/.40);side=1 if x>=0 else -1
    # Shared smooth field makes adjacent locks curl coherently; broad open curls.
    phase=(2.33-p.z)*18.5+1.4*y+side*.18+.55*sin(section*2.399)
    p.x+=side*(.028+.025*sin(phase))*w
    p.y+=.022*w*cos(phase+.5)*(-1 if y<-.08 else 1)
    p.z+=.008*w*sin(phase*.7+x*3)
   else:
    p.x+=.009*sin(8*f+y*5)*f
   if sweep:
    front=math.exp(-((y+.29)/.13)**2);upper=smooth((z-1.96)/.18)*(1-smooth((z-2.30)/.10))
    p.z-=.105*front*upper;p.y-=.018*front*upper
    p.z+=.10*f;p.x+=.018*f*sin(10*f+section*.6)
   # Curvature changes may never enter the immutable head support.
   dv=p-a.C
   if z>1.58 and not (short and len(ob.data.vertices)==2018):
    direction=Vector((dv.x/a.R.x,dv.y/a.R.y,dv.z/a.R.z)).normalized();theta=math.acos(max(-1,min(1,direction.z)));phi=math.atan2(direction.x,-direction.y)
    seated=head_surface(theta,phi,.004 if 'root' in ob.name.lower() else .014)
    if dv.length<(seated-a.C).length:p=seated
   v.co=inv@p
  if short and len(ob.data.vertices)==2018:
   # Seat complete cross-sections. Projecting individual vertices collapses
   # adjacent locks onto one surface and produces coplanar checkerboard patches.
   for ring in range(63):
    ids=list(range(1+ring*32,1+(ring+1)*32));ps=[ob.matrix_world@ob.data.vertices[k].co for k in ids];center=sum(ps,Vector())/32
    if center.z<1.40:continue
    radial=(center-a.C).normalized();required=0.
    for p in ps:
     dv=p-a.C;direction=Vector((dv.x/a.R.x,dv.y/a.R.y,dv.z/a.R.z)).normalized();theta=math.acos(max(-1,min(1,direction.z)));phi=math.atan2(direction.x,-direction.y);seated=head_surface(theta,phi,.008)
     required=max(required,(seated-a.C).length-dv.length)
    for k,p in zip(ids,ps):ob.data.vertices[k].co=inv@(p+radial*required)
   ob.data.vertices[0].co=sum((ob.data.vertices[k].co for k in range(1,33)),Vector())/32
   ob.data.vertices[-1].co=sum((ob.data.vertices[k].co for k in range(1+62*32,1+63*32)),Vector())/32
  ob.name=ob.name.replace('Bob',style.title())

def continuous_curls(afro=False):
 from mathutils import kdtree
 a.setup();a.GROUP='hair';rng=random.Random(702)
 for ob in list(bpy.context.scene.objects):
  if ob.name in ['Hair / Taper short sides','Hair / Taper fine direction']:bpy.data.objects.remove(ob,do_unlink=True)
 fade()
 guides=[]
 for k in range(72 if afro else 56):
  count=72 if afro else 56;ph=k*pi*(3-sqrt(5))+rng.uniform(-.2,.2);th=math.acos(1-(k+.5)/count*(1.15 if afro else .80));center=a.polar(th,ph,0);N=(center-a.C).normalized();A=Vector((cos(ph),sin(ph),0));B=N.cross(A);roll=rng.uniform(-1.1,1.1);aa=A*cos(roll)+B*sin(roll);bb=B*cos(roll)-A*sin(roll);size=rng.uniform(.037,.068);start=rng.uniform(-pi,pi);turn=rng.uniform(.85,1.55)*pi
  for t in np.linspace(0,1,45):
   p=center+aa*(size*cos(start+turn*t))+bb*(size*sin(start+turn*t));dv=p-a.C;scale=sqrt(sum((dv[i]/a.R[i])**2 for i in range(3)));guides.append(a.C+dv/scale)
 tree=kdtree.KDTree(len(guides))
 for i,p in enumerate(guides):tree.insert(p,i)
 tree.balance();verts=[];faces=[];colors=[];nu,nv=256,112
 for j in range(nv+1):
  t=j/nv
  for i in range(nu):
   ph=2*pi*i/nu;end=(1.85 if afro else 1.53)-(.40 if afro else .38)*max(0,cos(ph))+.018*sin(ph*11);th=.0001+end*t;p=a.polar(th,ph,0);dist=tree.find(p)[2]
   # Rounded broad ridges. A pole-invariant field prevents radial pinches.
   ridge=.026*math.exp(-(dist/.018)**2)-.006*math.exp(-((dist-.030)/.008)**2)
   broad=.012*sin(p.x*25+sin(p.z*13))*sin(p.y*27+p.z*9)
   pole=smooth(th/.14)
   height=(.052+(ridge+broad)*pole)*(1-smooth((t-.73)/.27))+.002
   if afro:height+=(.075+.012*sin(ph*7)*sin(th))*(1-smooth((t-.85)/.15))
   dv=(p-a.C).normalized();verts.append(tuple(p+dv*height));colors.append((1,1,1,1-smooth((t-.955)/.045)))
 for j in range(nv):
  for i in range(nu):x=j*nu+i;n=j*nu+(i+1)%nu;faces.append((x,n,n+nu,x+nu))
 faces.append(tuple(range(nu-1,-1,-1)));mat=a.material('Hair / rounded curly mass227',(.052,.020,.011),.34);ob=a.mesh('Hair / continuous rounded curls',verts,faces,mat,'hair')
 # Smooth the closest-guide switching seams without removing curl definition.
 bpy.context.view_layer.objects.active=ob;ob.select_set(True);mod=ob.modifiers.new('Rounded curl polish','SMOOTH');mod.factor=.50;mod.iterations=2;bpy.ops.object.modifier_apply(modifier=mod.name)
 co=ob.data.color_attributes.new(name='CurlDensity',type='FLOAT_COLOR',domain='POINT')
 for d,c in zip(co.data,colors):d.color=c
 bs=mat.node_tree.nodes['Principled BSDF'];attr=mat.node_tree.nodes.new('ShaderNodeVertexColor');attr.layer_name=co.name;mat.node_tree.links.new(attr.outputs['Alpha'],bs.inputs['Alpha']);mat.surface_render_method='DITHERED'

def fade():
 """Short geometry grain over a color-density field, with an actual skin fade."""
 rng=random.Random(727);nu,nv=192,45;v=[];f=[];rgba=[]
 def bounds(ph):
  front=max(0,cos(ph));return 1.08+.29*(1-front),1.17+.77*(1-front**2)
 for j in range(nv+1):
  t=j/nv
  for i in range(nu):
   ph=2*pi*i/nu;start,end=bounds(ph);th=start+(end-start)*t
   v.append(tuple(head_surface(th,ph,.0035)));rgba.append((1,1,1,.72*(1-smooth(t))**1.25*(1-smooth((cos(ph)-.60)/.25))))
 for j in range(nv):
  for i in range(nu):x=j*nu+i;n=j*nu+(i+1)%nu;f.append((x,n,n+nu,x+nu))
 mat=a.material('Hair / curly taper density227',(.049,.020,.012),.48);ob=a.mesh('Hair / curly taper foundation',v,f,mat,'hair');co=ob.data.color_attributes.new(name='Fade',type='FLOAT_COLOR',domain='POINT')
 for d,c in zip(co.data,rgba):d.color=c
 bs=mat.node_tree.nodes['Principled BSDF'];attr=mat.node_tree.nodes.new('ShaderNodeVertexColor');attr.layer_name='Fade';mat.node_tree.links.new(attr.outputs['Alpha'],bs.inputs['Alpha']);mat.surface_render_method='DITHERED'
 v=[];f=[]
 for k in range(12000):
  ph=rng.random()*2*pi;start,end=bounds(ph);t=rng.random()
  if rng.random()>1-smooth((cos(ph)-.60)/.25):continue
  if rng.random()>(1-t)**1.5:continue
  th=start+(end-start)*t;p=head_surface(th,ph,.005);q=head_surface(th+.012*(1-.55*t),ph+.003,.005);A=Vector((cos(ph),sin(ph),0))*.00075
  n=len(v);v.extend([tuple(p-A),tuple(p+A),tuple(q+A),tuple(q-A)]);f.append((n,n+1,n+2,n+3))
 a.mesh('Hair / short taper grain',v,f,a.material('Hair / short taper grain227',(.035,.012,.006),.43),'hair')

def clustered_curls(afro=False):
 """A small number of strands per packed curl cluster; roots buried in a core."""
 a.setup();a.GROUP='hair';rng=random.Random(517)
 for ob in list(bpy.context.scene.objects):
  if ob.name in ['Hair / Taper short sides','Hair / Taper fine direction']:bpy.data.objects.remove(ob,do_unlink=True)
 fade()
 mat=a.material('Hair / sculpted curl clusters227',(.077,.029,.015),.34)
 def edge(ph):return (1.70 if afro else 1.47)-(.64 if afro else .42)*max(0,cos(ph))**1.8
 def support(th,ph,lift=0):
  size=(.085 if afro else .025)+lift
  return head_surface(th,ph,size)
 # Core ends well inside the outer curls; it has no exposed forehead skirt.
 nu,nv=120,45;v=[];f=[]
 for j in range(nv+1):
  for i in range(nu):
   ph=2*pi*i/nu;th=.001+(edge(ph)-.045)*j/nv;v.append(tuple(support(th,ph,-.007)))
 for j in range(nv):
  for i in range(nu):x=j*nu+i;n=j*nu+(i+1)%nu;f.append((x,n,n+nu,x+nu))
 f.append(tuple(range(nu-1,-1,-1)));a.mesh('Hair / recessed curl core',v,f,mat,'hair')
 # Uniform area packing, modest irregularity, open hooks rather than closed rings.
 count=900 if afro else 380
 for k in range(count):
  ph=k*pi*(3-sqrt(5));th=math.acos(1-(k+.5)/count*(1-cos(edge(ph))))
  center=support(th,ph,.010);N=(center-a.C).normalized();A=Vector((cos(ph),sin(ph),0));B=N.cross(A).normalized();roll=rng.uniform(-pi,pi);AA=A*cos(roll)+B*sin(roll);BB=B*cos(roll)-A*sin(roll)
  radius=rng.uniform(.020,.032) if afro else rng.uniform(.030,.045);turn=rng.uniform(1.0,1.6)*pi;start=rng.random()*2*pi;pts=[]
  for t in np.linspace(0,1,38):
   q=start+turn*t;r=radius*(.8+.2*sin(pi*t));pts.append(center+AA*(r*cos(q))+BB*(r*.8*sin(q))+N*(-.026+.047*sin(pi*t)))
  a.tube('Hair / curl cluster '+str(k),pts,.0095 if afro else .0135,.008 if afro else .0105,mat,n=38,sides=12,taper=True,grooves=True)

def gathered_cap(high=True):
 from mathutils import kdtree
 a.setup();a.GROUP='hair';v=[];f=[];nu,nv=176,66;flow=[]
 for side in [-1,1]:
  target=Vector((side*.35,.13,2.30)) if high else a.polar(1.20,side*2.0,.025);unit=Vector((target.x/.50,(target.y-.015)/.425,(target.z-1.88)/.475)).normalized()
  for k in range(23):
   ph=side*(.055+k*(pi-.11)/22);end=1.06+.79*(1-max(0,cos(ph))**1.5);root=Vector((sin(end)*sin(ph),-sin(end)*cos(ph),cos(end)))
   flow += [root.lerp(unit,t).normalized() for t in np.linspace(0,1,65)]
 tree=kdtree.KDTree(len(flow))
 for i,p in enumerate(flow):tree.insert(p,i)
 tree.balance()
 for j in range(nv+1):
  t=j/nv
  for i in range(nu):
   ph=2*pi*i/nu;th=.001+t*(1.06+.79*(1-max(0,cos(ph))**1.5)+.008*sin(ph*19));side=1 if sin(ph)>=0 else -1
   unit=Vector((sin(th)*sin(ph),-sin(th)*cos(ph),cos(th)))
   target=Vector((side*.68,.35,.64 if high else .16)).normalized();AA=target.cross(Vector((0,0,1))).normalized();BB=target.cross(AA);q=math.atan2(unit.dot(BB),unit.dot(AA));distance=math.acos(max(-1,min(1,unit.dot(target))))
   dist=tree.find(unit)[2];relief=-.008*math.exp(-(dist/.025)**2)+.0015*cos(q*62+distance*2)*min(1,distance*4)
   lift=.005+.025*sin(pi*t)**.8+relief*sin(pi*t)**.4
   v.append(tuple(head_surface(th,ph,lift)))
 for j in range(nv):
  for i in range(nu):k=j*nu+i;n=j*nu+(i+1)%nu;f.append((k,n,n+nu,k+nu))
 f.append(tuple(range(nu-1,-1,-1)));a.mesh('Hair / paired gathered roots',v,f,a.M['hair'],'hair')

def plait(name,points,radius=.045,loc=False):
 ps=a.sample(points,130);arc=[0.]
 for i in range(1,len(ps)):arc.append(arc[-1]+(ps[i]-ps[i-1]).length)
 if loc:
  for i,p in enumerate(ps):
   t=i/129;p.x+=.006*sin(arc[i]*24)*sin(pi*t);p.y+=.005*sin(arc[i]*31+.8)*sin(pi*t)
  ob=a.tube(name,ps,lambda t:radius*(.93+.045*sin(t*31+.6))*(1-.20*t),radius*.81,n=130,sides=16,grooves=False)
  mat=a.material('Hair / loc texture227',(.12,.047,.026),.41);ob.data.materials.clear();ob.data.materials.append(mat);return
 frames=[]
 for i,p in enumerate(ps):
  T=(ps[min(129,i+1)]-ps[max(0,i-1)]).normalized();N=(p-a.C).normalized();N=(N-T*N.dot(T)).normalized()
  if N.length<.3:N=Vector((0,-1,0))
  B=T.cross(N).normalized();frames.append((N,B))
 for strand in range(3):
  pp=[]
  for i,p in enumerate(ps):
   t=i/129;q=arc[i]/.105*2*pi+strand*2*pi/3;r=radius*(1-.24*t);N,B=frames[i]
   pp.append(p+B*(r*.60*sin(q))+N*(r*.35*sin(2*q)))
  a.tube(name+' / woven '+str(strand),pp,lambda t:radius*.49*(1-.25*t)*min(1,.20+10*t),lambda t:radius*.42*(1-.25*t)*min(1,.20+10*t),n=130,sides=10,taper=False)
 end=ps[-1];T=(ps[-1]-ps[-3]).normalized();N,B=frames[-1]
 a.tube(name+' / tie',[end+N*(radius*.72*cos(q))+B*(radius*.72*sin(q)) for q in np.linspace(0,2*pi,32)],.006,.006,a.M['band'],n=32,sides=8,taper=False)
 a.tube(name+' / tapered brush',[end,end+T*.035,end+T*.065],radius*.57,radius*.44,n=20,sides=14,grooves=True)

def gathered(style,covered=False):
 a.setup();a.GROUP='hair';buns=style=='space-buns';gathered_cap(buns and not covered)
 for side in [-1,1]:
  # Raised, rooted direction guides converge into each real gather independently.
  target=Vector((side*.35,.32,1.88)) if buns and covered else Vector((side*.35,.13,2.30)) if buns else a.polar(1.20,side*2.0,.025)
  target_unit=Vector(((target.x)/.50,(target.y-.015)/.425,(target.z-1.88)/.475)).normalized()
  for k in range(23):
   ph=side*(.055+k*(pi-.11)/22);end=1.06+.79*(1-max(0,cos(ph))**1.5)
   root=Vector((sin(end)*sin(ph),-sin(end)*cos(ph),cos(end)));pts=[]
   for t in np.linspace(0,1,50):
    unit=root.lerp(target_unit,t).normalized();lift=.016+.021*sin(pi*t)
    pts.append(a.C+Vector(((.48+lift)*unit.x,(.405+lift)*unit.y,(.455+lift)*unit.z)))
   # Flow is carved into gathered_cap, not pasted on as wire-like ridges.
  if buns:
   center=target;a.sphere('Hair / bun body '+str(side),center,(.123,.112,.105),a.M['hair'])
   for j in range(4):
    pts=[]
    for t in np.linspace(0,1,60):
     q=t*1.8*pi+j*pi/2;z=-.080+.15*t;scale=sqrt(max(.06,1-(z/.105)**2));pts.append(center+Vector((.122*scale*cos(q),.112*scale*sin(q),z)))
    a.tube('Hair / bun wrap '+str(side)+' '+str(j),pts,.020,.012,n=60,sides=16,grooves=True)
  else:
   pts=[a.polar(1.20,side*2.0,.025),Vector((side*.44,.19,1.91)),Vector((side*.45,.06,1.69)),Vector((side*.40,-.17,1.46)),Vector((side*.32,-.25,1.23))]
   plait('Hair / twin braid '+str(side),pts,.064)
  pts=[a.polar(.98,side*.72,.022),Vector((side*.30,-.325,2.06)),Vector((side*.36,-.285,1.96)),Vector((side*.34,-.275,1.82))]
  lock('Hair / framing lock '+str(side),pts,[.012,.022,.023,.009],[.008,.012,.011,.004],phase=side)

def braid_fall(style):
 a.setup();a.GROUP='hair';loc=style=='locs';rng=random.Random(581)
 # Independent rectangular root sections fan into separate hanging braids.
 for side in [-1,1]:
  for j in range(21):
   ph=side*(.55+j*.123);y=-.24+j*.026;rootx=side*(.014+.030*(j%2));root=a.surface(rootx,y,.018)
   pts=[root,a.polar(.62,ph*.9,.028),a.polar(1.14,ph,.037),a.polar(1.73,ph,.033)]
   front=j<3;endz=(1.48 if loc else 1.16)+rng.uniform(-.065 if loc else -.035,.065 if loc else .035)
   pts += [Vector((side*.44*sin(abs(ph)),-.17 if front else -.33*cos(ph),1.46)),Vector((side*(.34 if front else .39)*sin(abs(ph)),-.25 if front else -.30*cos(ph),endz))]
   plait('Hair / '+style+' '+str(side)+' '+str(j),pts,.034 if loc else .039,loc)
 for j in range(7):
  x=-.25+j*.083;pts=[a.surface(x*.65,.25,.020),Vector((x,.38,2.13)),Vector((x,.445,1.91)),Vector((x,.40,1.64)),Vector((x*.9,.31,(1.47 if loc else 1.19)+.02*sin(j)))]
  plait('Hair / '+style+' rear '+str(j),pts,.032,loc)

def close_crop():
 a.setup();a.GROUP='hair';rng=random.Random(228)
 for ob in list(bpy.context.scene.objects):
  if ob.get('component159')=='hair':bpy.data.objects.remove(ob,do_unlink=True)
 def edge(ph):return 1.10+.73*(1-max(0,cos(ph))**3)
 nu,nv=192,64;v=[];f=[];rgba=[]
 for j in range(nv+1):
  for i in range(nu):
   ph=2*pi*i/nu;t=j/nv;th=.0001+edge(ph)*t;front=max(0,cos(ph))**5;fadeStart=.77+.19*front;density=.91*(1-smooth((t-fadeStart)/(1-fadeStart)))
   v.append(tuple(head_surface(th,ph,.004)));rgba.append((1,1,1,density))
 for j in range(nv):
  for i in range(nu):k=j*nu+i;n=j*nu+(i+1)%nu;f.append((k,n,n+nu,k+nu))
 f.append(tuple(range(nu-1,-1,-1)));mat=a.material('Hair / cropped density227',(.067,.027,.014),.49);ob=a.mesh('Hair / close crop support',v,f,mat,'hair');co=ob.data.color_attributes.new(name='Fade',type='FLOAT_COLOR',domain='POINT')
 for d,c in zip(co.data,rgba):d.color=c
 bs=mat.node_tree.nodes['Principled BSDF'];att=mat.node_tree.nodes.new('ShaderNodeVertexColor');att.layer_name='Fade';mat.node_tree.links.new(att.outputs['Alpha'],bs.inputs['Alpha']);mat.surface_render_method='DITHERED'
 v=[];f=[]
 for k in range(20000):
  ph=rng.random()*2*pi;th=math.acos(rng.uniform(cos(edge(ph)),1));t=th/edge(ph)
  if rng.random()>1-smooth((t-.74)/.26):continue
  p=head_surface(th,ph,.0055);q=head_surface(th+.010,ph+.003,.0055);A=Vector((cos(ph),sin(ph),0))*.00065;n=len(v);v += [tuple(p-A),tuple(p+A),tuple(q+A),tuple(q-A)];f.append((n,n+1,n+2,n+3))
 a.mesh('Hair / short crop grain',v,f,a.material('Hair / cropped grain227',(.032,.011,.005),.45),'hair')
