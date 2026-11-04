import sys,math,random,json
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue252')
from common252 import *
import bmesh
from math import sin,cos,pi,sqrt

def material(name,rough=.34):return a.material('Hair252 / '+name,(.120,.047,.026),rough)
def init():
 a.setup();a.GROUP='hair';a.M['hair']=material('sculpted locks');a.M['shine']=a.material('Hair252 / gentle tonal variation',(.129,.052,.030),.34);a.M['dark']=material('buried roots',.38)
def accent(k):return a.M['shine'] if k%5==2 else a.M['hair']

def normal_texture(mat,kind='cut'):
 name='Hair252 / '+kind+' normal';im=bpy.data.images.get(name)
 if im is None:
  w,h=(1024,256) if kind=='cut' else (512,512);x,y=np.meshgrid(np.linspace(0,1,w),np.linspace(0,1,h));q=2*pi*(x*(180 if kind=='cut' else 65)+.25*np.sin(y*2*pi*5)+.04*np.sin(x*2*pi*17));height=np.cos(q)*(.32+.06*np.cos(y*2*pi*17))+.08*np.cos(q*1.91+y*2*pi*21)
  if kind=='cut':
   rng=np.random.default_rng(77252);z=rng.random((h,w));height=(z*.3+np.roll(z,1,0)*.25+np.roll(z,-1,0)*.25+np.roll(z,2,0)*.10+np.roll(z,-2,0)*.10)*2
  gy,gx=np.gradient(height);nx=-gx*.58;ny=-gy*.38;nz=np.ones_like(nx);norm=np.sqrt(nx*nx+ny*ny+nz*nz);pixels=np.stack(((nx/norm+1)/2,(ny/norm+1)/2,(nz/norm+1)/2,np.ones_like(nx)),axis=-1).astype('f');im=bpy.data.images.new(name,width=w,height=h);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(pixels.ravel());im.pack()
 nodes=mat.node_tree.nodes
 if kind=='cut':
  name='Hair252 / dense close-cut pigment';col=bpy.data.images.get(name)
  if col is None:
   rng=np.random.default_rng(88252);pixels=np.ones((256,1024,4),dtype='f');z=rng.random((256,1024));z=.75+.25*(z*.6+np.roll(z,1,0)*.2+np.roll(z,-1,0)*.2);pixels[:,:,:3]=z[:,:,None];col=bpy.data.images.new(name,width=1024,height=256);col.colorspace_settings.name='Non-Color';col.pixels.foreach_set(pixels.ravel());col.pack()
  pigment=nodes.new('ShaderNodeTexImage');pigment.image=col;mix=nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[2].default_value=nodes['Principled BSDF'].inputs['Base Color'].default_value;mat['hairBase252']=list(mix.inputs[2].default_value);mat.node_tree.links.new(pigment.outputs['Color'],mix.inputs[1]);mat.node_tree.links.new(mix.outputs[0],nodes['Principled BSDF'].inputs['Base Color'])
 tex=nodes.new('ShaderNodeTexImage');tex.image=im;normal=nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.65 if kind=='cut' else .24;mat.node_tree.links.new(tex.outputs['Color'],normal.inputs['Color']);mat.node_tree.links.new(normal.outputs['Normal'],nodes['Principled BSDF'].inputs['Normal'])

def spline(points,n):
 ps=[Vector(p) for p in points];out=[]
 for x in np.linspace(0,len(ps)-1,n):
  i=min(len(ps)-2,int(x));t=x-i;p1=ps[i];p2=ps[i+1];p0=ps[i-1] if i else p1*2-p2;p3=ps[i+2] if i+2<len(ps) else p2*2-p1
  t0=0;t1=t0+max(1e-5,(p1-p0).length**.5);t2=t1+max(1e-5,(p2-p1).length**.5);t3=t2+max(1e-5,(p3-p2).length**.5);z=t1+t*(t2-t1)
  A1=p0*((t1-z)/(t1-t0))+p1*((z-t0)/(t1-t0));A2=p1*((t2-z)/(t2-t1))+p2*((z-t1)/(t2-t1));A3=p2*((t3-z)/(t3-t2))+p3*((z-t2)/(t3-t2));B1=A1*((t2-z)/(t2-t0))+A2*((z-t0)/(t2-t0));B2=A2*((t3-z)/(t3-t1))+A3*((z-t1)/(t3-t1));out.append(B1*((t2-z)/(t2-t1))+B2*((z-t1)/(t2-t1)))
 return out

def lock(name,points,widths,depths,phase=0,mat=None,n=64,sides=24,grain=.0008,round_tip=True):
 ps=spline(points,n) if len(points)!=n else [Vector(p) for p in points];v=[];f=[];prev=None
 if name.startswith(('flow','middle')):
  for i,p in enumerate(ps):
   if p.z>2.0 and i/(n-1)<.80:
    d=p-a.C;hit,_,_,dist=c.HEAD.ray_cast(a.C,d.normalized(),2)
    if hit is not None:
     lift=max(.027,min(.047,d.length-dist));ps[i]=hit+d.normalized()*lift
 for i,p in enumerate(ps):
  t=i/(n-1);T=(ps[min(i+1,n-1)]-ps[max(0,i-1)]).normalized();out=(p-a.C).normalized()
  if prev is None:
   N=out-T*out.dot(T)
   if N.length<.05:N=Vector((0,-1,0))-T*T.dot(Vector((0,-1,0)))
   N.normalize();B=T.cross(N).normalized()
  else:
   B=prev-T*prev.dot(T)
   if B.length<.05:B=T.cross(out)
   B.normalize();N=B.cross(T).normalized()
  prev=B;w=float(np.interp(t,np.linspace(0,1,len(widths)),widths));d=float(np.interp(t,np.linspace(0,1,len(depths)),depths));fall=math.sqrt(max(.0004,1-((t-.90)/.10)**2)) if round_tip and t>.90 else 1
  for j in range(sides):
   q=2*pi*j/sides;ac=cos(q);ridge=grain*(.65*cos(ac*26+phase+.18*sin(t*5))+.25*cos(ac*53+phase))*max(0,sin(q))**3;v.append(tuple(p+B*(w*ac*fall)+N*(d*sin(q)*fall+ridge*fall)))
 for i in range(n-1):
  for j in range(sides):x=i*sides+j;y=i*sides+(j+1)%sides;f.append((x,y,y+sides,x+sides))
 f.extend([tuple(range(sides-1,-1,-1)),tuple((n-1)*sides+j for j in range(sides))]);ob=a.mesh('Hair252 / '+name,v,f,mat or a.M['hair'],'hair');uv=ob.data.uv_layers.new(name='Authored hair flow252')
 for face in ob.data.polygons:
  seam=any(k%sides>sides*.9 for k in face.vertices)
  for li,k in zip(face.loop_indices,face.vertices):row,col=divmod(k,sides);uv.data[li].uv=(1 if seam and col==0 else col/sides,row/(n-1))
 ob['hairFlow252']=True;return ob

def author_uv(ob,sides,rows):
 assert len(ob.data.vertices)==sides*(rows-2)+2,(ob.name,len(ob.data.vertices))
 uv=ob.data.uv_layers.new(name='Authored hair flow252')
 for f in ob.data.polygons:
  coords=[]
  for k in f.vertices:
   if k in [0,len(ob.data.vertices)-1]:coords.append((.25,0 if k==0 else 1))
   else:row,col=divmod(k-1,sides);coords.append(((col/sides+.25)%1,(row+1)/(rows-1)))
  seam=max(q[0] for q in coords)-min(q[0] for q in coords)>.5
  for li,(u0,t) in zip(f.loop_indices,coords):uv.data[li].uv=(u0+1 if seam and u0<.5 else u0,t)

def boundary(ph,buzz=False):
 angle=abs((ph+pi)%(2*pi)-pi)
 if buzz:return .965-.035*sin(min(angle,.95)*1.5)**2+.86*smooth((angle-.93)/.75)
 if angle<.92:return .79-.035*sin(angle*1.5)**2
 return (.94 if buzz else .79)+(.88 if buzz else 1.00)*smooth((angle-.92)/.70)-.035*cos(ph*2)

def clip(buzz=False):
 nu,nv=384,96;v=[];f=[];col=[]
 for j in range(nv+1):
  t=j/nv
  for i in range(nu):
   ph=i/nu*2*pi;end=boundary(ph,buzz);th=.004+t*end;edge=end-th;front=cos(ph)>.66;density=smooth(edge/(.045+.295*smooth((abs((ph+pi)%(2*pi)-pi)-.65)/.45)));alpha=.32*smooth((1-t)/(.025+.05*smooth((abs((ph+pi)%(2*pi)-pi)-.75)/.35))) if buzz else (.04+.96*density)*smooth((1-t)/.018)
   lift=(.009+.007*density if buzz else .0025+.027*density)+.0010*sin(ph*250+sin(ph*19)*2+th*8)*density*smooth(t/.10)*smooth((1-t)/.05);v.append(tuple(sp(th,ph,lift)));col.append((1,1,1,alpha))
 for j in range(nv):
  for i in range(nu):k=j*nu+i;l=j*nu+(i+1)%nu;f.append((k,l,l+nu,k+nu))
 f.append(tuple(range(nu-1,-1,-1)));mat=material('buzz edge' if buzz else 'close fade coverage',.59 if buzz else .49);normal_texture(mat);o=a.mesh('Hair252 / close continuous clipped '+('buzz' if buzz else 'taper'),v,f,mat,'hair');rgba(o,col);uv=o.data.uv_layers.new(name='Continuous clipped flow252')
 for face in o.data.polygons:
  seam=any(k%nu>nu*.9 for k in face.vertices)
  for li,k in zip(face.loop_indices,face.vertices):row,q=divmod(k,nu);uv.data[li].uv=(1 if seam and q==0 else q/nu,row/nv)
 return o

def taper():
 # Recover the earlier coherent fade; discard the later particle layer.
 parts=json.loads(Path('E:/Ravedio-Avatar/refinement153/Taper-geometry.json').read_text());skin=tree([head_object(bpy.context.scene)])
 for k,part in enumerate(parts):
  if part['material'] not in ['hair','fade']:continue
  if part['name']=='Hair / Taper fine direction':continue
  verts=[Vector(x) for x in part['position']]
  if part['material']=='fade':
   for i,p in enumerate(verts):
    d=p-a.C
    if d.length<.2:continue
    unit=d.normalized();hit,_,_,dist=skin.ray_cast(a.C,unit,2)
    if hit is not None:
     density=float(part['color'][i][3]);verts[i]=hit+unit*(.003+.015*density+.0006*sin(math.atan2(unit.x,-unit.y)*170))
   mat=a.material('Hair252 / restored153 fade coverage',(.105,.039,.020),.44);ob=a.mesh('Hair252 / recovered directional taper',verts,np.asarray(part['index']).reshape(-1,3).tolist(),mat,'hair');rgba(ob,part['color']);normal_texture(mat)
   uv=ob.data.uv_layers.new(name='Recovered continuous fade flow252')
   for face in ob.data.polygons:
    for li,i in zip(face.loop_indices,face.vertices):d=verts[i]-a.C;uv.data[li].uv=((math.atan2(d.x,-d.y)+pi)/(2*pi),math.acos(max(-1,min(1,d.normalized().z)))/1.9)
  else:
   for i,p in enumerate(verts):
    weight=max(smooth((2.16-p.z)/.23),smooth((p.y-.18)/.16)*.9);d=p-a.C;hit,_,_,dist=skin.ray_cast(a.C,d.normalized(),2)
    if hit is not None and d.length>dist+.025:verts[i]=p.lerp(a.C+d.normalized()*(dist+.025),weight*.82)
   ob=a.mesh('Hair252 / retained sweep '+part['name'],[tuple(x) for x in verts],np.asarray(part['index']).reshape(-1,3).tolist(),accent(k),'hair');author_uv(ob,32,81)



def swept_surface(long=False):
 # Hair grows from a part seam across one continuous sculpted surface per bank.
 # The same flow field determines crown, sides, lengths and strand detail.
 for side in [-1,1]:
  nu,nv=144,224;vv=[];ff=[]
  for j in range(nv+1):
   v=j/nv;ph=pi*v;root=surf((.045 if long else 0)+side*.004,-.295+.59*v,0);rd=(root-a.C).normalized();edge=.84+.96*smooth(ph/1.10);hd=(sp(edge,side*ph,0)-a.C).normalized();angle=math.acos(max(-1,min(1,rd.dot(hd))))
   for i in range(nu+1):
    t=i/nu;qt=min(t/.83,1);e=qt*angle;direction=(rd*sin(angle-e)+hd*sin(e))/max(.001,sin(angle));direction.normalize()
    if long:
     turn=side*.22*sin(pi*t)*sin(pi*v);direction=Vector((direction.x*cos(turn)-direction.y*sin(turn),direction.x*sin(turn)+direction.y*cos(turn),direction.z))
    hit=c.HEAD.ray_cast(a.C,direction,2)[0];phase=v*14+(.42 if long else .15)*sin(t*4.7+v*3)*sin(pi*v);ridge=.020*(.5+.5*cos(phase*2*pi))**1.4*smooth(v/.07)*smooth((1-v)/.07);micro=.0016*cos(phase*2*pi*6+.3*sin(t*5))*smooth(v/.07)*smooth((1-v)/.07);edge_clean=1-(1-smooth((1-t)/.08))*(1-smooth((ph-1.20)/.45));ridge*=edge_clean;micro*=edge_clean;lift=.018+(.015+ridge+micro)*sin(pi*t*.92)**.45
    p=hit+direction*lift
    if t>.72:
     q=smooth((t-.72)/.28);fall=((.15+.08*max(0,-cos(ph))) if long else .055)*smooth((ph-.50)/.80);p.z-=fall*q
     out=Vector((side*sin(ph),-cos(ph),0));p+=out*((.045 if long else .004)*sin(q*pi*.75)*sin(ph));p.z+=(.032 if long else .008)*sin(v*14*2*pi+.3)*q*smooth((ph-1.20)/.50)
    vv.append(tuple(p))
  for j in range(nv):
   for i in range(nu):x=j*(nu+1)+i;ff.append((x,x+1,x+nu+2,x+nu+1))
  mat=material('flowing sculpt '+('flow' if long else 'middle'),.35);o=a.mesh('Hair252 / coherent flowing bank '+str(side),vv,ff,mat,'hair');sol=o.modifiers.new('Closed sculpted hair edges','SOLIDIFY');sol.thickness=.013;sol.offset=-1;uv=o.data.uv_layers.new(name='Authored hair flow252')
  for face in o.data.polygons:
   us=[(k//(nu+1)/nv*14)%1 for k in face.vertices];seam=max(us)-min(us)>.5
   for li,k,u0 in zip(face.loop_indices,face.vertices,us):row,col=divmod(k,nu+1);uv.data[li].uv=(u0+1 if seam and u0<.5 else u0,col/nu)

def flow():swept_surface(True)
def middle():swept_surface(False)

def locs():
 from mathutils import kdtree
 mat=material('sectioned locs',.59);normal_texture(mat,'felt');sites=[];k=0
 for ring,count in enumerate([5,8,11,14]):
  for j in range(count):
   ph=2*pi*(j+.41*(ring%2))/count;th=(ring+.35)/4*boundary(ph,True);sites.append((th,ph,k));k+=1
 centers=[sp(th,ph,0) for th,ph,k in sites];kd=kdtree.KDTree(len(centers))
 for i,p in enumerate(centers):kd.insert(p,i)
 kd.balance();nu,nv=240,80;rv=[];rf=[]
 for j in range(nv+1):
  t=j/nv
  for i in range(nu):
   ph=i/nu*2*pi;th=.004+t*(boundary(ph,True)-.26);p=sp(th,ph,0);near=kd.find_n(p,2);ds=near[0][2];border=abs(near[1][2]-ds);lift=.010+.018*math.exp(-(ds/.07)**2)-.006*math.exp(-(border/.020)**2);lift+=.0011*cos(ph*126+th*8)*smooth((1-t)/.06);rv.append(tuple(sp(th,ph,lift*smooth((1-t)/.045)+.003)))
 for j in range(nv):
  for i in range(nu):x=j*nu+i;y=j*nu+(i+1)%nu;rf.append((x,y,y+nu,x+nu))
 rf.append(tuple(range(nu-1,-1,-1)));roots=a.mesh('Hair252 / coherent gathered loc roots',rv,rf,mat,'hair');uv=roots.data.uv_layers.new(name='Authored hair flow252')
 for face in roots.data.polygons:
  seam=any(k%nu>nu*.9 for k in face.vertices)
  for li,k in zip(face.loop_indices,face.vertices):row,col=divmod(k,nu);uv.data[li].uv=(1 if seam and col==0 else col/nu,row/nv)
 for th,ph,k in sites:
  if cos(ph)>.60 and th>.70:continue
  front=cos(ph)>.60;root=sp(th,ph,.032);end=Vector((.48*sin(ph),.015-.43*cos(ph),1.83+.065*sin(k*1.7)))
  if front:end=Vector((.46*sin(ph),-.405+.03*abs(sin(ph)),2.135+.025*sin(k*2)))
  else:end.z=min(end.z,root.z-.16)
  mid=sp(min(1.17 if front else 1.48,th+.43),ph+.025,.044);pen=mid.lerp(end,.65);pen.x+=.008*sin(k*.7);pts=[root,sp(min(1.1 if front else 1.4,th+.16),ph+.01,.043),mid,pen,end];r=.030+.0015*sin(k*1.7);lock('short sectioned loc '+str(k),pts,[.033,r,r,r*.98,r*.85],[.026,r*.87,r*.89,r*.87,r*.77],k*.7,mat,n=64,sides=20,grain=.0010)

def curl_mass(afro=False):
 from mathutils import noise
 if not afro:
  # Same coherent short graduation as the restored taper, without its long top.
  parts=json.loads(Path('E:/Ravedio-Avatar/refinement153/Taper-geometry.json').read_text());part=next(p for p in parts if p['name']=='Hair / Taper short sides');vv=[]
  for p,color in zip(part['position'],part['color']):
   d=Vector(p)-a.C;hit=c.HEAD.ray_cast(a.C,d.normalized(),2)[0];vv.append(tuple(hit+d.normalized()*(.003+.015*color[3])) if hit is not None else tuple(p))
  side=material('curly close fade coverage',.48);o=a.mesh('Hair252 / curly top short graduation',vv,np.asarray(part['index']).reshape(-1,3).tolist(),side,'hair');rgba(o,part['color']);normal_texture(side);uv=o.data.uv_layers.new(name='Continuous clipped flow252')
  for face in o.data.polygons:
   for li,i in zip(face.loop_indices,face.vertices):d=Vector(vv[i])-a.C;uv.data[li].uv=((math.atan2(d.x,-d.y)+pi)/(2*pi),math.acos(max(-1,min(1,d.normalized().z)))/1.9)
 edge=lambda ph:(1.43-.40*max(0,cos(ph))**2+.018*sin(ph*11)+.010*sin(ph*23)) if afro else .94+.006*sin(ph*11)
 mat=material('dense natural coil groups' if afro else 'tousled curl groups',.54 if afro else .40);mat.node_tree.nodes['Principled BSDF'].inputs['Specular IOR Level'].default_value=.32;nu,nv=320,136;vv=[];ff=[]
 def ht(th,ph):return (.064+.026*cos(th)) if afro else (.038+.055*max(0,cos(th)))
 if not afro:
  from mathutils import kdtree
  guides=[];rng=random.Random(92252)
  for k in range(54):
   ph=k*pi*(3-sqrt(5))+rng.uniform(-.2,.2);th=math.acos(1-(k+.5)/54*(1-cos(.91)));center=sp(th,ph,0);N=(center-a.C).normalized();U=(sp(min(1.9,th+.015),ph,0)-sp(max(.001,th-.015),ph,0)).normalized();V=N.cross(U).normalized();angle=rng.uniform(-pi,pi);U,V=U*cos(angle)+V*sin(angle),-U*sin(angle)+V*cos(angle)
   for t in np.linspace(0,1,40):
    raw=center+U*(t-.5)*.14+V*.034*sin((t-.5)*2*pi);d=(raw-a.C).normalized();hit=c.HEAD.ray_cast(a.C,d,2)[0];guides.append(hit)
  kd=kdtree.KDTree(len(guides))
  for k,p in enumerate(guides):kd.insert(p,k)
  kd.balance()
 for j in range(nv+1):
  t=j/nv
  for i in range(nu):
   ph=i/nu*2*pi;th=.003+t*edge(ph);base=sp(th,ph,0);macro=noise.fractal(base*17,.85,2.0,3);ridge=noise.ridged_multi_fractal(base*31,1.0,2.0,3,1.0,1.7);fine=noise.fractal(base*75,.7,2.0,2);distance=0 if afro else kd.find(base)[2];detail=(.014*macro+.028*ridge+.0045*fine) if afro else (.025*math.exp(-(distance/.016)**2)-.004*math.exp(-((distance-.030)/.010)**2)+.002*macro);lift=.003+(ht(th,ph)+detail-.003)*smooth((1-t)/(.18 if afro else .25));vv.append(tuple(sp(th,ph,lift)))
 for j in range(nv):
  for i in range(nu):x=j*nu+i;y=j*nu+(i+1)%nu;ff.append((x,y,y+nu,x+nu))
 ff.append(tuple(range(nu-1,-1,-1)));o=a.mesh('Hair252 / organic continuous coil volume',vv,ff,mat,'hair');sol=o.modifiers.new('Interior hair shell252','SOLIDIFY');sol.thickness=.009;sol.offset=-1

def curly252():
 # Merge rooted curved clumps into a coherent sculpt, avoiding detached loops.
 curl_mass(False);core=next(o for o in bpy.context.scene.objects if o.name.startswith('Hair252 / organic continuous coil volume'))
 for v in core.data.vertices:
  p=core.matrix_world@v.co;d=p-a.C;hit,_,_,dist=c.HEAD.ray_cast(a.C,d.normalized(),2)
  if hit is not None:
   lift=max(.002,(d.length-dist)*.38);q=p+Vector((0,.040*smooth((-p.y-.18)/.14),0));N=(q-a.C).normalized();front=c.HEAD.ray_cast(a.C,N,2)[0];v.co=front+N*lift
 bm=bmesh.new();bm.from_mesh(core.data);bad=[f for f in bm.faces if f.calc_center_median().y<-.27];bmesh.ops.delete(bm,geom=bad,context='FACES');bm.to_mesh(core.data);bm.free()
 mat=material('sculpted curl groups',.36);core.data.materials.clear();core.data.materials.append(mat);rng=random.Random(155252)
 for k in range(42):
  ph=k*pi*(3-sqrt(5));th=math.acos(1-(k+.5)/42*(1-cos(.76)));center=sp(th,ph,0);N=(center-a.C).normalized();U=(sp(th+.015,ph,0)-sp(max(.001,th-.015),ph,0)).normalized();V=N.cross(U).normalized();angle=rng.uniform(-1.1,1.1);U,V=U*cos(angle)+V*sin(angle),-U*sin(angle)+V*cos(angle);ps=[]
  for t in np.linspace(0,1,54):
   raw=center+U*(t-.5)*.145+V*.034*sin((t-.5)*2*pi);d=(raw-a.C).normalized();hit=c.HEAD.ray_cast(a.C,d,2)[0];ps.append(hit+d*(.026+.045*sin(pi*t)**.8))
  lock('rooted sculpt curl '+str(k),ps,[.012,.030,.032,.011],[.010,.019,.020,.009],k*.7,mat,n=54,sides=20,grain=.001)
 obs=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.get('component159')=='hair' and 'graduation' not in o.name]
 bpy.ops.object.select_all(action='DESELECT')
 for o in obs:
  bpy.context.view_layer.objects.active=o
  for m in list(o.modifiers):bpy.ops.object.modifier_apply(modifier=m.name)
  o.select_set(True)
 bpy.context.view_layer.objects.active=core;bpy.ops.object.join();core.name='Hair252 / unified rooted curly sculpt';core.data.remesh_voxel_size=.0038;bpy.ops.object.voxel_remesh();mod=core.modifiers.new('Soft sculpted curl joins','SMOOTH');mod.factor=.35;mod.iterations=3
 for f in core.data.polygons:f.use_smooth=True

def straight():
 # Keep the authored main lengths; replace the exposed temple root plate.
 with bpy.data.libraries.load('E:/Ravedio-Avatar/catalogue226/revision227/sources/Feminine-straight.blend',link=False) as (src,dst):dst.objects=list(src.objects)
 for ob in dst.objects:
  if ob is None:continue
  if ob.type=='MESH' and ob.get('component159')=='hair':
   bpy.context.scene.collection.objects.link(ob)
   if 'side sweep' in ob.name:author_uv(ob,32,65)
   if ob.name.startswith('Recessed roots'):
    bm=bmesh.new();bm.from_mesh(ob.data);bad=[f for f in bm.faces if f.calc_center_median().z<2.16];bmesh.ops.delete(bm,geom=bad,context='FACES');bm.to_mesh(ob.data);bm.free()
  else:u.delete(ob)

 # Remove grazing internal root faces which produce thin raster slivers on skin.
 for ob in [q for q in bpy.context.scene.objects if q.type=='MESH' and q.get('component159')=='hair']:
  bm=bmesh.new();bm.from_mesh(ob.data);bad=[];matrix=ob.matrix_world
  for f in bm.faces:
   p=matrix@f.calc_center_median()
   if p.z<2.12 or p.y>-.18:continue
   d=p-a.C;hit,_,_,dist=c.HEAD.ray_cast(a.C,d.normalized(),2)
   if hit is not None and d.length<dist+.009:bad.append(f)
  bmesh.ops.delete(bm,geom=bad,context='FACES');bm.to_mesh(ob.data);bm.free()

def build(style):
 b='Feminine' if style=='straight' else 'Masculine';s,_=load252(b,style);frozen=protect(s);remove(['hair']);init()
 if style=='taper':taper()
 elif style=='buzz':clip(True)
 elif style=='flow':flow()
 elif style=='middle-part':middle()
 elif style=='locs':locs()
 elif style=='curly-top':curly252()
 elif style=='afro':curl_mass(True)
 elif style=='straight':straight()
 check(s,frozen);u.bake(s);bpy.ops.file.pack_all();src=P/'sources'/f'{b}-{style}-hair252.blend';bpy.ops.wm.save_as_mainfile(filepath=str(src),compress=True);out=P/'components'/f'{b}-{style}-hair252.glb';ex.export(s,out,'hair');
 if '--no-render' not in sys.argv:render252(s,b+'-'+style,('front','profile','rear','top'))
 return dict(path='components/'+out.name,source=str(src),protected_exact=True)
if __name__=='__main__':
 styles=next((x.split('=',1)[1].split(',') for x in sys.argv if x.startswith('--styles=')),['taper','buzz','flow','middle-part','locs','curly-top','afro','straight']);out=json.loads((P/'hair252.json').read_text()) if (P/'hair252.json').exists() else {}
 for style in styles:
  out[style]=build(style);(P/'hair252.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8');print('GROOM252',style,flush=True)
 print('GROOM252_COMPLETE',len(out),flush=True)
