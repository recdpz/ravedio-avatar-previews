from common235 import *
from math import sin
def clear_material():
 m=a.material('Glasses / clear non-refracting pane235',(.82,.91,.94),.025);bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Transmission Weight'].default_value=0;bs.inputs['IOR'].default_value=1.;bs.inputs['Alpha'].default_value=.075;bs.inputs['Coat Weight'].default_value=.14;bs.inputs['Specular IOR Level'].default_value=.25;m.surface_render_method='DITHERED';return m
def thin_lenses(obs):
 m=clear_material()
 for o in obs:
  if o.type!='MESH':continue
  # Retain one face-facing pane; discard back, perimeter and obsolete thickness.
  mat=o.matrix_world.to_3x3();keep=[]
  for poly in o.data.polygons:
   normal=mat@poly.normal
   if normal.y<-.45:keep.append(tuple(poly.vertices))
  if not keep:
   for poly in o.data.polygons:
    normal=mat@poly.normal
    if normal.y>.45:keep.append(tuple(reversed(poly.vertices)))
  assert keep,o.name
  verts=[tuple(v.co) for v in o.data.vertices];me=bpy.data.meshes.new('Thin clear pane235');me.from_pydata(verts,[],keep);me.update();o.data=me;o.data.materials.append(m)
  for p in me.polygons:p.use_smooth=False
  o.modifiers.clear()
def sprout():
 a.setup();a.GROUP='extra';remove(['extra']);support=tree([o for o in bpy.context.scene.objects if o.type=='MESH' and o.get('component159') in ['hair','headgear']]);hit,normal,_,_=support.ray_cast(Vector((.13,.02,3.1)),Vector((0,0,-1)),2)
 assert hit is not None,'Sprout clip has no support';N=normal.normalized()
 if N.z<0:N=-N
 X=Vector((1,0,0));X=(X-N*X.dot(N)).normalized();Y=N.cross(X);anchor=hit+N*.003;metal=a.material('Sprout / clip silver235',(.46,.49,.52),.28,.78)
 def point(x,y,z):return anchor+X*x+Y*y+N*z
 for j,z in enumerate([.003,.014]):
  # Rounded flattened jaws, joined at the rear hinge.
  o=a.sphere('Sprout / alligator clip jaw235 '+str(j),point(0,0,z),(.052,.018,.0045),metal,'extra');o.rotation_euler=N.to_track_quat('Z','Y').to_euler()
 a.tube('Sprout / clip hinge235',[point(-.037,-.018,.007),point(-.037,.018,.007)],.007,.007,metal,n=8,sides=12,taper=False,group='extra')
 for j in range(7):
  x=-.02+j*.01;a.tube('Sprout / clamp tooth235 '+str(j),[point(x,-.012,.006),point(x,-.012,.012)],.002,.002,metal,n=3,sides=5,taper=False,group='extra')
 a.tube('Sprout / rooted stem235',[point(0,0,.015),point(.006,0,.07),point(-.006,0,.112)],.007,.006,a.M['mint'],n=30,sides=10,taper=False,group='extra')
 for side in [-1,1]:
  def leaf(w,t):
   return point(-.006+side*.135*t,(w-.5)*.090*sin(math.pi*t),.103+.028*sin(math.pi*t)-.012*t+(w-.5)*.065*sin(math.pi*t))
  a.grid('Sprout / curved leaf235 '+str(side),leaf,14,25,a.M['mint'],.004,group='extra')
  a.tube('Sprout / leaf midrib235 '+str(side),[leaf(.5,t)+N*.002 for t in np.linspace(0,1,30)],.0015,.0012,a.material('Sprout / leaf vein235',(.08,.29,.16),.47),n=30,sides=5,taper=False,group='extra')
 return dict(anchor=list(anchor),surface=list(hit),clearance=.003,has_clip=True)
def lenses_main():
 records={}
 for style,item in CAT['glasses'].items():
  if style=='none':continue
  builds=['Feminine','Masculine'] if style=='rectangular' else ['Feminine']
  for build in builds:
   s=load(build);remove(['hair']);frames=CAT['builds'][build]['rectangular']['glasses'] if style=='rectangular' else item['path'];lenses=CAT['builds'][build]['rectangular']['lenses'] if style=='rectangular' else item['lenses'];imported((R/'234'/frames).resolve(),'glasses');obs=imported((R/'234'/lenses).resolve(),'lenses');thin_lenses(obs);key=build+'-'+style;parts=save(s,key,['lenses']);records[key]=parts;render(bpy.context.scene,key,['front','profile'],size=256)
 u.dump(P/'lenses235.json',records)
