"""Portable214 parameter evaluation; no historical generator dependencies."""
import math,json,numpy as np
from functools import lru_cache
from pathlib import Path
P=Path(__file__).parent
CFG=json.loads((P/'pony-parameters215.json').read_text(encoding='utf8'))
CAP=json.loads((P/'cap-parameters215.json').read_text(encoding='utf8'))
def sm(x):x=np.clip(x,0,1);return x*x*(3-2*x)
def norm(x):return x/max(1e-10,np.linalg.norm(x))
def lerp(x,y,t):return np.asarray(x)*(1-t)+np.asarray(y)*t
def points(p,j):
 anchors=np.asarray(CFG['anchors'])
 g=lerp(anchors[0],anchors[1],p['height']);axis=lerp([0,.78,.63],[0,.68,.74],p['height']);axis/=np.linalg.norm(axis)
 cross=np.array([0,-axis[2],axis[1]]);phase=2*math.pi*j/7;offset=np.array([math.cos(phase)*p['fullness']*.19,0,0])+cross*math.sin(phase)*p['fullness']*.15
 L=p['length'];A=p['arc'];B=p['bend'];S=p['side']
 # The gathering axis leaves the scalp, rounds over, then drops. The one
 # broad S gesture is in X/Z (rear view); depth has no alternating elbows.
 points=np.array([g-axis*.010,g+axis*.047,g+[S*.10+B*.48,A*.82,.025],g+[S*.38+B*1.45,A,-L*.24],g+[S*.70-B*.90,A*.96,-L*.53],g+[S*.90-B*1.05,A*.85,-L*.79],g+[S+B*.45,A*.76,-L]])
 points+=offset[None,:]*np.array([.15,.28,.65,1.,.92,.75,.37])[:,None];points[-1,2]+=.012*math.sin(j*1.5)
 return points

def hermite(pts,t,p=None):
 t=max(0,min(1,t));segment=min(t*6,6-1e-8);j=int(segment);u=segment-j;tang=np.empty_like(pts);tang[1:-1]=(pts[2:]-pts[:-2])*.5;tang[0]=pts[1]-pts[0];tang[-1]=pts[-1]-pts[-2]
 point=(2*u**3-3*u*u+1)*pts[j]+(u**3-2*u*u+u)*tang[j]+(-2*u**3+3*u*u)*pts[j+1]+(u**3-u*u)*tang[j+1]
 if p is not None:point[1]+=guide_amount(tuple(p[k] for k in ['length','fullness','arc','bend','side','height']))*sm(t/.32)
 return point
@lru_cache(maxsize=32)
def guide_amount(values):
 p=dict(zip(['length','fullness','arc','bend','side','height'],values));F=p['fullness'];path=np.asarray([[hermite(points(p,j),float(t)) for t in np.linspace(0,1,73)] for j in range(7)]);t=np.linspace(0,1,73);weight=sm(t/.32);env=(.25+.75*sm(t/.28))*(1-.85*sm((t-.70)/.30))*np.sqrt(np.maximum(0,1-sm((t-.94)/.06)**2));amount=0
 for iteration in range(4):
  shifted=path.copy();shifted[:,:,1]+=amount*weight[None,:];axis=np.gradient(shifted,axis=1);axis/=np.maximum(np.linalg.norm(axis,axis=2)[:,:,None],1e-9);side=np.broadcast_to([1.,0.,0.],axis.shape).copy();side-=axis*axis[:,:,0,None];side/=np.maximum(np.linalg.norm(side,axis=2)[:,:,None],1e-9);normal=np.cross(axis,side);phase=np.arange(24)*2*math.pi/24;ring=shifted[:,:,None,:]+side[:,:,None,:]*(F*.65*.5*env[None,:,None,None]*np.sin(phase)[None,None,:,None])+normal[:,:,None,:]*(F*.48*.5*env[None,:,None,None]*np.cos(phase)[None,None,:,None]);inside=1-(ring[:,:,:,0]/.490)**2-((ring[:,:,:,2]-1.88)/.465)**2;required=.015+.420*np.sqrt(np.maximum(0,inside))+.004;valid=(inside>0)&(t[None,:,None]>=.14);need=np.max(np.where(valid,np.maximum(0,required-ring[:,:,:,1])/np.maximum(weight[None,:,None],1e-8),0));amount+=float(need)
  if need<1e-6:break
 return amount
def tail_vertex(p,j,t,phase):
 pts=points(p,j);center=hermite(pts,t,p)
 if t<.00001 or t>.99999:return center
 tangent=norm(hermite(pts,min(1,t+1/72),p)-hermite(pts,max(0,t-1/72),p));side=norm(np.array([1,0,0])-tangent*tangent[0]);normal=np.cross(tangent,side);sx=math.sin(phase);out=math.cos(phase);groove=.00085*sum(math.exp(-((sx-g)/.12)**2) for g in [-.52,.05,.59])*max(out,0)**2;env=(.25+.75*sm(t/.28))*(1-.85*sm((t-.70)/.30));env*=math.sqrt(max(0,1-sm((t-.94)/.06)**2))
 return center+side*p['fullness']*.65*.5*sx*env+normal*(p['fullness']*.48*.5*out-groove)*env
def cap_vertex(point,p):
 x,y,z=point;C=[0,.015,1.88];rows=np.asarray(CAP['profile']);root_y=float(np.interp(abs(x),rows[:,0],rows[:,1]));extension=float(np.interp(abs(x),rows[:,0],rows[:,2]));bill=max(0,min(1,(root_y-y)/(.325*extension))) if y<0 else 0;y-=(p['length']-.325)*bill*extension;z-=p['curve']*(x/.46)**2*sm(bill/.75)*math.sqrt(extension);z+=p['crown']*sm((z-C[2]-.17)/.30)*(1-sm(bill/.15));t=math.radians(p['tilt']);dy=y-C[1];dz=z-C[2];y=C[1]+dy*math.cos(t)+dz*math.sin(t);z=C[2]-dy*math.sin(t)+dz*math.cos(t);yaw=math.radians(p.get('turn',0));return np.array([x*math.cos(yaw)-(y-C[1])*math.sin(yaw),C[1]+x*math.sin(yaw)+(y-C[1])*math.cos(yaw),z])
def apply(scene,choices):
 p=choices.get('pony',CFG['default']);cp=choices.get('cap',CAP['default'])
 for ob in scene.objects:
  role=ob.get('param214')
  if role=='roots':ob.data.shape_keys.key_blocks['TieHeight'].value=p['height']
  elif role=='tail':
   uv={vi:ob.data.uv_layers.active.data[li].uv[:] for poly in ob.data.polygons for vi,li in zip(poly.vertices,poly.loop_indices)}
   for i,vertex in enumerate(ob.data.vertices):vertex.co=tail_vertex(p,ob['tail_index'],uv[i][0],uv[i][1]*2*math.pi)
  elif role=='cap':
   keys=ob.data.shape_keys.key_blocks;original=keys['CapOriginal'];basis=keys['Basis'];result=np.array([cap_vertex(v.co,cp) for v in original.data],dtype='f');basis.data.foreach_set('co',result.ravel());ob.data.vertices.foreach_set('co',result.ravel());original.value=0
   if ob.get('capDesign'):ob.hide_render=ob.get('capDesign')!=cp.get('design','wordmark')
   palette={'navy':[.026,.053,.080]}
   for name,h in {'black':'25272D','cream':'D4CEBA','purple':'6A4E80','red':'964C5B'}.items():
    srgb=[int(h[i:i+2],16)/255 for i in [0,2,4]];palette[name]=[x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in srgb]
   for material in ob.data.materials:
    if 'midnight cotton' in material.name:material.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=palette.get(cp.get('color','navy'),palette['navy'])+[1]
  if role:ob.data.update()
