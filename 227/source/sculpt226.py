"""Original cartoon catalogue geometry. Shared Z-up coordinates, front -Y."""
import bpy,bmesh,math,random
import numpy as np
from mathutils import Vector
from math import sin,cos,pi,sqrt
C=Vector((0,.015,1.88));R=Vector((.48,.405,.455))
GROUP='hair';M={}
def material(name,rgb,rough=.3,metal=0):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*rgb,1);b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal
 return m
def setup():
 global M
 M={'hair':material('Hair / chestnut226',(.12,.047,.026),.29),'shine':material('Hair / chestnut light226',(.145,.062,.035),.31),'dark':material('Hair / root226',(.072,.026,.015),.34),'band':material('Hair / ties226',(.022,.024,.032),.35),'fabric':material('Headwear / fabric226',(.065,.115,.18),.55),'hem':material('Headwear / seam226',(.15,.24,.29),.48),'gold':material('Accessory / warm metal226',(.65,.43,.17),.27,.6),'pink':material('Accessory / pink226',(.42,.10,.22),.35),'mint':material('Accessory / mint226',(.10,.42,.29),.3),'frame':material('Glasses / frame226',(.025,.027,.035),.26)}
def mesh(name,v,f,mat,group=None):
 me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(ob);ob['component159']=group or GROUP;ob['catalogue226']=True;me.materials.append(mat)
 for p in me.polygons:p.use_smooth=True
 return ob
def sample(points,n=70):
 ps=[Vector(p) for p in points];out=[]
 for a in np.linspace(0,len(ps)-1,n):
  i=min(len(ps)-2,int(a));t=a-i;p0=ps[max(i-1,0)];p1=ps[i];p2=ps[i+1];p3=ps[min(i+2,len(ps)-1)]
  out.append(.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t))
 return out
def tube(name,points,width,depth=None,mat=None,n=70,sides=12,taper=True,grooves=False,group=None):
 ps=sample(points,n) if len(points)<n else [Vector(p) for p in points];depth=width if depth is None else depth;v=[];f=[]
 for i,p in enumerate(ps):
  t=i/(len(ps)-1);tangent=(ps[min(i+1,len(ps)-1)]-ps[max(0,i-1)]).normalized();ref=Vector((0,1,0));a=tangent.cross(ref).normalized()
  if a.length<.5:a=tangent.cross(Vector((1,0,0))).normalized()
  b=tangent.cross(a).normalized();fall=max(.04,min(1,(1-t)/.15))**.55 if taper else 1
  if taper:fall*=min(1,.32+t*14)
  w=width(t) if callable(width) else width;d=depth(t) if callable(depth) else depth
  for j in range(sides):
   q=2*pi*j/sides;ridge=1+(.07*cos(q*6+.2*sin(t*6)) if grooves else 0);v.append(tuple(p+fall*ridge*(a*(w*cos(q))+b*(d*sin(q)))))
 for i in range(len(ps)-1):
  for j in range(sides):a=i*sides+j;b=i*sides+(j+1)%sides;f.append((a,b,b+sides,a+sides))
 f.extend([tuple(range(sides-1,-1,-1)),tuple((len(ps)-1)*sides+j for j in range(sides))]);return mesh(name,v,f,mat or M['hair'],group)
def sphere(name,loc,scale,mat,group=None):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=20,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o['component159']=group or GROUP;o['catalogue226']=True;o.data.materials.append(mat)
 for p in o.data.polygons:p.use_smooth=True
 return o
def surface(x,y,extra=.025):
 z=C.z+R.z*sqrt(max(.001,1-(x/R.x)**2-((y-C.y)/R.y)**2));return Vector((x,y,z+extra))
def polar(theta,phi,extra=.02):
 return C+Vector(((R.x+extra)*sin(theta)*sin(phi),-(R.y+extra)*sin(theta)*cos(phi),(R.z+extra)*cos(theta)))
def scalp(kind='normal',covered=False):
 nu,nv=112,35;v=[];f=[]
 for j in range(nv+1):
  t=j/nv
  for i in range(nu):
   ph=2*pi*i/nu;front=max(0,cos(ph));end=1.94-.94*front**1.6
   if kind=='buzz':end=1.79-.73*front**1.8
   theta=.007+t*end;lift=.012 if covered or kind=='buzz' else .023+.012*sin(theta)**2
   relief=(.0007 if kind=='buzz' else .0018)*sin(ph*40+theta*5)*sin(theta)*sin(pi*t)
   v.append(tuple(polar(theta,ph,lift+relief)))
 for j in range(nv):
  for i in range(nu):a=j*nu+i;b=j*nu+(i+1)%nu;f.append((a,b,b+nu,a+nu))
 f.append(tuple(range(nu-1,-1,-1)));o=mesh('Hair / rooted coverage',v,f,M['dark'] if kind=='buzz' else M['hair']);sol=o.modifiers.new('Hairline inward edge','SOLIDIFY');sol.thickness=.008;sol.offset=-1
 return o
def root_sections(gather=False,covered=False):
 for side in [-1,1]:
  for j in range(9):
   y=-.31+j*.073;root=surface(side*.018,y,.026);ph=.60+j*.315
   pts=[root,polar(.6,side*ph,.032),polar(1.0,side*ph,.032),polar(1.53,side*ph,.027)]
   if gather:pts=[root,polar(.8,side*ph,.032),polar(1.10,side*2.0,.032),Vector((side*.18,.34,2.06))]
   tube('Hair / swept root %s %s'%(side,j),pts,.040,.016,n=45,sides=12,grooves=True)
def long_hair(style,covered=False):
 scalp(covered=covered);is_curl=style=='curls';short=style=='flow';sweep=style=='side-sweep'
 for side in [-1,1]:
  count=11 if is_curl else 10
  for j in range(count):
   ph=.70+j*(2.36/(count-1));front=j<2
   root=surface((.10 if sweep else .018)+side*.009,-.32+j*.063,.010 if covered else .017)
   p1=polar(.66,side*ph,.014 if covered else .023);p2=polar(1.2,side*ph,.014 if covered else .035)
   p3=polar(1.67,side*ph,.017 if covered else .032);endz=(1.57 if short else 1.21)+.035*sin(j*2.2)
   endx=side*(.29 if front else .37)*sin(ph);endy=(-.235 if front else .24-.06*cos(ph))
   pts=[root,p1,p2,p3,Vector((side*(.42 if covered else .44)*sin(ph),(-.17 if front else .32),1.48)),Vector((endx,endy,endz))]
   ps=sample(pts,90)
   for k,p in enumerate(ps):
    t=k/(len(ps)-1);fall=max(0,(t-.37)/.63)
    p.x+=side*((.036 if is_curl else .006)*sin(fall*(4.2 if is_curl else 1.5)*pi+j*.35))*sin(pi*min(1,fall))
    p.y+=(.035 if is_curl else .004)*sin(fall*4.2*pi+j*.3)*sin(pi*min(1,fall))
   tube('Hair / flowing lock %s %02d'%(side,j),ps,.041 if is_curl else .040,.025 if is_curl else .020,n=90,sides=18,grooves=True)
   for d in [-.018,.018]:
    detail=[p+Vector((d,(-.025 if front else .024),0)) for p in ps[30:]]
    tube('Hair / engraved strand %s %s %s'%(side,j,d),detail,.0026,.0018,M['shine'],n=len(detail),sides=6)
 # Rooted framing layers cover the shell edge and join the main lengths.
 for side in [-1,1]:
  for j in range(3):
   root=surface(.018+side*.007,-.34+j*.018,.015)
   pts=[root,Vector((side*(.16+j*.032),-.365+j*.018,2.15+j*.025)),Vector((side*(.32+j*.022),-.32+j*.018,2.02)),Vector((side*.43,-.22+j*.016,1.80)),Vector((side*.37,-.23+j*.02,1.40+j*.035))]
   tube('Hair / face framing '+str(side)+str(j),pts,.031,.016,n=65,sides=16,grooves=True)
 if is_curl:
  # Small irregular S-shaped crown locks, never closed rings.
  for side in [-1,1]:
   for j in range(10):
    ph=.45+j*.26;pts=[surface(side*.035,-.30+j*.06,.025),polar(.55,side*(ph+.04),.038),polar(.85,side*(ph-.06),.042),polar(1.15,side*(ph+.05),.042)]
    tube('Hair / crown curl '+str(side)+str(j),pts,.026,.020,n=40,sides=12,grooves=True)
 if sweep:
  for j in range(5):
   pts=[surface(.14,-.22+j*.035,.04),surface(-.12,-.30+j*.018,.04),Vector((-.32,-.337,2.15-j*.012)),Vector((-.43,-.26,1.99-j*.02)),Vector((-.46,-.16,1.73-j*.02))]
   tube('Hair / side fringe %s'%j,pts,.043,.022,n=65,sides=16,grooves=True)
def curls_top(afro=False,covered=False):
 scalp(covered=covered);rng=random.Random(226)
 for ring in range(1,7 if afro else 5):
  theta=.16+ring*(.23 if afro else .19);count=7+ring*5
  for j in range(count):
   ph=2*pi*(j+.47*(ring%2))/count;theta2=theta+ rng.uniform(-.035,.035)
   if not afro and cos(ph)>.5:theta2+=.06
   p=polar(theta2,ph,.014 if covered else (.065 if afro else .05));a=Vector((cos(ph),sin(ph),0));b=Vector((cos(theta2)*sin(ph),-cos(theta2)*cos(ph),-sin(theta2)));pts=[]
   for t in np.linspace(0,1,32):
    q=-.4+1.15*pi*t;pts.append(p+a*(.037*sin(q))+b*(.045*(t-.5))+Vector((0,0,.021*sin(pi*t))))
   tube('Hair / curl cluster %s %s'%(ring,j),pts,.022 if covered else .032,.025,n=32,sides=10,grooves=True)
def braid(name,path,radius=.055,locs=False):
 ps=sample(path,95)
 if locs:
  for k,p in enumerate(ps):p.x+=.006*sin(k*.19);p.y+=.004*sin(k*.25)
  tube(name,ps,radius,radius*.82,n=95,sides=14,grooves=True);return
 for strand in range(3):
  pp=[]
  for i,p in enumerate(ps):
   t=i/(len(ps)-1);q=t*2*pi*6+strand*2*pi/3;r=radius*(1-.28*t)
   pp.append(p+Vector((r*.60*sin(q),r*.40*cos(q),0)))
  tube(name+' / interlace '+str(strand),pp,lambda t:radius*.51*(1-.35*t),lambda t:radius*.45*(1-.35*t),n=95,sides=10,grooves=True)
 tip=ps[-1];tube(name+' / tie',[tip+Vector((0,0,.04)),tip+Vector((0,0,.025))],radius*.70,radius*.62,M['band'],n=5,sides=16,taper=False)
 tube(name+' / brush end',[tip+Vector((0,0,.025)),tip+Vector((.007,0,-.065))],radius*.57,radius*.43,n=14,sides=14,grooves=True)
def braided(style,covered=False):
 scalp(covered=covered)
 if style=='twin-braids':
  root_sections(True,covered)
  for side in [-1,1]:
   pts=[surface(side*.17,-.26,.028),polar(.9,side*1.18,.035),polar(1.50,side*1.40,.03),Vector((side*.46,-.005,1.65)),Vector((side*.36,-.21,1.39)),Vector((side*.29,-.26,1.14))]
   braid('Hair / Dutch braid '+str(side),pts,.064)
 else:
  for side in [-1,1]:
   for j in range(9):
    ph=.63+j*.30;front=j<2;pts=[surface(side*(.025+(j%2)*.07),-.30+j*.075,.026),polar(.8,side*ph,.028),polar(1.45,side*ph,.032),polar(1.80,side*ph,.040),Vector((side*.37*sin(ph),-.22 if front else .33,1.28)),Vector((side*.30*sin(ph),-.24 if front else .27,1.13+.04*sin(j*2)))];braid('Hair / '+style+str(side)+' '+str(j),pts,.030 if style=='box-braids' else .038,style=='locs')
def buns(covered=False):
 scalp(covered=covered);root_sections(True,covered)
 for side in [-1,1]:
  center=Vector((side*(.28 if covered else .37),.30 if covered else .10,1.86 if covered else 2.28))
  sphere('Hair / bun core '+str(side),center,(.115,.105,.11),M['hair'])
  for k in range(6):
   pts=[]
   for t in np.linspace(0,1,50):
    q=t*1.8*pi+k*.55;pts.append(center+Vector((.11*cos(q),.10*sin(q),-.075+.15*t)))
   tube('Hair / wrapped bun '+str(side)+' '+str(k),pts,.021,.018,n=50,sides=12,grooves=True)
def buzz(covered=False):
 scalp('buzz',covered);rng=random.Random(99)
 for i in range(850):
  ph=rng.random()*2*pi;theta=rng.uniform(.09,1.78-.76*max(0,cos(ph))**1.8);p=polar(theta,ph,.014);q=polar(theta+.016,ph+.007,.015)
  tube('Hair / buzz grain %04d'%i,[p,q],.0018,.0014,M['shine'] if i%3==0 else M['dark'],n=3,sides=5,taper=False)
HAIR=['straight','curls','space-buns','twin-braids','box-braids','side-sweep','buzz','curly-top','flow','afro','locs']
def hair(style,covered=False):
 global GROUP;GROUP='hair';setup()
 if style in ['straight','curls','side-sweep','flow']:long_hair(style,covered)
 elif style in ['twin-braids','box-braids','locs']:braided(style,covered)
 elif style=='space-buns':buns(covered)
 elif style=='buzz':buzz(covered)
 else:curls_top(style=='afro',covered)
def grid(name,fn,nu,nv,mat,thickness=.008,closed=False,group=None):
 v=[tuple(fn(i/nu,j/nv)) for j in range(nv+1) for i in range(nu+1)];f=[]
 for j in range(nv):
  for i in range(nu):a=j*(nu+1)+i;f.append((a,a+1,a+nu+2,a+nu+1))
 ob=mesh(name,v,f,mat,group)
 if thickness:mod=ob.modifiers.new('Sewn shell thickness','SOLIDIFY');mod.thickness=thickness;mod.offset=-1
 return ob
def hat(style):
 global GROUP;GROUP='headgear';setup()
 if style=='beanie':
  def cap(a,t):
   theta=.01+1.38*t;ph=a*2*pi;return Vector((.52*sin(theta)*sin(ph),.015-.445*sin(theta)*cos(ph),1.91+.51*cos(theta)+.025*sin(ph)*sin(pi*t)))
  grid('Beanie / knitted crown',cap,96,32,M['fabric'],.018)
  for j in range(60):
   ph=2*pi*j/60;pts=[cap(j/60,t)+Vector((sin(ph)*.003,-cos(ph)*.003,0)) for t in np.linspace(.09,.93,35)];tube('Beanie / knit rib '+str(j),pts,.003,.002,M['hem'],n=35,sides=5,taper=False)
  def cuff(a,t):
   ph=a*2*pi;z=2.035+.082*t;rx=.514-.01*t;return (rx*sin(ph),.015-(.443-.008*t)*cos(ph),z+.015*sin(ph))
  grid('Beanie / folded cuff',cuff,96,10,M['fabric'],.022)
 elif style in ['bucket','cowboy']:
  cow=style=='cowboy'
  def crown(a,t):
   ph=a*2*pi;rr=(.52-.11*t)+.010*sin(pi*t);z=2.07+.38*t
   if cow:z-=.055*t**4*cos(ph)**2
   return (rr*sin(ph),.015-(rr*.87)*cos(ph),z)
  grid(style+' / crown',crown,96,24,M['fabric'],.014)
  grid(style+' / top',lambda a,t:(.41*t*sin(a*2*pi),.015-.357*t*cos(a*2*pi),2.45+(.018*(1-t*t) if not cow else -.075*(1-(t*sin(a*2*pi))**2))),96,16,M['fabric'],.012)
  def brim(a,t):
   ph=a*2*pi;rx=.52+(.20 if cow else .13)*t;ry=.453+(.18 if cow else .12)*t;z=2.07+(.11*sin(ph)**2-.035*cos(ph)**2)*t*t if cow else 2.07-.11*t+.018*sin(ph*3)*t*t
   return (rx*sin(ph),.015-ry*cos(ph),z)
  grid(style+' / brim',brim,128,18,M['fabric'],.013)
  for t in [.75,.95]:tube(style+' / brim stitch '+str(t),[Vector(brim(a,t))+Vector((0,0,.006)) for a in np.linspace(0,1,129)],.0023,.0023,M['hem'],n=129,sides=5,taper=False)
  tube(style+' / crown band',[Vector(crown(a,.075))+Vector((sin(a*2*pi)*.006,-cos(a*2*pi)*.006,0)) for a in np.linspace(0,1,129)],.014,.012,M['hem'],n=129,sides=8,taper=False)
 elif style in ['headband','ears']:
  def band(a,t):
   ph=a*2*pi;theta=1.10+.13*t;return polar(theta,ph,.045)
  if style=='headband':
   grid('Headband / cloth',band,128,8,M['fabric'],.014)
   for t in [0,1]:tube('Headband / stitched edge '+str(t),[band(a,t) for a in np.linspace(0,1,129)],.003,.003,M['hem'],n=129,sides=6,taper=False)
  else:
   tube('Ears / crown band',[(.54*sin(q),.04,1.90+.52*cos(q)) for q in np.linspace(-1.37,1.37,70)],.014,.010,M['fabric'],n=70,sides=10,taper=False)
  if style=='headband':
   for side in [-1,1]:tube('Headband / knot tail '+str(side),[(side*.025,.445,1.99),(side*.10,.45,1.92),(side*.14,.43,1.83)],.025,.010,M['fabric'],n=30,sides=12)
  else:
   for side in [-1,1]:
    pts=[(side*.27,.015,2.31),(side*.39,.01,2.56),(side*.48,.02,2.25)];v=[(p[0],p[1]-.05,p[2]) for p in pts]+[(p[0],p[1]+.05,p[2]) for p in pts];ob=mesh('Ears / soft shell '+str(side),v,[(0,1,2),(3,5,4),(0,3,4,1),(1,4,5,2),(2,5,3,0)],M['fabric']);mod=ob.modifiers.new('Rounded ear','BEVEL');mod.width=.025;mod.segments=4;mesh('Ears / inner '+str(side),[(side*.31,-.043,2.31),(side*.39,-.044,2.49),(side*.445,-.043,2.29)],[(0,1,2)],M['pink'])
 elif style=='pashmina':pashmina()
def old_pashmina():
 # One rectangular scarf laid over the head; continuous into its two hanging ends.
 path=sample([(-.25,-.25,.96),(-.40,-.12,1.46),(-.57,.015,1.88),(-.49,.015,2.19),(0,.015,2.47),(.49,.015,2.19),(.57,.015,1.88),(.40,-.12,1.46),(.25,-.25,.99)],161)
 def drape(a,t):
  i=min(159,int(a*160));p=path[i].lerp(path[i+1],a*160-i);end=abs(2*a-1);w=.77*(1-end**3)+.16*end**3
  p.y+=(t-.5)*w;p.z-=.15*(2*t-1)**2*(1-end)**.4
  p.x+=.017*sin(t*4*pi+a*5)*max(0,(end-.35)/.65);p.y+=.014*sin(t*4*pi+a*3)*end
  return p
 grid('Pashmina / continuous drape',drape,160,40,M['fabric'],.014)
 for t in [.015,.985]:tube('Pashmina / selvage '+str(t),[drape(a,t) for a in np.linspace(0,1,161)],.008,.006,M['hem'],n=161,sides=8,taper=False)
 for a in [0,1]:
  for j in range(13):
   p=drape(a,j/12);tube('Pashmina / fringe '+str(a)+str(j),[p,p+Vector((.004*sin(j),.004*cos(j),-.045))],.0028,.0028,M['hem'],n=7,sides=5)
 for a in [.04,.075,.11,.89,.925,.96]:tube('Pashmina / woven border '+str(a),[drape(a,t)+Vector((0,-.003,.004)) for t in np.linspace(0,1,42)],.003,.002,M['hem'],n=42,sides=6,taper=False)
def pashmina():
 # Continuous loft from face opening over crown to settled rear cape.
 guide=sample([(-.31,.78,1.57),(.08,.91,1.57),(.51,.65,1.50),(.54,.24,1.36),(.36,0,1.20)],81)
 def hood(a,t):
  i=min(79,int(t*80));g=guide[i].lerp(guide[i+1],t*80-i);q=(a-.5)*pi
  return Vector(((.60-.27*t**3)*sin(q),g.x+.020*cos(a*5*pi)*sin(pi*t)*sin(q)**2,g.z+g.y*cos(q)+.025*cos(3*q)*t**5))
 grid('Pashmina / head shoulder drape',hood,88,80,M['fabric'],.014)
 tube('Pashmina / face selvage',[hood(a,0) for a in np.linspace(0,1,89)],.009,.006,M['hem'],n=89,sides=8,taper=False)
 for side in [-1,1]:
  def end(a,t):
   x=side*(.53*(1-t)+.27*t+(a-.5)*.14);y=-.31+.05*t+.018*sin(a*3*pi)*t;z=1.57-.58*t+.008*sin(a*pi*3)*t;return Vector((x,y,z))
  grid('Pashmina / hanging end '+str(side),end,24,50,M['fabric'],.012)
  for aa in [.04,.96]:tube('Pashmina / end hem '+str(side)+str(aa),[end(aa,t) for t in np.linspace(0,1,60)],.004,.003,M['hem'],n=60,sides=6,taper=False)
  for j in range(12):
   p=end(j/11,1);tube('Pashmina / fringe '+str(side)+str(j),[p,p+Vector((.003*sin(j),.003*cos(j),-.044))],.0026,.0026,M['hem'],n=7,sides=5)
  for t in [.70,.78,.85,.92]:tube('Pashmina / end weave '+str(side)+str(t),[end(aa,t)+Vector((0,-.006,0)) for aa in np.linspace(0,1,30)],.0025,.002,M['hem'],n=30,sides=5,taper=False)
 # Woven lines follow the drape itself rather than a floating cross-neck bar.
 for k in range(5):
  t=.20+k*.145
  tube('Pashmina / woven drape '+str(k),[hood(aa,t)+Vector((0,.002,.003)) for aa in np.linspace(.05,.95,80)],.0018,.0018,M['hem'],n=80,sides=5,taper=False)
def eyewear(style):
 global GROUP;GROUP='glasses';setup();lens=material('Glasses / transmitting lens226',(.83,.90,.94),.08);bs=lens.node_tree.nodes['Principled BSDF'];bs.inputs['Transmission Weight'].default_value=1;bs.inputs['IOR'].default_value=1.25
 for side in [-1,1]:
  coords=[]
  for t in np.linspace(0,2*pi,81):
   if style=='heart':x=.0088*16*sin(t)**3;z=.0088*(13*cos(t)-5*cos(2*t)-2*cos(3*t)-cos(4*t))
   else:
    power=.55 if style in ['wayfarer','wraparound','reading'] else .9;x=.135*math.copysign(abs(cos(t))**power,cos(t));z=(.073 if style=='reading' else .095)*math.copysign(abs(sin(t))**power,sin(t))
    if style=='cat-eye':z+=.22*(side*x)+.015*max(0,side*x/.135)**3
    if style=='kaleidoscope':x=.135*cos(round(t/(pi/3))*(pi/3));z=.105*sin(round(t/(pi/3))*(pi/3))
   xx=side*.16+x;y=-.435+.14*(abs(xx)/.48)**2;coords.append(Vector((xx,y,1.900+z)))
  if style=='kaleidoscope':coords=sample(coords,81)
  tube('Glasses / '+style+' frame '+str(side),coords,.009 if style=='reading' else .013,.010,M['gold'] if style=='reading' else M['frame'],n=len(coords),sides=10,taper=False)
  # Lens surface and a real second surface, not an opacity-painted pane.
  center=Vector((side*.16,-.435+.14*(.16/.48)**2,1.900));verts=[tuple(center)]+[tuple(center+(p-center)*.92+Vector((0,.004,0))) for p in coords[:-1]];faces=[(0,j+1,(j+1)%(len(verts)-1)+1) for j in range(len(verts)-1)];ob=mesh('Glasses / '+style+' lens '+str(side),verts,faces,lens,'lenses');sol=ob.modifiers.new('Lens thickness','SOLIDIFY');sol.thickness=.009
  tube('Glasses / temple '+str(side),[(side*.295,-.382,1.925),(side*.405,-.23,1.925),(side*.487,-.02,1.915),(side*.477,.10,1.895)],.009,.009,M['frame'],n=36,sides=8,taper=False)
 tube('Glasses / bridge',[(-.028,-.432,1.915),(0,-.440,1.93),(.028,-.432,1.915)],.008,.008,M['frame'],n=20,sides=8,taper=False)
def extra(style):
 global GROUP;GROUP='extra';setup()
 if style=='sprout':
  tube('Sprout / stem',[(.1,0,2.36),(.11,-.005,2.46),(.08,0,2.51)],.009,.008,M['mint'],n=25,sides=8,taper=False)
  for side in [-1,1]:
   def leaf(a,t):return (.09+side*.17*t,.015+(a-.5)*.10*sin(pi*t),2.49+.04*sin(pi*t)-.015*t)
   grid('Sprout / leaf '+str(side),leaf,12,22,M['mint'],.006,group='extra')
 else:
  for side in [-1,1]:
   for j in range(4):
    x=side*(.15+j*.055);z=1.88+.018*j;y=C.y-R.y*sqrt(max(.01,1-(x/R.x)**2-((z-C.z)/R.z)**2))-.008
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.012 if j else .018,location=(x,y,z));o=bpy.context.object;o.name='Face gem / '+str(side)+' '+str(j);o['component159']='extra';o['catalogue226']=True;o.scale.y=.45;o.data.materials.append(M['gold'] if j%2 else M['pink'])
