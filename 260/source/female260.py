import sys
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue260')
from build260 import *
STAGE='pass7'

def rebuild_upper(ob):
 assert len(ob.data.vertices)==2018
 pts=[(ob.matrix_world@v.co).copy() for v in ob.data.vertices];centers=[pts[0]]+[sum(pts[1+i*32:1+(i+1)*32],Vector())/32 for i in range(63)]+[pts[-1]];inv=ob.matrix_world.inverted();changes=0;maxshift=0.;lastB=None
 # The old projection damage continues below the temple into the middle rows.
 # Reconstruct that complete segment, rather than blending back into the patch.
 C=[];forelock='Side-Sweep' in ob.name and int(ob.name.split()[-1]) in [0,1,7]
 for i,p in enumerate(centers):
  weights=[(k,math.exp(-((k-i)/2.)**2)) for k in range(max(0,i-5),min(65,i+6))];q=sum((centers[k]*w for k,w in weights),Vector())/sum(w for k,w in weights);C.append(p.lerp(q,.7))
 if forelock:
  for i in range(13):
   D=(C[i]-a.C).normalized();hit=c.HEAD.ray_cast(a.C,D,2)[0];C[i]=C[i].lerp(hit-D*.004,1-smooth(i/12))
 widths=[];phase=0.
 for row in range(1,64):
  center=C[row];T=(C[row+1]-C[row-1]).normalized();N=(center-a.C).normalized();N-=T*N.dot(T);N.normalize();B=T.cross(N).normalized();off=[q-centers[row] for q in pts[1+(row-1)*32:1+row*32]];widths.append(sqrt(sum(q.dot(B)**2 for q in off)/16))
  if row==52:phase=math.atan2(off[0].dot(N),off[0].dot(B))
 for row in range(1,64):
  t=row/64;weight=(1 if forelock else smooth((row-7)/8))*(1-smooth((row-50)/8))
  if weight<=0:continue
  center=C[row];T=(C[row+1]-C[row-1]).normalized();N=(center-a.C).normalized();N-=T*N.dot(T)
  if N.length<.02:N=Vector((0,-1,0))-T*T.dot(Vector((0,-1,0)))
  N.normalize();B=T.cross(N).normalized();ring=pts[1+(row-1)*32:1+row*32];off=[q-centers[row] for q in ring]
  base_width=max(.043,min(.070,float(np.median(widths[42:55]))));w=base_width*(.88+.12*sin(pi*t));d=.016+.003*sin(pi*t);angle=phase;new=[]
  if forelock:w*=.10+.90*smooth(row/10);d*=.10+.90*smooth(row/10)
  for j in range(32):
   ph=2*pi*j/32+angle;detail=(.0017*cos(cos(ph)*32+.35*sin(t*5))+.0006*cos(cos(ph)*75+.2*sin(t*7)))*max(0,sin(ph))**3;new.append(center+B*(w*cos(ph))+N*(d*sin(ph)+detail))
  # A single center correction keeps cross-sections round at the temple.
  shift=0.;radial=(center-a.C).normalized()
  for j,q in enumerate(new):
   if sin(2*pi*j/32+angle)<.5:continue
   D=q-a.C;hit,_,_,dist=c.HEAD.ray_cast(a.C,D.normalized(),2)
   if hit is not None:shift=max(shift,dist+.007-D.length)
  shift*=smooth(row/(12 if forelock else 8))
  if row<6:
   hit=c.HEAD.ray_cast(a.C,radial,2)[0];center_shift=(hit-radial*.005-center)*(1-smooth(row/6));new=[q+center_shift for q in new]
  for j,q in enumerate(new):
   k=1+(row-1)*32+j;target=pts[k].lerp(q+radial*shift,weight);maxshift=max(maxshift,(target-pts[k]).length);ob.data.vertices[k].co=inv@target;changes+=1
 ob.data.vertices[0].co=inv@(C[0] if forelock else pts[0])
 old.author_uv(ob,32,65);return dict(name=ob.name,vertices_changed=changes,max_shift=maxshift,root_tips_exact=not forelock,last_six_rings_exact=True,forelock_root_seated_under_neighboring_part=forelock,full_temple_and_mid_length_cross_sections_reconstructed=True)

for style in STYLES['Feminine']:
 arg=next((x.split('=',1)[1].split(',') for x in sys.argv if x.startswith('--styles=')),None)
 if arg and style not in arg:continue
 s=load260('Feminine',style);frozen=protect(s);obs=female_source(s,style);report={}
 if style=='box-braids':
  before=min((ob.matrix_world@v.co).z for ob in obs for v in ob.data.vertices)
  for ob in obs:
   inv=ob.matrix_world.inverted()
   for v in ob.data.vertices:
    p=ob.matrix_world@v.co;p.z+=.075*smooth((1.85-p.z)/.60);v.co=inv@p
  report=dict(method='Shorten lower braid fall modestly with ties moving with the same path; roots retained',min_before=before,min_after=min((ob.matrix_world@v.co).z for ob in obs for v in ob.data.vertices))
 else:
  reports=[]
  for ob in list(obs):
   if ob.name.startswith('Recessed roots'):
    bm=bmesh.new();bm.from_mesh(ob.data);bad=[f for f in bm.faces if (ob.matrix_world@f.calc_center_median()).z<2.18];bmesh.ops.delete(bm,geom=bad,context='FACES');bm.to_mesh(ob.data);bm.free();continue
   if len(ob.data.vertices)==2018:reports.append(rebuild_upper(ob))
  report=dict(method='Reconstruct round whole root cross-sections and smooth root trajectories; remove exposed smooth temple support faces. No pointwise projection or texture cover-up',locks=reports)
 check(s,frozen);save260(s,'Feminine',style,STAGE,report)
print('FEMALE260_COMPLETE',flush=True)
