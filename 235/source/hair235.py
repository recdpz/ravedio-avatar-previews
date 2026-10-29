from common235 import *
from math import sin,cos,pi,sqrt
def lock(name,points,widths,depths,phase=0,mat=None,n=56,sides=18,root=.78,tip=.07,rough=False):
 ps=a.sample(points,n);v=[];f=[];prev=None
 for i,p in enumerate(ps):
  t=i/(n-1);T=(ps[min(i+1,n-1)]-ps[max(0,i-1)]).normalized();out=Vector((p.x/.50**2,(p.y-.015)/.43**2,max(.03,p.z-1.86)/.48**2)).normalized();N=out-T*out.dot(T)
  if N.length<.1:N=Vector((0,-1,0))-T*T.dot(Vector((0,-1,0)))
  N.normalize();B=T.cross(N).normalized()
  if prev is not None and B.dot(prev)<0:B=-B;N=-N
  prev=B;w=float(np.interp(t,np.linspace(0,1,len(widths)),widths));d=float(np.interp(t,np.linspace(0,1,len(depths)),depths));fall=max(.035,min(1,(1-t)/tip))**.48;w*=min(1,root+t*10)*fall;d*=fall
  for j in range(sides):
   q=2*pi*j/sides;ac=cos(q);front=max(0,sin(q));relief=(.0012*cos(ac*18+phase+.6*sin(t*5))+.0005*cos(ac*43+phase))*front**3
   if rough:relief+=.0010*sin(q*7+t*53+phase)+.0006*sin(q*11-t*79)
   v.append(tuple(p+B*(w*ac)+N*(d*sin(q)+relief)))
 for i in range(n-1):
  for j in range(sides):k=i*sides+j;l=i*sides+(j+1)%sides;f.append((k,l,l+sides,k+sides))
 f.extend([tuple(range(sides-1,-1,-1)),tuple((n-1)*sides+j for j in range(sides))]);return a.mesh(name,v,f,mat or a.M['hair'],'hair')
def boundary(ph):return 1.91-.84*max(0,cos(ph))**2.5
def scalp(kind='fade',top=.78):
 rng=random.Random(235);nv=66;nu=176;v=[];f=[];cols=[]
 for j in range(nv+1):
  t=j/nv
  for i in range(nu):
   ph=2*pi*i/nu;end=(1.94-.74*max(0,cos(ph))**2.2) if kind=='buzz' else boundary(ph);th=.004+t*end
   # Color is neutral; coverage alone creates the gradient, so all hair colors work.
   alpha=(.96 if kind!='buzz' else .20)*smooth((1-t)/(.018 if kind=='buzz' else .035))
   if kind in ['fade','buzz']:
    band=((.17 if cos(ph)>.65 else .46) if kind=='buzz' else (1.0 if cos(ph)>.65 else .70));alpha*=.09+.91*smooth((end-th)/band)
   lift=.0006 if kind=='buzz' else .0028 if kind=='fade' else .024+.009*sin(th*8+ph*5)**2
   v.append(tuple(h.head_surface(th,ph,lift)));cols.append((1,1,1,alpha))
 for j in range(nv):
  for i in range(nu):k=j*nu+i;l=j*nu+(i+1)%nu;f.append((k,l,l+nu,k+nu))
 f.append(tuple(range(nu-1,-1,-1)));m=a.material('Hair / neutral coverage235',(.060,.022,.011),.72 if kind=='buzz' else .43);m.node_tree.nodes['Principled BSDF'].inputs['Specular IOR Level'].default_value=.16 if kind=='buzz' else .40;o=a.mesh('Hair / seated '+kind+' coverage235',v,f,m,'hair');rgba(o,cols)
 if kind=='buzz':
  uv=o.data.uv_layers.new(name='Cut grain UV235')
  for poly in o.data.polygons:
   high=any(vi%nu>nu*.9 for vi in poly.vertices)
   for li,vi in zip(poly.loop_indices,poly.vertices):row,col=divmod(vi,nu);uv.data[li].uv=(1 if high and col==0 else col/nu,row/nv)
  rng2=np.random.default_rng(235);grain=np.repeat(np.repeat(rng2.uniform(.46,1.0,(128,256)),4,axis=0),2,axis=1);grain*=.94+.06*np.sin(np.arange(512)[:,None]*2.4);pix=np.ones((512,512,4),dtype='f');pix[:,:,:3]=grain[:,:,None];im=bpy.data.images.new('Hair / neutral clipped grain235',width=512,height=512);im.pixels.foreach_set(pix.ravel());im.pack();tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;mix=m.node_tree.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[2].default_value=(.060,.022,.011,1);m.node_tree.links.new(tex.outputs['Color'],mix.inputs[1]);m.node_tree.links.new(mix.outputs[0],m.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
 # Dense tiny actual cut fibers reinforce the gradient without a painted opaque shell.
 if kind in ['fade','buzz']:
  vv=[];ff=[];cc=[];count=7000 if kind=='buzz' else 5200
  for k in range(count):
   ph=rng.random()*2*pi;end=(1.94-.74*max(0,cos(ph))**2.2) if kind=='buzz' else boundary(ph);th=math.acos(1-rng.random()*(1-cos(end)))
   if kind=='fade' and th<top:continue
   distance=end-th;density=(.80+.20*smooth(distance/.12)) if kind=='buzz' else .10+.90*smooth(distance/.65)
   if rng.random()>density:continue
   p=h.head_surface(th,ph,.0010 if kind=='buzz' else .0045);N=(p-a.C).normalized();B=Vector((cos(ph),sin(ph),0));T=N.cross(B).normalized();r=.00065 if kind=='buzz' else .00165;length=.0015 if kind=='buzz' else .0048;off=len(vv)
   vv.extend([tuple(p+B*r+T*length),tuple(p-B*r+T*length),tuple(p-B*r-T*length),tuple(p+B*r-T*length)]);ff.append((off,off+1,off+2,off+3));cc.extend([(1,1,1,.55 if kind=='buzz' else .85)]*4)
  o=a.mesh('Hair / fine cut fiber235',vv,ff,a.material('Hair / cut grain235',(.105,.043,.023),.42),'hair');rgba(o,cc)
def taper():
 for o in list(bpy.context.scene.objects):
  if o.get('component159')!='hair':continue
  if 'short sides' in o.name or 'fine direction' in o.name:u.delete(o);continue
  if not o.data.color_attributes:continue
  c=o.data.color_attributes[0]
  for vert,col in zip(o.data.vertices,c.data):
   p=o.matrix_world@vert.co;side=smooth((abs(p.x)-.18)/.22);rear=smooth((p.y-.15)/.15)
   cutoff=2.09+.075*max(side,rear);col.color[3]*=smooth((p.z-cutoff)/.13)
 scalp('fade',.74)
def curly(afro=False,bandana=False):
 if afro:
  coiled_mass();return
 scalp('fade',.70);rng=random.Random(235)
 # Dense contiguous rooted volume follows the head, with irregular curl relief.
 count=245 if afro else 145;maxth=.84 if bandana else 1.76 if afro else 1.07
 for k in range(count):
  ph=k*pi*(3-sqrt(5))+rng.uniform(-.10,.10);th=math.acos(1-(k+.5)/count*(1-cos(maxth)));end=boundary(ph)-(.04 if afro else .12)
  if th>end:continue
  lift=(.057 if afro else .037)+(.025 if afro else .022)*cos(th*.7);p=h.head_surface(th,ph,lift);N=(p-a.C).normalized();B=Vector((cos(ph),sin(ph),0));T=N.cross(B).normalized();turn=rng.uniform(-pi,pi);A=B*cos(turn)+T*sin(turn);B2=N.cross(A);r=rng.uniform(.034,.052) if afro else rng.uniform(.041,.064);pts=[]
  for t in np.linspace(0,1,18):
   # Broad incomplete S turns. Ends tuck back into neighboring masses.
   across=r*sin((t-.15)*1.48*pi);along=r*(t-.5)*1.60;lift2=.017*sin(pi*t)
   pts.append(p+A*across+B2*along+N*lift2)
  lock('Hair / '+('coiled afro' if afro else 'top curl')+'235 '+str(k),pts,[.018,.031,.030,.025,.013],[.013,.026,.028,.025,.013],k*.73,n=32,sides=16,root=.85,tip=.12)
def coiled_mass():
 coiled_puffs()
def coiled_puffs(bandana=False):
 rng=random.Random(901);nu=144;nv=64;v=[];f=[]
 def edge(ph):return (.92+.12*max(0,-cos(ph))) if bandana else 1.70-.60*max(0,cos(ph))**2
 for j in range(nv+1):
  for i in range(nu):
   ph=2*pi*i/nu;th=.003+(j/nv)*edge(ph);lift=.050+.050*cos(th*.8)
   if bandana:lift=.012+(lift-.012)*(1-smooth((j/nv-.72)/.28))
   v.append(tuple(h.head_surface(th,ph,lift)))
 for j in range(nv):
  for i in range(nu):k=j*nu+i;l=j*nu+(i+1)%nu;f.append((k,l,l+nu,k+nu))
 f.append(tuple(range(nu-1,-1,-1)));mat=a.material('Hair / dense coiled texture235',(.080,.029,.014),.46);base=a.mesh('Hair / continuous afro foundation235',v,f,mat,'hair')
 # Voxel union needs a closed support volume. An open cap disappears and
 # leaves the curls floating over skin, particularly in held-back variants.
 solid=base.modifiers.new('Closed rooted curl support235','SOLIDIFY');solid.thickness=.045;solid.offset=-1;bpy.ops.object.select_all(action='DESELECT');base.select_set(True);bpy.context.view_layer.objects.active=base;bpy.ops.object.modifier_apply(modifier=solid.name)
 for k in range(260):
  ph=k*pi*(3-sqrt(5))+rng.uniform(-.12,.12);th=math.acos(1-(k+.5)/260*1.23)+rng.uniform(-.035,.035)
  if th>edge(ph)-(.11 if bandana else -.025):continue
  N=(h.head_surface(th,ph)-a.C).normalized();p=h.head_surface(th,ph,.061+.057*cos(th*.8));B=Vector((cos(ph),sin(ph),0));T=N.cross(B).normalized();r=rng.uniform(.035,.064);v=[];f=[];phase=rng.random()*pi*2
  for j in range(17):
   lat=pi*j/16
   for i in range(24):
    q=2*pi*i/24;relief=1+.055*sin(3*q+lat*4+phase)*sin(lat)**2+.03*sin(q*7-lat*8);off=(B*cos(q)+T*sin(q))*r*sin(lat)*relief+N*(r*.68*cos(lat));v.append(tuple(p+off))
  for j in range(16):
   for i in range(24):z=j*24+i;n=j*24+(i+1)%24;f.append((z,n,n+24,z+24))
  a.mesh('Hair / compact coil puff235 '+str(k),v,f,mat,'hair')
 if bandana:
  for k in range(48):
   ph=k*2*pi/48;th=edge(ph)-.035;p=h.head_surface(th,ph,.023);N=(p-a.C).normalized();A=Vector((cos(ph),sin(ph),0));B=N.cross(A).normalized();pts=[p-A*.030-B*.018,p-A*.015+B*.017+N*.009,p+A*.018+B*.019+N*.009,p+A*.029-B*.012];lock('Hair / held coil edge235 '+str(k),pts,[.010,.017,.017,.007],[.008,.014,.014,.006],k*.7,mat=mat,n=30,sides=14,tip=.15)
 bpy.ops.object.select_all(action='DESELECT');obs=[o for o in bpy.context.scene.objects if o.get('component159')=='hair'];
 for o in obs:o.select_set(True)
 bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();o=bpy.context.object;o.name='Hair / unified coiled afro235';mod=o.modifiers.new('Connected coiled volume235','REMESH');mod.mode='VOXEL';mod.voxel_size=.005;mod.use_smooth_shade=True;mod=o.modifiers.new('Soft curl junctions235','SMOOTH');mod.factor=.7;mod.iterations=3
def flow(middle=False):
 if not middle:
  swept_flow();return
 scalp('fade');rng=random.Random(819)
 # Crown strips begin on the narrow visible part and sweep backwards in layers.
 for side in [-1,1]:
  for j in range(9):
   y=-.255+j*.058;root=a.surface(side*.010 if middle else .115,y,.018);ph=side*(.82+j*.265);endth=1.66 if j<5 else 1.86
   pts=[root,h.head_surface(.48,ph*.7,.045),h.head_surface(.87,ph,.063),h.head_surface(1.20,ph+.12*side,.058),h.head_surface(1.48,ph+.20*side,.044)]
   end=h.head_surface(endth,ph+.35*side,.037);end.y+=.030;end.z-=.016 if middle else .060;pts += [end]
   if j<2:pts=pts[:4]+[h.head_surface(1.38,side*(1.30+j*.16),.036)]
   lock('Hair / '+('center part' if middle else 'swept flow')+'235 '+str(side)+' '+str(j),pts,[.025,.069,.074,.066,.038,.003],[.009,.025,.027,.024,.014,.003],j*.7,n=64,tip=.14)
  for j in range(3):
   root=a.surface(side*(.007+j*.008) if middle else .10,-.30+j*.032,.021)
   pts=[root,Vector((side*.115,-.357+j*.015,2.30+j*.008)),Vector((side*.28,-.335+j*.026,2.21)),Vector((side*.40,-.21+j*.03,2.07)),Vector((side*.43,-.08+j*.035,2.01+j*.018))]
   if not middle:
    for k,p in enumerate(pts):p.z+=.035*sin(pi*k/4);p.y+=.035*sin(pi*k/4)
   lock('Hair / soft front curtain235 '+str(side)+' '+str(j),pts,[.018,.052,.065,.042,.004],[.009,.027,.026,.018,.003],j+side,n=60,tip=.16)
 # Narrow, rooted banks close triangular crown holes while retaining a fine part.
 for side in [-1,1]:
  def bank(w,t):
   y=-.27+.55*t;x=(side*(.004+.095*w) if middle else .115+side*(.004+.095*w));p=a.surface(x,y,.020+.009*sin(pi*w));return p
  a.grid('Hair / part root bank235 '+str(side),bank,20,54,a.M['hair'],.005,group='hair')
 for j in range(8):
  x=-.29+j*.083;pts=[a.surface(x*.3,.22,.028),Vector((x*.8,.36,2.15)),Vector((x,.443,1.99)),Vector((x+.010*sin(j),.438,1.85 if middle else 1.80)),Vector((x*.92,.48,1.83 if middle else 1.76))]
  lock('Hair / feathered nape235 '+str(j),pts,[.025,.061,.062,.035,.003],[.012,.027,.024,.012,.003],j,n=58,tip=.16)
 for j in [-1,0,1]:
  pts=[a.surface(j*.038,.17,.025),a.surface(j*.05,.26,.035),Vector((j*.06,.365,2.19)),Vector((j*.075,.442,1.94)),Vector((j*.07,.47,1.84))];lock('Hair / seated crown connection235 '+str(j),pts,[.025,.045,.050,.035,.004],[.012,.024,.023,.015,.003],j,n=54,tip=.14)
def swept_flow():
 scalp('fade');rng=random.Random(941)
 for j in range(13):
  x=-.37+j*.0615;z=1.88+.455*sqrt(max(.01,1-(x/.48)**2-(-.27/.405)**2));front=Vector((x,-.255,z+.018));sgn=1 if x>0 else -1
  pts=[front,Vector((x*.96,-.21,2.30-.20*(abs(x)/.4)**2)),Vector((x*.95,-.04,2.405-.22*(abs(x)/.4)**2)),Vector((x*.98,.21,2.32-.17*(abs(x)/.4)**2)),Vector((x,.39,2.11)),Vector((x*.96,.442,1.92)),Vector((x*.97+sgn*.018,.49,1.81+.022*sin(j*1.7)))]
  lock('Hair / brushed back flow235 '+str(j),pts,[.029,.053,.058,.058,.054,.033,.003],[.012,.027,.029,.028,.023,.014,.003],j*.9,n=72,tip=.14)
 for side in [-1,1]:
  for j in range(4):
   pts=[h.head_surface(.97+j*.075,side*(.90+j*.10),.023),h.head_surface(1.12+j*.05,side*(1.38+j*.12),.045),h.head_surface(1.46,side*(1.85+j*.13),.048),h.head_surface(1.76,side*(2.03+j*.14),.038),Vector((side*(.39-j*.022),.32+j*.025,1.83+.024*j))]
   lock('Hair / flowing temple layer235 '+str(side)+' '+str(j),pts,[.024,.055,.057,.034,.003],[.010,.025,.023,.014,.003],j,n=60,tip=.16)
def locs():
 scalp('dense');a.M['hair']=a.material('Hair / loc fiber235',(.105,.039,.020),.50);a.M['hair'].node_tree.nodes['Principled BSDF'].inputs['Specular IOR Level'].default_value=.25;rng=random.Random(1010)
 for ring,th0 in enumerate([.16,.40,.65,.89,1.13]):
  count=[5,10,14,18,20][ring]
  for j in range(count):
   ph=2*pi*(j+.4*(ring%2))/count;th=min(th0,boundary(ph)-.16);root=h.head_surface(th,ph,.018);p=h.head_surface(min(1.55,th+.4),ph+.07,.042);end=h.head_surface(min(1.83,th+.68),ph+.10,.05);end.z=max(1.87,end.z-.065);end.y+=.024*max(0,-cos(ph))
   if cos(ph)>.25:end.z=max(2.10,end.z);end.y+=.025
   pts=[root,root.lerp(p,.6)+Vector((.006*sin(j),0,.026)),p,end,end+Vector((.010*sin(j),.010, -.025))];r=.029+rng.random()*.009
   lock('Hair / short loc235 '+str(ring)+' '+str(j),pts,[r*.72,r,r*.96,r*.88,r*.65],[r*.70,r*.83,r*.81,r*.77,r*.53],j*.7,n=42,sides=16,tip=.025,rough=True)
def build(style):
 a.setup();a.GROUP='hair'
 if style=='taper':taper();return
 remove(['hair'])
 if style=='buzz':scalp('buzz')
 elif style in ['curly-top','afro']:curly(style=='afro')
 elif style in ['flow','middle-part']:flow(style=='middle-part')
 elif style=='locs':locs()
def main():
 args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [];styles=args[0].split(',') if args else ['taper','buzz','curly-top','afro','flow','locs','middle-part'];records=json.loads((P/'hair235.json').read_text()) if (P/'hair235.json').exists() else {}
 for style in styles:
  s=load('Masculine');protected=protect(s);build(style);check(s,protected);key='Masculine-'+style;parts=save(s,key,['hair']);s=bpy.context.scene;render(s,key,['front','threequarter','profile','rear','top']);records[style]=dict(parts=parts,source=str(P/'sources'/f'{key}.blend'),protected_exact=True,status='construction review');u.dump(P/'hair235.json',records);print('HAIR235',style,flush=True)
if __name__=='__main__':main()
