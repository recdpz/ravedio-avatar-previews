"""Correct garment-like headwear and separate transparent eyewear components."""
import bpy,math
import numpy as np
from math import sin,cos,pi,sqrt
from mathutils import Vector
import sculpt226 as a

def eyewear(style):
 a.eyewear(style)
 for ob in list(bpy.context.scene.objects):
  if not ob.get('catalogue226'):continue
  if ob.type=='MESH' and (' frame ' in ob.name or ' lens ' in ob.name):
   side=-1 if ob.name.endswith('-1') else 1
   for v in ob.data.vertices:
    v.co.y=-.430+.194*side*(v.co.x-side*.16)
  if ob.get('component159')=='lenses':
   # Front/back normals must not average across the thin perimeter wall.
   # A smoothly shaded solidified pane falsely behaves like a thick prism.
   for poly in ob.data.polygons:poly.use_smooth=False
   for mod in ob.modifiers:
    if mod.type=='SOLIDIFY':mod.thickness=.0025
   for m in ob.data.materials:
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['IOR'].default_value=1.45;bs.inputs['Roughness'].default_value=.06
  if style=='wraparound' and ob.type=='MESH' and ob.get('component159') in ['glasses','lenses']:
   for v in ob.data.vertices:
    p=v.co
    if p.y<-.30:
     side=-1 if p.x<0 else 1
     p.x*=1.10;p.z=1.90+(p.z-1.90)*.72;p.y=-.443+.32*side*(p.x-side*.176)
  if style=='kaleidoscope' and ob.get('component159')=='lenses':
   # Small triangular facets on the actual lens, not an opaque lens decal.
   sub=ob.modifiers.new('Lens facets','TRIANGULATE')

def gems():
 a.setup();a.GROUP='extra'
 for side in [-1,1]:
  for j in range(4):
   x=side*(.13+j*.053);z=1.765+j*.017;y=.015-.405*sqrt(max(.01,1-(x/.48)**2-((z-1.88)/.455)**2))-.006
   bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=(x,y,z));o=bpy.context.object;o.name='Face gems / cheek crystal '+str(side)+' '+str(j);o.scale=(.012,.006,.012);o['component159']='extra';o['catalogue226']=True;o.data.materials.append(a.M['pink'] if j%2 else a.M['gold'])

def hat(style):
 a.setup();a.GROUP='headgear'
 if style=='pashmina':pashmina();return
 if style=='headband':headband();return
 if style not in ['bucket','cowboy']:
  a.hat(style);return
 cow=style=='cowboy';mat=a.M['fabric'];hem=a.M['hem']
 def crown(ang,t):
  ph=ang*2*pi;rx=.516-(.065 if cow else .072)*t;ry=.446-(.060 if cow else .065)*t
  # Pinched crown and a continuous shallow center dent distinguish the cowboy.
  pinch=.026*t*t*math.exp(-((abs(sin(ph))-.68)/.26)**2) if cow else .007*sin(3*ph+.4)*sin(pi*t)
  x=(rx-pinch)*sin(ph);y=.015-(ry-pinch*.7)*cos(ph);z=2.075+(.35 if cow else .32)*t+.014*sin(ph+.4)*sin(pi*t)
  if cow:z-=.065*cos(ph)**2*t**3
  return Vector((x,y,z))
 a.grid(style+' / soft crown',crown,112,32,mat,.014)
 def top(ang,r):
  ph=ang*2*pi;edge=crown(ang,1);x=edge.x*r;y=.015+(edge.y-.015)*r
  z=2.425-.065*(1-(x/.45)**2) if cow else edge.z+.016*(1-r*r)
  return Vector((x,y,z))
 a.grid(style+' / shaped crown top',top,112,30,mat,.014)
 def brim(ang,t):
  ph=ang*2*pi;rx=.516+(.20 if cow else .105)*t;ry=.446+(.17 if cow else .11)*t
  z=2.075+(.115*sin(ph)**2-.042*cos(ph)**2)*t*t if cow else 2.075-.090*t+.010*sin(3*ph+.4)*t*t
  return Vector((rx*sin(ph),.015-ry*cos(ph),z))
 a.grid(style+' / flexible brim',brim,144,24,mat,.013)
 for t in [.70,.93]:a.tube(style+' / stitched brim '+str(t),[brim(ang,t)+Vector((0,0,.003)) for ang in np.linspace(0,1,145)],.0017,.0017,hem,n=145,sides=6,taper=False)
 # Quiet sewn panels, not a thick hard rim around a bucket.
 for ang in [0,.25,.5,.75]:a.tube(style+' / sewn panel '+str(ang),[crown(ang,t)+Vector((.002*sin(ang*2*pi),-.002*cos(ang*2*pi),0)) for t in np.linspace(.04,.98,45)],.0017,.0014,hem,n=45,sides=6,taper=False)
 if cow:a.tube('Cowboy / crown band',[crown(ang,.08)+Vector((.004*sin(ang*2*pi),-.004*cos(ang*2*pi),0)) for ang in np.linspace(0,1,145)],.010,.008,hem,n=145,sides=8,taper=False)

def pashmina():
 a.setup();a.GROUP='headgear';fabric=a.material('Pashmina / woven teal227',(.035,.105,.13),.62);thread=a.material('Pashmina / woven sand227',(.39,.35,.25),.65)
 guides=a.sample([(-.285,.55,1.75,.68),(.07,.56,1.75,.68),(.49,.53,1.63,.52),(.45,.36,1.08,.12)],100)
 def hood(ang,t):
  k=min(98,int(t*99));g=guides[k].lerp(guides[k+1],t*99-k);q=(ang-.5)*pi
  fold=.013*sin(q*5+t*4)*sin(pi*t)*sin(q)**2
  return Vector(((g.y+fold)*sin(q),g.x+.008*cos(q*7)*sin(pi*t),g.z+g.w*cos(q)))
 # guides are four-dimensional vectors (Y, half width, lower height, arc height).
 a.grid('Pashmina / settled head drape',hood,112,99,fabric,.010)
 for t in [0,1]:a.tube('Pashmina / head hem '+str(t),[hood(q,t) for q in np.linspace(0,1,113)],.0035,.003,thread,n=113,sides=6,taper=False)
 for t in [.05,.10,.82,.88,.94]:a.tube('Pashmina / woven head border '+str(t),[hood(q,t)+Vector((0,-.001,.002)) for q in np.linspace(0,1,113)],.0018,.0016,thread,n=113,sides=5,taper=False)
 for side in [-1,1]:
  edge=1 if side==1 else 0;start=hood(edge,.10);path=a.sample([start,(side*.43,-.265,1.48),(side*.30,-.35,1.17),(side*.24,-.35,.93)],81)
  def end(w,t):
   k=min(79,int(t*80));p=path[k].lerp(path[k+1],t*80-k);blend=min(1,t/.45);blend=blend*blend*(3-2*blend);offset=(hood(edge,w*.20)-start)*(1-blend)+Vector((side*(w-.5)*.18,0,0))*blend;p+=offset;p.y+=.012*sin(w*3*pi+.3)*sin(pi*t*.85);p.z+=.008*sin(w*2*pi)*t;return p
  a.grid('Pashmina / soft hanging end '+str(side),end,32,80,fabric,.010)
  for w in [.02,.98]:a.tube('Pashmina / end selvage '+str(side)+str(w),[end(w,t) for t in np.linspace(0,1,81)],.003,.0028,thread,n=81,sides=6,taper=False)
  for t in [.72,.80,.88,.95]:a.tube('Pashmina / end woven border '+str(side)+str(t),[end(w,t)+Vector((0,-.006,0)) for w in np.linspace(0,1,33)],.002,.0018,thread,n=33,sides=5,taper=False)
  for j in range(12):
   p=end((j+.5)/12,1);a.tube('Pashmina / tassel '+str(side)+str(j),[p,p+Vector((.003*sin(j),0,-.05))],.0024,.0024,thread,n=8,sides=6,taper=False)
 # Neck fold rests on the upper torso, below the floating head.
 path=a.sample([(-.49,-.24,1.53),(-.32,-.33,1.38),(0,-.375,1.32),(.32,-.33,1.40),(.49,-.24,1.53)],81)
 def wrap(u,v):
  k=min(79,int(u*80));p=path[k].lerp(path[k+1],u*80-k);p.z+=(v-.5)*.085+.015*sin(u*pi);p.y+=.007*(2*v-1)**2;return p
 a.grid('Pashmina / resting neck fold',wrap,80,24,fabric,.010)

def headband():
 a.setup();a.GROUP='headgear'
 def band(ang,t):
  ph=ang*2*pi;theta=1.10+.13*t+.43*max(0,-cos(ph))**1.3;clear=.010+.012*max(0,cos(ph))**5
  return a.polar(theta,ph,clear)
 a.grid('Headband / under-hair wrap',band,160,12,a.M['fabric'],.008)
 for t in [0,1]:a.tube('Headband / fine hem '+str(t),[band(ang,t) for ang in np.linspace(0,1,161)],.0018,.0018,a.M['hem'],n=161,sides=6,taper=False)
 for side in [-1,1]:a.tube('Headband / nape knot tail '+str(side),[(side*.018,.435,1.86),(side*.075,.43,1.79),(side*.10,.41,1.73)],.022,.007,a.M['fabric'],n=30,sides=10)
