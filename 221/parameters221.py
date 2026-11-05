"""221: physical-length tail and authored current-head support for tie offset."""
import math,json,base64,numpy as np
from functools import lru_cache
from pathlib import Path
P=Path(__file__).parent;CFG=json.loads((P/'pony-parameters221.json').read_text());CAP=json.loads((P/'cap-parameters221.json').read_text());C=np.array([0.,.015,1.88])
KEYS=['length','fullness','arc','bend','side','height','depth','flow','lift','rootSide','covered']
SHAPE_KEYS=[k for k in KEYS if k!='length'];WX=[.24,.30,.34,.29,.24];DY=[.32,.38,.44,.39,.31];OX=[-.36,-.185,0,.18,.35];OY=[-.035,.045,-.025,.040,-.020];SHORT=[.10,.035,0,.05,.13]
def sm(t):t=np.clip(t,0,1);return t*t*(3-2*t)
def norm(p):return np.asarray(p)/max(1e-12,np.linalg.norm(p))
def cubic(p,t):return (1-t)**3*p[0]+3*(1-t)**2*t*p[1]+3*(1-t)*t*t*p[2]+t**3*p[3]
def fitted(p,covered=False):
 p={**p,'rootSide':p.get('rootSide',0),'covered':bool(covered)}
 if covered:p['height']=min(p['height'],CFG['cap_fit']['height_max']);p['rootSide']=float(np.clip(p['rootSide'],*CFG['cap_fit']['rootSide_bounds']))
 return p
def gather_weights(height):
 knots=CFG['height_knots'];i=min(len(knots)-2,max(0,int(np.searchsorted(knots,height,side='right'))-1));u=float(np.clip((height-knots[i])/(knots[i+1]-knots[i]),0,1));w=[0.]*len(knots);w[i]=1-u;w[i+1]=u;return w
def base_attachment(p):
 w=np.asarray(gather_weights(p['height']));return w@np.asarray(CFG['anchors']),norm(w@np.asarray(CFG['attach_axes']))
@lru_cache(maxsize=1)
def support_table():
 q=CFG['scalp_support'];return np.frombuffer(base64.b64decode(q['radii_u16le']),dtype='<u2').reshape(q['rows'],q['cols'])*q['unit']+q['offset']
def support_radius(d):
 a=np.asarray(d);q=CFG['scalp_support'];table=support_table();th=(np.arctan2(a[...,1],a[...,0])%(2*math.pi))/(2*math.pi)*q['cols'];ph=np.arccos(np.clip(a[...,2],-1,1))/math.pi*(q['rows']-1);i=np.floor(th).astype(int)%q['cols'];j=np.minimum(q['rows']-2,np.floor(ph).astype(int));u=th-np.floor(th);v=ph-j
 return (table[j,i]*(1-u)+table[j,(i+1)%q['cols']]*u)*(1-v)+(table[j+1,i]*(1-u)+table[j+1,(i+1)%q['cols']]*u)*v
def turn_direction(d,angle):
 d=np.asarray(d);east=np.zeros_like(d);east[...,0]=1;east-=d*d[...,0,None];east/=np.maximum(1e-12,np.linalg.norm(east,axis=-1))[...,None]
 a=np.asarray(angle);return d*np.cos(a)[...,None]+east*np.sin(a)[...,None]
def attachment(p):
 g,axis=base_attachment(p);offset=p.get('rootSide',0)
 if abs(offset)<1e-12:return g,axis
 d=norm(g-C);new=turn_direction(d,offset/.49);return C+new*(support_radius(new)+.010),norm(new)
def rotation(p):
 g0,_=base_attachment(p);g1,_=attachment(p);a=norm(g0-C);b=norm(g1-C);v=np.cross(a,b);co=float(a@b);K=np.array([[0,-v[2],v[1]],[v[2],0,-v[0]],[-v[1],v[0],0]]);return g0,g1,np.eye(3)+K+K@K/max(1e-12,1+co)
def gather_points(points,t,p,role='roots'):
 points=np.asarray(points);off=p.get('rootSide',0)
 if abs(off)<1e-12:return points.copy()
 g0,g1,R=rotation(p);rigid=(points-g0)@R.T+g1
 if role=='tie':return rigid
 r=np.linalg.norm(points-C,axis=1);d=(points-C)/r[:,None];new=turn_direction(d,off/.49*sm(np.asarray(t)/.90));clear=r-support_radius(d);out=C+new*(support_radius(new)+clear+.00045*sm(np.asarray(t)/.10)*(1-sm((np.asarray(t)-.86)/.14))*abs(off)/.18)[:,None];mix=sm((np.asarray(t)-.86)/.14)[:,None];return out*(1-mix)+rigid*mix
def controls(p):
 g,axis=attachment(p);A=p['arc'];H=p['lift'];tangent=axis if p.get('covered',False) else norm([axis[0],axis[1]*.8,max(axis[2],.85)]);departure=.29 if p.get('covered',False) else .20
 # This master path is independent of selected length. Its lower fall stays
 # behind the head instead of hooking back toward the neck/torso.
 return g,np.array([g-axis*.010,g+tangent*.065,g+[0,departure+.55*A,.12+.8*H],g+[0,.24+.50*A,-.16],g+[0,.25+.40*A,-.78],g+[0,.23+.35*A,-1.13]])
def bezier5(points,t):return sum(math.comb(5,i)*(1-t)**(5-i)*t**i*points[i] for i in range(6))
@lru_cache(maxsize=96)
def master(values):
 p=dict(zip(SHAPE_KEYS,values));_,a=controls(p);t=np.linspace(0,1,257);points=np.array([bezier5(a,x) for x in t]);distance=np.r_[0,np.cumsum(np.linalg.norm(np.diff(points,axis=0),axis=1))];return distance,points
def raw_center(p,s,amount=0):
 distance,points=master(tuple(p.get(k,False) for k in SHAPE_KEYS));point=np.array([np.interp(s,distance,points[:,k]) for k in range(3)]);g,_=attachment(p);u=float(np.clip((g[2]-point[2])/.80,0,1));point[0]+=p['side']*sm(u)+p['bend']*32*u*u*(1-u)**2*(1-2*u);point[1]+=amount*sm(s/.22);return point
def frame(p,s,amount=0):
 axis=norm(raw_center(p,s+.0001,amount)-raw_center(p,max(0,s-.0001),amount));side=norm(np.array([1.,0.,0.])-axis*axis[0]);return side,np.cross(axis,side)
def envelope(s,length=None):
 e=.28+.72*sm(s/.20)
 if length is not None:e*=(1-.72*sm((s-(length-.18))/.16))*math.sqrt(max(0,1-float(sm((s-(length-.03))/.03))**2))
 return e
def lock_length(p,j):return p['length']-SHORT[j]*p['flow']*.55
def lock_frame(p,j,s,amount,length=None):
 flow=p['flow'];point=raw_center(p,s,amount);side,normal=frame(p,s,amount);e=envelope(s,length);u=s/.90;free=sm((s-.22)/.38)
 point+=side*(p['fullness']*(OX[j]*e*(.80-.35*min(u,1))+flow*.24*math.sin(1.30*math.pi*u+j*.85)*free))+normal*(p['fullness']*p['depth']*(OY[j]*e+flow*.18*math.sin(1.45*math.pi*u+j*.95)*free))
 roll=flow*(.22*math.sin(math.pi*u+j*.9)+.10*math.sin(2*math.pi*u+j*1.3))*free;co=math.cos(roll);sn=math.sin(roll);return point,side*co+normal*sn,normal*co-side*sn,e
def section(p,j,s,phase,amount,length=None):
 point,side,normal,e=lock_frame(p,j,s,amount,length);sx=math.sin(phase);out=math.cos(phase);u=s/.90;flow=p['flow'];lobes=1-.055*flow*math.cos(3*phase+j*.7);ws=1+.09*flow*math.sin(1.7*math.pi*u+j*1.1);ds=1+.13*flow*math.sin(1.3*math.pi*u+j*.7);groove=.0011*sum(math.exp(-((sx-g-.035*math.sin(u*math.pi+j))/.13)**2) for g in [-.50,.20,.62])*out**2
 return point+side*(WX[j]*p['fullness']*.5*sx*e*ws*lobes)+normal*((DY[j]*p['fullness']*.5*out*ds*lobes-math.copysign(groove,out))*e*p['depth'])
@lru_cache(maxsize=96)
def guide(values):
 p=dict(zip(SHAPE_KEYS,values));amount=0
 # Use the full untapered master envelope, so clearance never shifts the upper
 # locks when only Length changes. This is authored fitting, not live physics.
 for _ in range(4):
  needed=0
  for s in np.linspace(.10,1.10,42):
   phase=np.arange(16)*2*math.pi/16
   for j in range(5):
    center,side,normal,e=lock_frame(p,j,float(s),amount);u=s/.90;lobes=1-.055*p['flow']*np.cos(3*phase+j*.7);ws=1+.09*p['flow']*math.sin(1.7*math.pi*u+j*1.1);ds=1+.13*p['flow']*math.sin(1.3*math.pi*u+j*.7)
    ring=center+(np.sin(phase)*lobes)[:,None]*side*(WX[j]*p['fullness']*.5*e*ws)+(np.cos(phase)*lobes)[:,None]*normal*(DY[j]*p['fullness']*.5*e*ds*p['depth']);inside=1-(ring[:,0]/.490)**2-((ring[:,2]-1.88)/.465)**2;required=.015+.420*np.sqrt(np.maximum(0,inside))+.004;needed=max(needed,float(np.max(np.where(inside>0,np.maximum(0,required-ring[:,1])/sm(s/.22),0))))
  amount+=needed
  if needed<1e-7:break
 return amount
def tail_vertex(p,j,t,phase):
 length=lock_length(p,j);s=length*t;amount=guide(tuple(p.get(k,False) for k in SHAPE_KEYS))
 if t<.000001 or t>.999999:return lock_frame(p,j,s,amount,length)[0]
 return section(p,j,s,phase,amount,length)
def front_base(p,sign,t):
 roots=CFG['front_anchors'][str(sign)];a=np.asarray(roots[0])*(1-p['root'])+np.asarray(roots[1])*p['root']
 if t<=.40:return cubic(a,t/.40)
 u=(t-.40)/.60;start=a[3];end=start+np.array([sign*(.012+p['spread']),-.018,-p['length']]);c1=start+1.5*(a[3]-a[2]);c2=end+np.array([sign*.018,-.010,p['length']*.30]);out=cubic(np.array([start,c1,c2,end]),u);out[0]+=sign*p['curl']*32*u*u*(1-u)**2*(1-2*u);return out
def front_fixed(p,sign,t,phase,amount):
 def centerline(t):out=front_base(p,sign,t);out[1]-=amount*sm((t-.40)/.25);return out
 center=centerline(t);axis=norm(centerline(min(1,t+.0001))-centerline(max(0,t-.0001)));side=norm(np.array([1.,0.,0.])-axis*axis[0]);normal=np.cross(axis,side);e=(.20+.80*sm(t/.50))*(1-.80*sm((t-.72)/.28))*math.sqrt(max(0,1-sm((t-.95)/.05)**2));sx=math.sin(phase);out=math.cos(phase);groove=.00045*sum(math.exp(-((sx-g)/.14)**2) for g in [-.45,.32])*max(out,0)**2
 if t<.000001 or t>.999999:return center
 return center+side*(p['volume']*.5*sx*e)+normal*((p['volume']*.23*out-groove)*e)
@lru_cache(maxsize=128)
def front_guide(values,sign):
 p=dict(zip(['length','volume','curl','spread','root'],values));amount=0
 for _ in range(4):
  needed=0
  for t in np.linspace(.54,.98,24):
   for phase in np.arange(12)*math.pi/6:
    vertex=front_fixed(p,sign,float(t),phase,amount);inside=1-(vertex[0]/.486)**2-((vertex[2]-1.88)/.462)**2
    if inside>0:needed=max(needed,max(0,vertex[1]-(.015-.412*math.sqrt(inside)-.003))/float(sm((t-.40)/.25)))
  amount+=needed
  if needed<1e-7:break
 return amount
def front_vertex(p,sign,t,phase):return front_fixed(p,sign,t,phase,front_guide(tuple(p[k] for k in ['length','volume','curl','spread','root']),sign))
def cap_vertex(point,p):
 x,y,z=point;profile=CAP['profile'];ry=float(np.interp(abs(x),[r[0] for r in profile],[r[1] for r in profile]));ext=float(np.interp(abs(x),[r[0] for r in profile],[r[2] for r in profile]));bill=float(np.clip((ry-y)/(.325*ext),0,1)) if y<0 else 0
 y-=(p['length']-.325)*bill*ext;z-=p['curve']*(x/.46)**2*float(sm(bill/.75))*math.sqrt(ext);z+=p['crown']*float(sm((z-1.88-.17)/.30))*(1-float(sm(bill/.15)));t=math.radians(p['tilt']);dy=y-.015;dz=z-1.88;y=.015+dy*math.cos(t)+dz*math.sin(t);z=1.88-dy*math.sin(t)+dz*math.cos(t);return np.array([x,y,z])

def apply(scene,choices):
 p=fitted(choices.get('pony',CFG['default']),bool(scene.get('pony_cap221')));front=choices.get('front',{});w=gather_weights(p['height'])
 for ob in scene.objects:
  if ob.get('param221')=='gather':
   keys=ob.data.shape_keys.key_blocks;points=sum(weight*np.array([v.co[:] for v in keys['RootOriginal221_'+str(i)].data]) for i,weight in enumerate(w) if weight)
   for i in range(9):keys['RootOriginal221_'+str(i)].value=0
   role=ob['gatherRole'];t=np.repeat(np.linspace(0,1,85),256) if role=='roots' else None;points=gather_points(points,t,p,role);ob.data.vertices.foreach_set('co',np.asarray(points,dtype='f').ravel());keys['Basis'].data.foreach_set('co',np.asarray(points,dtype='f').ravel());ob.data.update()
  if ob.get('param214')=='cap' and choices.get('cap'):
   cp={**CAP['default'],**choices['cap']};cp['turn']=0
   for k,(lo,hi) in CAP['bounds'].items():cp[k]=float(np.clip(cp[k],lo,hi))
   points=np.array([cap_vertex(v.co[:],cp) for v in ob.data.shape_keys.key_blocks['CapOriginal'].data],dtype='f');ob.data.vertices.foreach_set('co',points.ravel());ob.data.shape_keys.key_blocks['Basis'].data.foreach_set('co',points.ravel());ob.data.update()
   if ob.get('capDesign'):ob.hide_render=ob['capDesign']!=cp.get('design','wordmark')
   colors={'black':'25272D','cream':'D4CEBA','purple':'6A4E80','red':'964C5B'};color=cp.get('color','navy');rgb=[.026,.053,.080] if color=='navy' else [int(colors.get(color,colors['black'])[i:i+2],16)/255 for i in [0,2,4]]
   if color!='navy':rgb=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb]
   for ma in ob.data.materials:
    if ma and 'midnight cotton' in ma.name:ma.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*rgb,1)
  role=ob.get('param216')
  if role not in ['tail','front'] or (role=='front' and 'front' not in choices):continue
  uv=ob.data.uv_layers.active;values={}
  for poly in ob.data.polygons:
   for li in poly.loop_indices:
    i=ob.data.loops[li].vertex_index
    if i not in values:
     t,phase=uv.data[li].uv;values[i]=tail_vertex(p,int(ob['tail_index']),t,phase*2*math.pi) if role=='tail' else front_vertex(front.get(str(ob['front_side']),CFG['front_default']),int(ob['front_side']),t,phase*2*math.pi)
  for i,point in values.items():ob.data.vertices[i].co=point
  ob.data.update()
 scene.view_layers.update()
