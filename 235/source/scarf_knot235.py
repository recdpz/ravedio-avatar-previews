"""Gathered one-piece hood, broad side folds, loose chest knot and two ends.

Owner direction supersedes the free rear cape and separate neck ring drafts.
"""
import sys
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue235')
from common235 import *
from scarf_support235 import cloth_boundary,convex_support
import headwear235 as hats
from math import sin,cos,pi,sqrt

def patch(name,fn,nu,nv,mat):
 ob=hats.grid(name,fn,nu,nv,mat,0);sub=ob.modifiers.new('Soft woven folds235','SUBSURF');sub.levels=1;sub.render_levels=1
 solid=ob.modifiers.new('Woven scarf thickness235','SOLIDIFY');solid.thickness=.003;solid.offset=-1;return ob

def run(build):
 bpy.ops.wm.open_mainfile(filepath=str(P/'sources'/f'{build}-pashmina-polish235.blend'));s=bpy.context.scene;a.setup()
 for o in list(s.objects):
  if o.get('component159')=='headgear' and 'soft crown and rear' not in o.name:u.delete(o)
 frozen={k:v for k,v in u.object_geometry(s).items() if s.objects[k].get('component159')!='headgear'}
 hood=next(o for o in s.objects if 'soft crown and rear' in o.name);mat=hood.data.materials[0].copy();mat.name='Headwear / continuous woven pashmina235';hood.data.materials[0]=mat;n=len(hood.data.vertices)//2;uv={}
 # One weave orientation follows the whole scarf. Borders run along its long
 # edges, and the hood-to-fold UVs meet exactly instead of appearing sewn on.
 yy,xx=np.mgrid[0:256,0:512];distance=np.minimum(yy,255-yy);border=((distance>=9)&(distance<=12))|((distance>=20)&(distance<=22));motif=(abs((xx%64)-32)/32+abs((yy%48)-24)/24)<.18
 pix=np.ones((256,512,4),dtype='f');pix[:,:,:3]=np.where((border|motif)[:,:,None],np.array([.52,.46,.33]),np.array([.065,.14,.16]));pix[:,:,:3]*=(.985+.015*((xx+yy)%2))[:,:,None]
 im=bpy.data.images.new('Continuous pashmina weave235',width=512,height=256,alpha=True);im.pixels.foreach_set(pix.ravel());im.pack();bs=mat.node_tree.nodes.get('Principled BSDF');tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;mat.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
 for poly in hood.data.polygons:
  if max(poly.vertices)>=n:continue
  for li,vi in zip(poly.loop_indices,poly.vertices):uv[vi]=hood.data.uv_layers.active.data[li].uv.copy()
 torso=[o for o in s.objects if o.type=='MESH' and (o.name=='Skin / rounded torso' or o.name.startswith('Clothing /'))];body=convex_support(torso);major=convex_support(torso+[o for o in s.objects if o.name=='Skin / soft oval head'])
 # The rear portion is drawn into the nape. There is no free rear curtain
 # or decorative rear hem. Front side panels also gather into their folds.
 moved=0
 for i,q in uv.items():
  old=hood.matrix_world@hood.data.vertices[i].co;p=old.copy();theta=(q.x-.5)*3.96
  gather=smooth((q.y-.45)/.55)*(1-smooth((p.z-1.48)/.30))
  target=Vector((.285*sin(theta),.015+.225*cos(theta),1.385+.018*cos(theta)))
  target.x+=.006*sin(theta*5)*sin(pi*q.x)
  p=p.lerp(target,gather)
  corner=smooth((abs(q.x-.5)-.25)/.25)*(1-smooth((q.y-.12)/.40))*(1-smooth((p.z-1.38)/.30))
  radial=Vector((p.x,p.y,0)).normalized();hit=major.ray_cast(Vector((0,0,p.z)),radial,1.)[0]
  if hit is not None:p=p.lerp(hit+radial*.012,corner)
  delta=hood.matrix_world.inverted().to_3x3()@(p-old);hood.data.vertices[i].co+=delta;hood.data.vertices[i+n].co+=delta;moved=max(moved,delta.length)
 hem=a.material('Headwear / gathered scarf edge235',(.045,.085,.10),.96)
 front=[p for _,p in cloth_boundary(hood,1,0)];a.tube('Pashmina / subtle face hem235',front,.0015,.0014,hem,n=len(front),sides=6,taper=False,group='headgear')
 # The actual rear cloth boundary folds inward at the nape; its termination
 # is buried beneath this return, rather than hanging below the shoulders.
 rear=cloth_boundary(hood,1,1)
 def rear_point(w):
  for (lo,p),(hi,q) in zip(rear,rear[1:]):
   if lo<=w<=hi:return p.lerp(q,(w-lo)/(hi-lo))
  return rear[-1][1].copy()
 def tuck(w,t):
  p=rear_point(w);p.y-=.035*t;p.x*=1-.15*t;p.z+=.035*t-.008*sin(pi*t);return p
 ob=patch('Pashmina / buried nape return235',tuck,48,8,mat)
 for v in ob.data.uv_layers.active.data:v.uv=(v.uv.x,1+v.uv.y*.10)
 def support(x,z):
  hit=body.ray_cast(Vector((x,-1,z)),Vector((0,1,0)),2.)[0]
  return hit.y if hit is not None and hit.y<0 else None
 # Low-frequency support follows the bust, then bridges small hollows and
 # the crop gap instead of copying the individual garment surface.
 zs=np.linspace(.90,1.38,121);profiles={}
 for side in [-1,1]:
  ys=[]
  for z in zs:
   values=[support(side*x,float(z)) for x in [.13,.17,.21]];values=[y for y in values if y is not None];ys.append(min(values) if values else np.nan)
  ys=np.array(ys);good=np.isfinite(ys);assert good.sum()>50;ys=np.interp(zs,zs[good],ys[good]);raw=ys.copy()
  for _ in range(100):ys[1:-1]=(ys[:-2]+2*ys[1:-1]+ys[2:])/4
  ys-=max(0,float(np.max(ys-raw)));profiles[side]=ys
 def drape_y(x,z):
  blend=smooth((x+.06)/.12);return float(np.interp(z,zs,profiles[-1]))*(1-blend)+float(np.interp(z,zs,profiles[1]))*blend-.018
 knot_z=1.225;knot_back=drape_y(0,knot_z);knot_y=knot_back-.032
 # Broad hood sides converge into the chest knot. Their root is the actual
 # hood boundary, and their two edges are authored directly.
 for side in [-1,1]:
  edge=cloth_boundary(hood,0,0 if side<0 else 1)
  def root(w):
   value=(w if side>0 else 1-w)*.24
   for (lo,p),(hi,q) in zip(edge,edge[1:]):
    if lo<=value<=hi:return p.lerp(q,(value-lo)/(hi-lo))
   raise ValueError('Missing hood attachment boundary')
  center=root(.5);centers=[center,Vector((side*.31,-.18,1.365)),Vector((side*.21,-.25,1.31)),Vector((side*.10,knot_y+.01,1.265)),Vector((side*.025,knot_y-.012,1.23))];widths=[.22,.21,.19,.15,.115]
  rootB=(root(1)-root(0)).normalized();B=[rootB,Vector((-.65,.20*side,.73*side)),Vector((-.60,.15*side,.78*side)),Vector((-.4,.05*side,.92*side)),Vector((-.4,0,.92*side))]
  L=a.sample([c-b*w/2 for c,b,w in zip(centers,B,widths)],72);Rr=a.sample([c+b*w/2 for c,b,w in zip(centers,B,widths)],72);L[0]=root(0);Rr[0]=root(1)
  def side_fold(w,t):
   j=min(70,int(t*71));f=t*71-j;p=L[j].lerp(L[j+1],f).lerp(Rr[j].lerp(Rr[j+1],f),w)
   nominal=root(0).lerp(root(1),w);p+=(root(w)-nominal)*(1-smooth(t/.22))
   fit=smooth((t-.18)/.25);limit=drape_y(p.x,p.z);fitted=.5*(p.y+limit-sqrt((p.y-limit)**2+.008**2));p.y=p.y*(1-fit)+fitted*fit
   p.y-=.007*sin(2*pi*w+.25*side)*smooth(t/.2);return p
  ob=patch('Pashmina / hood side gathered into knot235 '+str(side),side_fold,24,64,mat)
  for v in ob.data.uv_layers.active.data:
   w,t=v.uv;v.uv=((0 if side<0 else 1)+side*.8*t,(w if side>0 else 1-w)*.24)
 # A loose overhand-like cloth fold, rather than a solid bead or rigid ring.
 knotmat=mat
 def loop(w,t):
  angle=(-.45+.85*t)*2*pi;r=.018*(2*w-1);return Vector(((.093+r)*cos(angle),knot_y-.008-.025*sin(angle*2)-.007*sin(pi*w),knot_z+(.048+r*.55)*sin(angle)))
 ob=patch('Pashmina / loose folded knot loop235',loop,12,80,knotmat)
 for v in ob.data.uv_layers.active.data:v.uv=(-.7-v.uv.y*.6,.35+v.uv.x*.10)
 def crossing(w,t):
  x=-.105+.21*t;z=knot_z+.026-.054*t+(w-.5)*(.065+.020*sin(pi*t));p=Vector((x,knot_y+.004-.058*sin(pi*t)**.8-.006*sin(pi*w),z));return p
 ob=patch('Pashmina / knot crossing and tucked fold235',crossing,14,48,knotmat)
 for v in ob.data.uv_layers.active.data:v.uv=(1.7+v.uv.y*.3,.35+v.uv.x*.15)
 # Two free ends emerge from opposite sides of the loose knot, follow the
 # large chest/bust form, then ease toward the torso without dipping into gaps.
 for side in [-1,1]:
  end=.96 if side<0 else .985;curve=a.sample([(side*.09,knot_y-.008,1.19),(side*.13,drape_y(side*.13,1.14)-.005,1.14),(side*.165,drape_y(side*.165,1.055),1.055),(side*.18,drape_y(side*.18,end),end)],72)
  def tail(w,t):
   j=min(70,int(t*71));f=t*71-j;p=curve[j].lerp(curve[j+1],f);width=.125+.025*smooth(t);p.x+=(w-.5)*width
   blend=smooth(t/.28);p.y=p.y*(1-blend)+drape_y(side*.17,p.z)*blend-.006*sin(2*pi*w+.2*side)*smooth(t/.15);p.z+=.004*sin(pi*w+.3*side)*t*t;return p
  ob=patch('Pashmina / soft end below knot235 '+str(side),tail,20,64,mat)
  for v in ob.data.uv_layers.active.data:
   w,t=v.uv;v.uv=((-1 if side<0 else 2)+side*t*.5,(w if side>0 else 1-w)*.24)
  thread=a.material('Headwear / fine scarf fringe235',(.12,.17,.17),.96)
  for k in range(10):
   p=tail((k+.5)/10,1);a.tube('Pashmina / free end fringe235 '+str(side)+' '+str(k),[p,p+Vector((.001*sin(k),0,-.017-.002*cos(k)))],.0012,.0010,thread,n=6,sides=5,taper=False,group='headgear')
 now=u.object_geometry(s);assert all(now.get(k)==v for k,v in frozen.items()),'Protected model changed'
 key=build+'-pashmina-knot235';u.camera(s,'front',512,True);parts=save(s,key,['headgear']);s=bpy.context.scene
 render(s,key,['front','threequarter','profile','rightprofile','rear','top','underside'],size=512,body=True)
 for angle in ['front','threequarter','profile','rear']:
  u.camera(s,angle,768,True);s.camera.data.ortho_scale=1.35;s.camera.location.z-=.02;s.cycles.samples=24;s.render.filepath=str(P/'review1'/f'{key}-detail-{angle}.png');bpy.ops.render.render(write_still=True)
 clay=a.material('Review / gray cloth knot235',(.24,.24,.24),.92)
 for o in s.objects:
  if o.type=='MESH' and o.get('component159')=='headgear':
   for i in range(len(o.data.materials)):o.data.materials[i]=clay
 render(s,key+'-clay',['front','threequarter','profile','rear'],size=512,body=True)
 return dict(source=str(P/'sources'/f'{key}.blend'),component=parts['headgear'],protected_neighbors_exact=True,max_lower_hood_change=moved,rear='Gathered into nape; no free rear curtain/hem; buried inward return',front='Broad hood sides converge into a loose chest-supported knot, with two soft ends. Major-form envelope bridges small garment gaps. No neck ring, no runtime physics.')
if __name__=='__main__':
 builds=next((x.split('=',1)[1].split(',') for x in sys.argv if x.startswith('--builds=')),['Feminine','Masculine']);records={}
 for build in builds:records[build]=run(build);u.dump(P/'pashmina-knot235.json',records)
