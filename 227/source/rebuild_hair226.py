"""Second construction: scalp-tangent ribbons, actual existing taper donor."""
import bpy,math,random
import numpy as np
from mathutils import Vector
from math import sin,cos,pi,sqrt
import sculpt226 as a
from pathlib import Path
P=Path(__file__).parent
def ribbon(name,points,width=.055,thick=.018,taper=True,curl=False):
 ps=a.sample(points,100);v=[];faces=[];rows=100;cols=20
 prev=None
 for i,p in enumerate(ps):
  t=i/(rows-1);tangent=(ps[min(i+1,rows-1)]-ps[max(i-1,0)]).normalized()
  ref=Vector((p.x/.48**2,(p.y-.015)/.405**2,max(0,p.z-1.88)/.455**2)).normalized()
  normal=(ref-tangent*ref.dot(tangent)).normalized()
  if normal.length<.2:normal=Vector((0,-1,0))
  across=tangent.cross(normal).normalized()
  if curl:
   roll=.42*sin(t*3*pi);normal,across=normal*cos(roll)+across*sin(roll),across*cos(roll)-normal*sin(roll)
  if prev is not None and across.dot(prev)<0:across=-across;normal=-normal
  prev=across
  tip=max(.035,min(1,(1-t)/.10))**.48 if taper else 1
  root=min(1,.75+t*8)
  for j in range(cols):
   q=2*pi*j/cols;relief=1+.035*cos(q*8+t*4);pt=p+across*(width*cos(q)*tip*root)+normal*(thick*sin(q)*relief*tip)
   # Upper sections lie outside the immutable head support. This projection is
   # limited to the rooted crown, not free lengths or shoulder contact regions.
   if pt.z>1.72 and t<.62:
    dv=pt-a.C;scale=sqrt(sum((dv[k]/(a.R[k]+.006))**2 for k in range(3)))
    if scale<1:pt=a.C+dv/max(.01,scale)
   v.append(tuple(pt))
 for i in range(rows-1):
  for j in range(cols):k=i*cols+j;n=i*cols+(j+1)%cols;faces.append((k,n,n+cols,k+cols))
 faces.extend([tuple(range(cols-1,-1,-1)),tuple((rows-1)*cols+j for j in range(cols))]);return a.mesh(name,v,faces,a.M['hair'],'hair')
def long(style,covered=False):
 a.setup();a.GROUP='hair';curl=style=='curls';short=style=='flow';sweep=style=='side-sweep';rng=random.Random(226)
 part=.11 if sweep else .04
 # Longitudinal part: transverse sheets wrap the cranium, then fall under gravity.
 for side in [-1,1]:
  for j in range(11):
   y=-.337+j*.066;section=sqrt(max(.01,1-((y-.015)/.433)**2));rx=.50*section;rz=.48*section;theta0=math.asin(min(.90,part/max(.01,rx)));points=[]
   for t in np.linspace(0,1,38):
    theta=theta0*side+(1.75-theta0*side)*t;x=side*rx*sin(theta);z=1.88+rz*cos(theta);yy=y+.009*sin(pi*t)*sin(j)
    points.append(Vector((x,yy,z)))
   # Roots stay on the part. Rear rows fan subtly around the back of the head.
   points[0]=Vector((part,y,1.88+rz*cos(theta0)))
   front=j<2;endz=(1.57 if short else 1.18)+.025*sin(j*1.7)
   p=points[-1];endx=side*(.31+.07*sin(j/10*pi));endy=(-.235 if front else .10+.18*(j/10));shoulder=Vector((side*(.43 if front else .44)*section,(-.18 if front else y*.87),1.47))
   points=a.sample(points,55)+a.sample([p,shoulder,Vector((endx,endy,endz))],45)[1:]
   if curl:
    for k,p in enumerate(points):
     t=k/(len(points)-1);f=max(0,(t-.26)/.74);amp=.027*sin(pi*min(1,f))+.008
     p.x+=side*amp*sin(f*(4.8*pi)+j*.40);p.y+=amp*.8*sin(f*4.8*pi+j*.40+pi/2)
   ribbon('Hair / '+style+' section '+str(side)+' '+str(j),points,.044 if curl else .042,.027 if curl else .015,curl=curl)
 # Join the rear part into a rounded crown instead of an open central slit.
 for j in range(9):
  x=-.34+j*.085;extent=sqrt(max(.1,1-(x/.51)**2));endz=1.56 if short else 1.25;pts=[a.surface(x,.23,.024),Vector((x,.015+.42*extent,2.06)),Vector((x*.98,.015+.43*extent,1.75)),Vector((x*.90,.32,max(1.43,endz+.055))),Vector((x*.86,.28,endz+.02*cos(j)))]
  ribbon('Hair / nape fall '+str(j),pts,.052,.018,curl=curl)
 if sweep:
  for j in range(4):
   pts=[a.surface(.13,-.27+j*.03,.025),a.surface(-.04,-.33+j*.02,.025),Vector((-.26,-.35,2.13-j*.015)),Vector((-.39,-.26,1.98-j*.015)),Vector((-.42,-.18,1.67))];ribbon('Hair / sweeping fringe '+str(j),pts,.029,.014)
def taper_donor():
 path=P.parent/'refinement224/scenes/Masculine-taper.blend'
 if Path(bpy.data.filepath)==path:
  # This source is already open; retain these donor objects during removal.
  return
 with bpy.data.libraries.load(str(path),link=False) as(src,dst):dst.objects=[n for n in src.objects if n in ['Hair / Taper short sides','Hair / Taper fine direction']]
 for ob in dst.objects:
  bpy.context.scene.collection.objects.link(ob);ob['catalogue226']=True;ob['taper_source']='224 exact selected214 fade'
def curly(afro=False,covered=False):
 a.setup();a.GROUP='hair';taper_donor();rng=random.Random(42)
 # Offset, irregularly packed curls cover crown and blend into the preserved fade.
 count=94 if afro else 48
 for k in range(count):
  ph=k*pi*(3-sqrt(5));theta=math.acos(1-(k+.5)/count*(1.02 if afro else .66));root=a.polar(theta,ph,.022);normal=(root-a.C).normalized();az=Vector((cos(ph),sin(ph),0));down=normal.cross(az).normalized();size=(.075 if afro else .090)*rng.uniform(.85,1.12);pts=[]
  for t in np.linspace(0,1,44):
   turn=2.1*pi*t+k*.2;lift=sin(pi*t)**.65
   # A broad flowing S lock: no closed macaroni ring or isolated ball.
   pts.append(root+az*(size*.34*sin(turn))+down*(size*1.65*(t-.5))+normal*((.065 if afro else .050)*lift))
  ribbon('Hair / open curl '+str(k),pts,.037 if afro else .041,.026,taper=True)
 # Front edge curls tuck into the mass and break its outline, not into repeated rings.
 for k in range(8):
  ph=-.95+k*.27;pts=[a.polar(.88,ph,.035),a.polar(1.0,ph+.05,.055),a.polar(1.10,ph+.08,.035)];ribbon('Hair / fringe curl '+str(k),pts,.033,.021)
def buzz():
 a.setup();a.GROUP='hair';taper_donor();rng=random.Random(312)
 # Dense, short directional strokes rather than a shiny bald cap.
 for i in range(2500):
  ph=rng.random()*2*pi;theta=math.acos(rng.uniform(.32,1));p=a.polar(theta,ph,.010);q=a.polar(theta+.022,ph+.012,.012);a.tube('Hair / close grain '+str(i),[p,q],.0028,.0018,a.M['dark'],n=3,sides=5,taper=False)
def gathered_roots():
 path=P.parent/'refinement224/scenes/Feminine-cap.blend'
 with bpy.data.libraries.load(str(path),link=False) as(src,dst):dst.objects=[n for n in src.objects if n=='Hair / swept roots220']
 for ob in dst.objects:bpy.context.scene.collection.objects.link(ob);ob['catalogue226']=True;ob['source226']='224 accepted selected pulled-back roots'
def plaits(style):
 a.setup();a.GROUP='hair';locs=style=='locs'
 for side in [-1,1]:
  for j in range(13):
   y=-.335+j*.057;section=sqrt(max(.01,1-((y-.015)/.433)**2));pts=[]
   for theta in np.linspace(.04,1.78,20):pts.append(Vector((side*.505*section*sin(theta),y,1.88+.483*section*cos(theta))))
   front=j<2;pts+= [Vector((side*.43*section,-.17 if front else y*.87,1.47)),Vector((side*.32,-.23 if front else .18+.09*j/12,(1.42 if locs else 1.18)+.025*sin(j*2)))]
   a.braid('Hair / rooted '+style+str(side)+' '+str(j),pts,.033 if locs else .034,locs)
 for j in range(9):
  x=-.33+j*.0825;extent=sqrt(max(.1,1-(x/.51)**2));pts=[a.surface(x,.23,.018),Vector((x,.015+.43*extent,2.06)),Vector((x*.98,.015+.44*extent,1.75)),Vector((x*.90,.32,1.43)),Vector((x*.86,.28,(1.41 if locs else 1.20)+.025*sin(j)))]
  a.braid('Hair / rear '+style+' '+str(j),pts,.034,locs)
def build(style,covered=False):
 if style in ['straight','curls','flow','side-sweep']:long(style,covered)
 elif style in ['curly-top','afro']:curly(style=='afro',covered)
 elif style=='buzz':buzz()
 elif style in ['box-braids','locs']:plaits(style)
 else:
  a.hair(style,covered)
  # Retire rejected generic cap and disconnected root strokes; use the actual
  # developed rooted surface as a construction reference for gathered styles.
  for ob in list(bpy.context.scene.objects):
   if ob.get('catalogue226') and (ob.name.startswith('Hair / rooted coverage') or ob.name.startswith('Hair / swept root ')):bpy.data.objects.remove(ob,do_unlink=True)
  gathered_roots()
