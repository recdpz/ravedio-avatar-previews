"""Shared217 authoring/review evaluator. No Blender or historical helpers."""
import math,json,numpy as np
from functools import lru_cache
from pathlib import Path
P=Path(__file__).parent;CFG=json.loads((P/'pony-parameters217.json').read_text())
KEYS=['length','fullness','arc','bend','side','height','depth'];WX=[.37,.41,.50,.39,.34];DY=[.34,.42,.50,.42,.34];OX=[-.33,-.17,0,.17,.33];OY=[-.02,-.05,-.06,-.05,-.02]
def sm(t):t=np.clip(t,0,1);return t*t*(3-2*t)
def norm(p):return np.asarray(p)/max(1e-12,np.linalg.norm(p))
def cubic(p,t):return (1-t)**3*p[0]+3*(1-t)**2*t*p[1]+3*(1-t)*t*t*p[2]+t**3*p[3]
def attachment(p):
 knots=CFG['height_knots'];i=min(len(knots)-2,max(0,int(np.searchsorted(knots,p['height'],side='right'))-1));u=float(np.clip((p['height']-knots[i])/(knots[i+1]-knots[i]),0,1))
 return np.asarray(CFG['anchors'][i])*(1-u)+np.asarray(CFG['anchors'][i+1])*u,norm(np.asarray(CFG['attach_axes'][i])*(1-u)+np.asarray(CFG['attach_axes'][i+1])*u)
def gather_weights(height):
 knots=CFG['height_knots'];i=min(len(knots)-2,max(0,int(np.searchsorted(knots,height,side='right'))-1));u=float(np.clip((height-knots[i])/(knots[i+1]-knots[i]),0,1));w=[0.]*(len(knots)-1)
 if i>0:w[i-1]=1-u
 w[i]=u
 return w
def controls(p):
 g,axis=attachment(p);L=p['length'];A=p['arc'];end=g[1]-.04+.20*A;inside=1-((g[2]-L-1.88)/.465)**2
 if inside>0:end=max(end,.015+.420*math.sqrt(inside)+.009)
 d=end-g[1]
 return g,np.array([g-axis*.010,g+axis*.055,g+[0,.20+.70*A,.105],g+[0,max(.38+A,d+.16),-L*.26],g+[0,max(.18+.60*A,d+.07),-L*.76],g+[0,d,-L]])
def bezier5(points,t):return sum(math.comb(5,i)*(1-t)**(5-i)*t**i*points[i] for i in range(6))
def fall(p,t):
 g,points=controls(p);return float(np.clip((g[2]-bezier5(points,t)[2])/p['length'],0,1))
def env(p,t):
 u=fall(p,t);return (.28+.72*sm(t/.32))*(1-.72*sm((u-.66)/.34))*math.sqrt(max(0,1-sm((u-.94)/.06)**2))
def raw_center(p,t,amount=0):
 g,points=controls(p);point=bezier5(points,t)
 u=fall(p,t);point[0]+=p['side']*sm(u)+p['bend']*32*u*u*(1-u)**2*(1-2*u);point[1]+=amount*sm(t/.38)
 return point
def frame(p,t,amount=0):
 axis=norm(raw_center(p,min(1,t+.0001),amount)-raw_center(p,max(0,t-.0001),amount));side=norm(np.array([1.,0.,0.])-axis*axis[0]);return side,np.cross(axis,side)
def tail_fixed(p,j,t,phase,amount):
 point=raw_center(p,t,amount);side,normal=frame(p,t,amount);e=env(p,t);point+=side*(OX[j]*p['fullness']*e*(.80-.35*t))+normal*(OY[j]*p['fullness']*e*p['depth']);point[2]+=p['length']*.025*abs(j-2)/2*sm(t)
 if t<.000001 or t>.999999:return point
 sx=math.sin(phase);out=math.cos(phase);groove=.0007*sum(math.exp(-((sx-g)/.14)**2) for g in [-.46,.12,.61])*out**2
 return point+side*(WX[j]*p['fullness']*.5*sx*e)+normal*((DY[j]*p['fullness']*.5*out-math.copysign(groove,out))*e*p['depth'])
@lru_cache(maxsize=64)
def guide(values):
 p=dict(zip(KEYS,values));amount=0
 # Check the real five-lock ring envelope; move the coherent departure only.
 for _ in range(4):
  needed=0
  for t in np.linspace(.15,.95,54):
   side,normal=frame(p,float(t),amount);base=raw_center(p,float(t),amount);e=env(p,t);phase=np.arange(24)*2*math.pi/24
   for j in range(5):
    center=base+side*(OX[j]*p['fullness']*e*(.80-.35*t))+normal*(OY[j]*p['fullness']*e*p['depth'])+[0,0,p['length']*.025*abs(j-2)/2*sm(t)]
    ring=center+np.sin(phase)[:,None]*side*(WX[j]*p['fullness']*.5*e)+np.cos(phase)[:,None]*normal*(DY[j]*p['fullness']*.5*e*p['depth'])
    inside=1-(ring[:,0]/.490)**2-((ring[:,2]-1.88)/.465)**2;required=.015+.420*np.sqrt(np.maximum(0,inside))+.003;needed=max(needed,float(np.max(np.where(inside>0,np.maximum(0,required-ring[:,1])/sm(t/.38),0))))
  amount+=needed
  if needed<1e-7:break
 return amount
def tail_vertex(p,j,t,phase):return tail_fixed(p,j,t,phase,guide(tuple(p[k] for k in KEYS)))
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
def apply(scene,choices):
 p=choices.get('pony',CFG['default']);front=choices.get('front',{});weights=gather_weights(p['height'])
 for ob in scene.objects:
  if ob.get('param217')=='gather':
   for k,w in enumerate(weights):ob.data.shape_keys.key_blocks['Gather217_'+str(k+1)].value=w
  role=ob.get('param216')
  if role not in ['tail','front']:continue
  if role=='front' and 'front' not in choices:continue
  uv=ob.data.uv_layers.active;values={}
  for poly in ob.data.polygons:
   for li in poly.loop_indices:
    i=ob.data.loops[li].vertex_index
    if i in values:continue
    t,phase=uv.data[li].uv;phase*=2*math.pi
    values[i]=tail_vertex(p,int(ob['tail_index']),t,phase) if role=='tail' else front_vertex(front.get(str(ob['front_side']),CFG['front_default']),int(ob['front_side']),t,phase)
  for i,point in values.items():ob.data.vertices[i].co=point
  ob.data.update()
 scene.view_layers.update()
