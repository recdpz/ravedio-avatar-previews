from common235 import *
from math import sin,cos,pi,sqrt
def textile(name,bandana=False):
 m=a.material(name,(1,1,1),.93);bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Sheen Weight'].default_value=.12;bs.inputs['Specular IOR Level'].default_value=.12
 if bandana:
  yy,xx=np.mgrid[0:128,0:64];mask=np.zeros((128,64),dtype=bool)
  points=[(24,14),(10,29),(8,62),(26,100),(34,117),(34,96),(55,72),(54,44),(38,30),(25,39),(23,53),(33,64),(42,55),(39,44)]
  for p in a.sample(points,180):mask|=(xx-p.x)**2+(yy-p.y)**2<1.6**2
  for x,y in [(6,13),(57,16),(8,110),(53,111)]:mask|=(xx-x)**2+(yy-y)**2<1.3**2
  pattern=np.tile(mask,(2,16));pattern[128:]=np.roll(pattern[128:],32,axis=1);pattern[11:14]=True;pattern[21:23]=True;pattern[233:235]=True;pattern[242:245]=True
  pix=np.ones((256,1024,4),dtype='f');pix[:,:,:3]=np.where(pattern[:,:,None],np.array([.52,.52,.47]),np.array([.009,.010,.013]));im=bpy.data.images.new(name+' paisley cotton design',width=1024,height=256,alpha=True);im.pixels.foreach_set(pix.ravel());im.pack();tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color']);bs.inputs['Roughness'].default_value=.90;bs.inputs['Specular IOR Level'].default_value=.15;return m
 im=bpy.data.images.new(name+' woven design',width=256,height=256,alpha=True);pix=[]
 for y in range(256):
  for x in range(256):
   u1=x/256;v1=y/256;border=min(v1,1-v1) if bandana else min(u1,1-u1);stripe=.055<border<.065 or .095<border<.103
   pu=(x%32)/32-.5;pv=v1-.5;drop=((pu-.06*sin(pv*6))/.27)**2+(pv/.30)**2;motif=(abs(drop-1)<.14 and pv>-.27) or ((pu+.03)**2+(pv+.06)**2<.008) if bandana else (abs((x%48)-24)/24+abs((y%48)-24)/24<.19)
   base=(.065,.14,.16) if not bandana else (.055,.06,.07);light=(.52,.46,.33) if not bandana else (.64,.64,.59);rgb=light if stripe or motif else base;weave=.98+.02*((x+y)%2)
   pix.extend([*(c*weave for c in rgb),1])
 im.pixels.foreach_set(pix);im.pack();tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color']);return m
def grid(name,fn,nu,nv,mat,thick=.005):
 o=a.grid(name,fn,nu,nv,mat,thick,group='headgear');uv=o.data.uv_layers.new(name='Cloth UV')
 for p in o.data.polygons:
  for li,vi in zip(p.loop_indices,p.vertices):j,i=divmod(vi,nu+1);uv.data[li].uv=(i/nu,j/nv)
 return o
def shaped_hat(style):
 cow=style=='cowboy';mat=a.material('Headwear / '+style+' fabric235',(.075,.12,.17) if not cow else (.24,.15,.075),.65);hem=a.material('Headwear / '+style+' stitch235',(.25,.30,.32) if not cow else (.43,.29,.14),.66)
 def crown(ang,t):
  ph=ang*2*pi;rx=.515-(.135 if cow else .145)*t;ry=.446-(.105 if cow else .125)*t
  soft=.006*sin(ph*3+.4)*sin(pi*t);z=(2.055 if cow else 2.125)+(.39 if cow else .245)*t
  if cow:z-=.032*cos(ph)**2*t**3
  return Vector(((rx+soft)*sin(ph),.015-(ry+soft)*cos(ph),z))
 grid(style+' / sewn tapered crown235',crown,128,36,mat,.009)
 def top(ang,r):
  ph=ang*2*pi;e=crown(ang,1);x=e.x*r;y=.015+(e.y-.015)*r
  if cow:z=2.445-.078*math.exp(-(x/.14)**2)-.020*cos(ph)**2*r**3+.014*sin(ph*2)*r*(1-r)
  else:z=2.37+.014*(1-r*r)+.003*sin(ph*3)*r
  if r>.96:z=z*(1-smooth((r-.96)/.04))+e.z*smooth((r-.96)/.04)
  return Vector((x,y,z))
 grid(style+' / creased top235',top,128,36,mat,.009)
 def brim(ang,t):
  ph=ang*2*pi;rx=.515+(.238 if cow else .158)*t;ry=.446+(.18 if cow else .16)*t
  z=2.055+(.215*sin(ph)**4-.067*cos(ph)**4)*t*t if cow else 2.125-.110*t+.010*sin(ph*3+.4)*t*t
  return Vector((rx*sin(ph),.015-ry*cos(ph),z))
 grid(style+' / curved cloth brim235',brim,160,30,mat,.009)
 for t in ([.94] if cow else [.58,.76,.94]):a.tube(style+' / sewn brim235 '+str(t),[brim(ang,t)+Vector((0,0,.003)) for ang in np.linspace(0,1,161)],.0018,.0014,hem,n=161,sides=6,taper=False,group='headgear')
 for ang in [0,.25,.5,.75]:a.tube(style+' / crown seam235 '+str(ang),[crown(ang,t)+Vector((.002*sin(ang*2*pi),-.002*cos(ang*2*pi),0)) for t in np.linspace(.02,.98,42)],.0015,.0012,hem,n=42,sides=6,taper=False,group='headgear')
 if cow:a.tube('Cowboy / ribbon band235',[crown(ang,.06)+Vector((.003*sin(ang*2*pi),-.003*cos(ang*2*pi),0)) for ang in np.linspace(0,1,129)],.011,.006,a.M['dark'],n=129,sides=10,taper=False,group='headgear')
def bandana():
 if bpy.context.scene.get('build235')=='Feminine':kerchief();return
 mat=textile('Headwear / bandana235',True);hem=a.material('Headwear / bandana hem235',(.20,.21,.22),.85)
 style=bpy.context.scene.get('hairStyle235','');build=bpy.context.scene.get('build235','');clear=.025
 if (build=='Feminine' and style in ['bob','straight','side-sweep','curls','box-braids']) or (build=='Masculine' and style in ['flow','middle-part','locs']):clear=.055
 # Tension determines the smooth cloth outline. Hair is fitted beneath the
 # contact strip; cloth must never trace the individual curls or locs.
 def band(ang,t):
  ph=ang*2*pi;mid=1.06+.24*max(0,-cos(ph));th=mid+.14*(2*t-1);p=a.polar(th,ph,clear+.0025*sin(3*ph+.4)*sin(pi*t));p.z+=.005*sin(2*ph)*sin(pi*t)
  if style=='locs':p.y-=.040*max(0,cos(ph))**3;p.x+=.012*sin(ph)**3
  return p
 grid('Bandana / tensioned folded cotton235',band,160,22,mat,.005)
 for t in [0,1]:a.tube('Bandana / soft folded edge235 '+str(t),[band(ang,t) for ang in np.linspace(0,1,161)],.0016,.0014,hem,n=161,sides=6,taper=False,group='headgear')
 center=band(.5,.5)
 for side in [-1,1]:a.tube('Bandana / crossed cloth knot235 '+str(side),[center+Vector((side*.03,0,.017)),center+Vector((side*.012,.018,-.004)),center+Vector((-side*.025,.008,-.017))],.015,.008,mat,n=28,sides=12,taper=False,group='headgear')
 for side in [-1,1]:
  path=a.sample([center+Vector((side*.01,.014,0)),center+Vector((side*.055,.030,-.05)),center+Vector((side*.08,.018,-.16))],38)
  def tail(w,t):p=path[min(37,int(t*37))].copy();p.x+=(w-.5)*(.035+.030*sin(pi*t))*(1-.75*t*t);p.y+=.007*sin(w*pi*2)*sin(pi*t);p.z+=.012*(w-.5)*t;return p
  grid('Bandana / flared fabric tie235 '+str(side),tail,16,37,mat,.004)

def kerchief():
 mat=textile('Headwear / triangular bandana235',True);hem=a.material('Headwear / folded kerchief edge235',(.035,.038,.045),.86);N=80;verts=[];faces=[];rows=[];uv=[]
 def point(s,t):
  th=.70+.50*abs(s)**1.4;ph=s*pi/2;front=Vector((sin(th)*sin(ph),-sin(th)*cos(ph),cos(th)));rear=Vector((0,sin(1.20),cos(1.20)));d=(front*(1-t)+rear*t).normalized();p=a.C+Vector(((a.R.x+.041)*d.x,(a.R.y+.041)*d.y,(a.R.z+.041)*d.z));p+=d*(.0025*sin(s*4*pi+t*3)*sin(pi*t));return p
 for j in range(N+1):
  count=N-j+1;row=[]
  for i in range(count):
   s=-1+2*i/(count-1) if count>1 else 0;row.append(len(verts));verts.append(tuple(point(s,j/N)));uv.append(((s*(1-j/N)+1)/2,j/N))
  rows.append(row)
 for j in range(N):
  row,nxt=rows[j],rows[j+1]
  for i in range(len(nxt)):
   faces.append((row[i],row[i+1],nxt[i]))
   if i+1<len(nxt):faces.append((row[i+1],nxt[i+1],nxt[i]))
 o=a.mesh('Bandana / feminine triangular crown scarf235',verts,faces,mat,'headgear');layer=o.data.uv_layers.new(name='Unfolded triangular cloth UV')
 for poly in o.data.polygons:
  for li,vi in zip(poly.loop_indices,poly.vertices):layer.data[li].uv=uv[vi]
 mod=o.modifiers.new('Folded cotton thickness235','SOLIDIFY');mod.thickness=.004;mod.offset=-1
 a.tube('Bandana / folded front edge235',[point(s,0) for s in np.linspace(-1,1,121)],.0024,.0020,hem,n=121,sides=8,taper=False,group='headgear')
 center=point(0,1)+Vector((0,.012,0))
 for side in [-1,1]:
  a.tube('Bandana / kerchief knot235 '+str(side),[center+Vector((side*.027,0,.016)),center+Vector((side*.01,.017,0)),center+Vector((-side*.024,.007,-.016))],.015,.009,mat,n=28,sides=10,taper=False,group='headgear')
  path=a.sample([center+Vector((side*.012,.015,0)),center+Vector((side*.06,.034,-.045)),center+Vector((side*.08,.023,-.15))],40)
  def tie(w,t):p=path[min(39,int(t*39))].copy();p.x+=(w-.5)*(.04+.025*sin(pi*t))*(1-.8*t*t);p.y+=.006*sin(w*2*pi)*sin(pi*t);return p
  grid('Bandana / kerchief tie235 '+str(side),tie,14,39,mat,.004)
def build(style,build):
 a.setup();a.GROUP='headgear';remove(['headgear'])
 if style=='none':return
 if style in ['bucket','cowboy']:shaped_hat(style)
 elif style=='headband':bandana()
 elif style=='pashmina':
  final=P/'components'/f'{build}-pashmina-headgear.glb'
  if not final.exists():raise FileNotFoundError('Build/review scarf_knot235.py, then promote the final pashmina component')
  imported(final,'headgear')
 elif style=='cap':library(P.parent/'refinement224/scenes'/('Feminine-cap.blend' if build=='Feminine' else 'Masculine-details.blend'),['headgear'])
 else:library(P.parent/'catalogue226/revision227/sources'/f'Feminine-{style}.blend',['headgear'])
