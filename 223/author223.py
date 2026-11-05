import bpy,sys,math,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).parent;sys.path.insert(0,str(P));import parameters222 as pa;import export222 as ex

def sig(s):
 out={}
 for o in s.objects:
  if o.type!='MESH' or o.get('capDesign'):continue
  h=hashlib.sha256();h.update(np.array([v.co[:] for v in o.data.vertices],dtype='f').tobytes());h.update(str([(p.vertices[:],p.material_index) for p in o.data.polygons]).encode());h.update(str([m.name if m else None for m in o.data.materials]).encode());out[o.name]=h.hexdigest()
 return out

def render(s,path,angle,size=384):
 target=Vector((0,0,1.88));d={'front':(0,-8,0),'threequarter':(-4,-8,0),'profile':(-8,0,0),'rightprofile':(8,0,0),'rear':(0,8,0),'top':(0,-4,8)}[angle];s.camera.location=target+Vector(d);s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=1.5;s.render.resolution_x=s.render.resolution_y=size;s.render.resolution_percentage=100;s.cycles.samples=40 if size<512 else 64;s.render.filepath=str(path);s.render.image_settings.file_format='PNG';bpy.ops.render.render(write_still=True)

def add_logo(s):
 for o in list(s.objects):
  if o.get('capDesign'):bpy.data.objects.remove(o,do_unlink=True)
 crown=s.objects['Cap / sewn crown and curved bill212'];raw=[v.co[:] for v in crown.data.shape_keys.key_blocks['CapOriginal'].data];tree=BVHTree.FromPolygons(raw,[p.vertices[:] for p in crown.data.polygons])
 mat=bpy.data.materials.new('Cap / ivory emblem223');mat.diffuse_color=(.78,.83,.81,1);mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.78,.83,.81,1);bs.inputs['Roughness'].default_value=.52
 routes={'orbit':[], 'pulse':[]}
 # Original split orbit with a small central diamond; no letters or brand tracing.
 for start,end in [(18,164),(198,344)]:
  pts=[]
  for a in np.linspace(math.radians(start),math.radians(end),44):
   x=.071*math.cos(a);z=.047*math.sin(a);r=.36;pts.append((x*math.cos(r)-z*math.sin(r),x*math.sin(r)+z*math.cos(r)))
  routes['orbit'].append((pts,False,.0038))
 routes['orbit'].append(([(0,.019),(.014,0),(0,-.019),(-.014,0)],True,.0034))
 routes['pulse']=[([(-.060,-.023),(-.032,-.023),(-.012,.032),(.014,-.030),(.034,.023),(.060,.023)],False,.0052)]
 for design,strokes in routes.items():
  for j,(points,closed,width) in enumerate(strokes):
   cv=bpy.data.curves.new('Cap emblem223','CURVE');cv.dimensions='3D';cv.bevel_depth=width;cv.bevel_resolution=3;cv.resolution_u=1;cv.use_fill_caps=True;sp=cv.splines.new('POLY');sp.points.add(len(points)-1)
   for q,(x,z) in zip(sp.points,points):q.co=(x,0,2.225+z,1)
   sp.use_cyclic_u=closed;o=bpy.data.objects.new('Cap / '+design+' emblem223 '+str(j),cv);s.collection.objects.link(o);o.data.materials.append(mat);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o=bpy.context.object;o.select_set(False)
   original=[]
   for v in o.data.vertices:
    hit,no,_,_=tree.ray_cast(Vector((v.co.x,-1,v.co.z)),Vector((0,1,0)));assert hit is not None;original.append(np.array(hit)+np.array(no)*(.0035-v.co.y))
   o['component159']='headgear';o['param214']='cap';o['capDesign']=design;o['graphic223']=True;o.shape_key_add(name='Basis');key=o.shape_key_add(name='CapOriginal');key.value=0
   for v,kv,co in zip(o.data.vertices,key.data,original):v.co=pa.cap_vertex(co,pa.CAP['default']);kv.co=co
   o.data.shape_keys.key_blocks['Basis'].data.foreach_set('co',np.array([v.co[:] for v in o.data.vertices],dtype='f').ravel());o.hide_render=design!='orbit'
   for p in o.data.polygons:p.use_smooth=True

def main():
 cases={'Feminine-ponytail-cap':P.parent/'refinement222/scenes/Feminine-ponytail-cap.blend','Feminine-cap':P.parent/'refinement214/scenes/Feminine-cap.blend','Masculine-cap':P.parent/'refinement214/scenes/Masculine-cap.blend'};report={};final='--final' in sys.argv
 for name,src in cases.items():
  bpy.ops.wm.open_mainfile(filepath=str(P/'scenes'/(name+'.blend') if final else src));s=bpy.context.scene
  if not final:
   before=sig(s);add_logo(s);assert before==sig(s),'Protected geometry changed';s.name='223 '+name;bpy.ops.file.pack_all();dst=P/'scenes'/(name+'.blend');bpy.ops.wm.save_as_mainfile(filepath=str(dst),compress=True);bpy.ops.wm.open_mainfile(filepath=str(dst));s=bpy.context.scene;assert before==sig(s);ex.export(s,P/'components'/(name+'.glb'),'headgear');report[name]={'source':str(src),'protected_meshes_exact':len(before),'saved_reopened':True,'scene_sha256':hashlib.sha256(dst.read_bytes()).hexdigest()}
  if name=='Feminine-ponytail-cap':
   choices=json.loads((P/'owner-choices222.json').read_text());choices['cap']['design']='orbit';pa.apply(s,choices)
  for design in ['orbit','pulse']:
   for o in s.objects:
    if o.get('capDesign'):o.hide_render=o['capDesign']!=design
   for angle in (['front','threequarter','profile','rightprofile','rear','top'] if final else ['front','threequarter','profile']):render(s,P/('review2' if final else 'review1')/(name+'-'+design+'-'+angle+'.png'),angle,512 if final else 384)
 if final:
  skins=[[.8713671191987972,.6038273388553378,.4793201831008268],[.8148465722161012,.6239603916950761,.3419144249086609],[.5149176653765214,.3049873140698863,.18782077230067787],[.21586050011389926,.10461648409110419,.07421356838014963]]
  bpy.ops.wm.open_mainfile(filepath=str(P/'scenes/Feminine-ponytail-cap.blend'));s=bpy.context.scene
  for tone in range(4):
   for ob in s.objects:
    if ob.type not in ['MESH','CURVE']:continue
    for mat in ob.data.materials:
     if mat and mat.use_nodes and mat.name.startswith('Skin'):mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*skins[tone],1)
   for size in [32,48,64,128,512]:render(s,P/'review2'/('tone'+str(tone)+'-'+str(size)+'.png'),'front',size)
 if not final:(P/'audit223.json').write_text(json.dumps(report,indent=2))
 print('AUTHOR223 COMPLETE',final,flush=True)
if __name__=='__main__':main()
