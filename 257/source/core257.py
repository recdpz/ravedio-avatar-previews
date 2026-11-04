"""B silhouette,214-style smooth vertex fade and restrained sculpted direction."""
import sys,json,math,struct,shutil,hashlib
from pathlib import Path
sys.path.insert(0,'E:/Ravedio-Avatar/recovery255')
from recover255 import *
import numpy as np
P=Path('E:/Ravedio-Avatar/catalogue257');W=P/'pass3'
for d in [W/'sources',W/'components',W/'renders']:d.mkdir(parents=True,exist_ok=True)
CFG=dict(fade_span=.38,side_lift=.012,mark_rows=14,mark_columns=112,tip_start=.70,tip_alpha_start=.76,tip_thinning=.55,mark_length_base=.025,mark_length_density=.11,mark_width_base=.0007,mark_width_density=.0014,mark_alpha=.36,mark_relief=.00055)

def vertex_alpha(ob,values):
 for x in list(ob.data.color_attributes):ob.data.color_attributes.remove(x)
 co=ob.data.color_attributes.new(name='Hair257 opacity',type='FLOAT_COLOR',domain='POINT');co.data.foreach_set('color',np.asarray(values,dtype='f').ravel());ob.data.color_attributes.active_color=co;ob.data.color_attributes.render_color_index=0

def alpha_material(name,base=(.12,.047,.026),rough=.44):
 m=a.material(name,base,rough);bs=m.node_tree.nodes['Principled BSDF'];bs.inputs['Specular IOR Level'].default_value=.30;bs.inputs['Coat Weight'].default_value=.035
 attr=m.node_tree.nodes.new('ShaderNodeVertexColor');attr.layer_name='Hair257 opacity';m.node_tree.links.new(attr.outputs['Alpha'],bs.inputs['Alpha']);return m

def coords257(theta,phi):
 end=old.boundary(phi,False);t=max(0,min(1,(theta-.003)/end));density=smooth((1-t)/CFG['fade_span']);lift=.0025+CFG['side_lift']*density**1.25+.0006*math.cos(phi*122+theta*4)*density*smooth(t/.15)*smooth((1-t)/.06)
 return c.sp(theta,phi,lift),density

def sides257():
 material=alpha_material('Hair257 / smooth side fade');nu,nv=384,112;vv=[];ff=[];rgba=[]
 for j in range(nv+1):
  for i in range(nu):
   phi=i/nu*2*PI;theta=.003+(j/nv)*old.boundary(phi,False);p,density=coords257(theta,phi);vv.append(tuple(p));rgba.append((1,1,1,density))
 for j in range(nv):
  for i in range(nu):x=j*nu+i;y=j*nu+(i+1)%nu;ff.append((x,y,y+nu,x+nu))
 ff.append(tuple(range(nu-1,-1,-1)));ob=a.mesh('Hair257 / smooth fitted sides',vv,ff,material,'hair');vertex_alpha(ob,rgba)
 # Short flattened sculpt marks lie on the fade, grow shorter/fainter toward skin,
 # and stay out of the forehead. They are coherent strokes, not scattered dots.
 vv=[];ff=[];rgba=[];count=0
 for row in range(CFG['mark_rows']):
  for col in range(CFG['mark_columns']):
   phi=(col+.44*(row%2))/CFG['mark_columns']*2*PI;theta=.88+row*.074+.012*math.sin(col*.91+row*.7)
   if abs((phi+PI)%(2*PI)-PI)<.94:continue
   p,density=coords257(theta,phi)
   if theta>old.boundary(phi,False)-.025 or density<.035:continue
   length=CFG['mark_length_base']+CFG['mark_length_density']*density**1.3;width=CFG['mark_width_base']+CFG['mark_width_density']*density;offset=len(vv)
   for k in range(5):
    t=k/4;ang=theta+(t-.5)*length;flow=phi+.012*math.cos(phi)*(t-.5);center,dd=coords257(ang,flow);N=(center-a.C).normalized();tangent=Vector((math.cos(flow),math.sin(flow),0));tangent=(tangent-N*tangent.dot(N)).normalized();half=width*(.30+.70*math.sin(PI*t)**.65)
    for side in [-1,0,1]:
     point=center+tangent*(side*half)+N*(.00015+(CFG['mark_relief'] if side==0 else 0)*math.sin(PI*t));vv.append(tuple(point));rgba.append((1,1,1,CFG['mark_alpha']*density*smooth(t/.20)*smooth((1-t)/.20)))
   for k in range(4):
    for side in range(2):i=offset+k*3+side;ff.append((i,i+1,i+4,i+3))
   count+=1
 ob=a.mesh('Hair257 / short sculpted direction',vv,ff,alpha_material('Hair257 / directional fade marks'),'hair');vertex_alpha(ob,rgba);return count

def blend_tips257(s):
 report=[]
 for ob in [o for o in s.objects if o.type=='MESH' and o.get('component159')=='hair' and len(o.data.vertices)==2530]:
  original=[(ob.matrix_world@v.co).copy() for v in ob.data.vertices];centers=[original[0]]+[sum(original[1+i*32:1+(i+1)*32],Vector())/32 for i in range(79)]+[original[-1]];inv=ob.matrix_world.inverted();rgba=[];changed=0
  for i,v in enumerate(ob.data.vertices):
   row=0 if i==0 else 80 if i==2529 else (i-1)//32+1;t=row/80;center=centers[row];dv=center-a.C;q=Vector((dv.x/.48,dv.y/.405,dv.z/.455));theta=math.acos(max(-1,min(1,q.normalized().z)));phi=math.atan2(q.x,-q.y);covered=smooth((old.boundary(phi,False)-theta-.012)/.09);weight=smooth((t-CFG['tip_start'])/(1-CFG['tip_start']))*covered
   if weight>0:
    N=dv.normalized();hit,_,_,dist=c.HEAD.ray_cast(a.C,N,2);dep=max(.003,dv.length-dist);newcenter=center-N*max(0,dep-.009)*weight*.55;v.co=inv@(newcenter+(original[i]-center)*(1-CFG['tip_thinning']*weight));changed+=1
   else:assert tuple(ob.matrix_world@v.co)==tuple(original[i])
   opacity=1-covered*smooth((t-CFG['tip_alpha_start'])/(1-CFG['tip_alpha_start']));rgba.append((1,1,1,opacity))
  vertex_alpha(ob,rgba)
  originals=list(ob.data.materials);blended={}
  for index,base in enumerate(originals):
   name='Hair257 / blended terminal tips '+base.name
   material=bpy.data.materials.get(name)
   if material is None:
    material=base.copy();material.name=name;attr=material.node_tree.nodes.new('ShaderNodeVertexColor');attr.layer_name='Hair257 opacity';material.node_tree.links.new(attr.outputs['Alpha'],material.node_tree.nodes['Principled BSDF'].inputs['Alpha'])
   ob.data.materials.append(material);blended[index]=len(ob.data.materials)-1
  for face in ob.data.polygons:
   if min(rgba[i][3] for i in face.vertices)<.999999:face.material_index=blended[face.material_index]
  report.append(dict(name=ob.name,vertices_changed=changed,upper_shape_preserved=True,changes_restricted_to_terminal_fraction=.30))
 return report

def patch257(path,s=None):
 r=path.read_bytes();n=struct.unpack_from('<I',r,12)[0];g=json.loads(r[20:20+n]);binary=bytearray(r[28+n:]);expected={}
 if s:
  for ob in s.objects:
   if ob.type!='MESH' or ob.get('component159')!='hair' or not ob.data.color_attributes:continue
   col=ob.data.color_attributes[0]
   if col.domain!='POINT':continue
   for m in ob.data.materials:
    table=expected.setdefault(m.name,{})
    for v,cc in zip(ob.data.vertices,col.data):
     p=ob.matrix_world@v.co;table[tuple(round(x,5) for x in (p.x,p.z,-p.y))]=list(cc.color)
 for mesh in g.get('meshes',[]):
  for pr in mesh['primitives']:
   m=g['materials'][pr['material']];name=m.get('name','')
   if not name.startswith('Hair257 /'):continue
   m['alphaMode']='BLEND';m['doubleSided']=False;m.setdefault('pbrMetallicRoughness',{})['baseColorFactor']=list(bpy.data.materials[name].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value) if s and name in bpy.data.materials else m.get('pbrMetallicRoughness',{}).get('baseColorFactor',[.12,.047,.026,1])
   if name not in expected:continue
   accessor=g['accessors'][pr['attributes']['POSITION']];view=g['bufferViews'][accessor['bufferView']];pts=np.ndarray((accessor['count'],3),dtype='<f4',buffer=binary,offset=view.get('byteOffset',0)+accessor.get('byteOffset',0),strides=(view.get('byteStride',12),4)).copy();table=expected[name];colors=np.asarray([table[tuple(round(float(x),5) for x in point)] for point in pts],dtype='<f4');binary.extend(b'\0'*((-len(binary))%4));off=len(binary);binary.extend(colors.tobytes());vi=len(g['bufferViews']);g['bufferViews'].append(dict(buffer=0,byteOffset=off,byteLength=colors.nbytes,target=34962));ai=len(g['accessors']);g['accessors'].append(dict(bufferView=vi,componentType=5126,count=len(colors),type='VEC4'));pr['attributes']['COLOR_0']=ai
 g['buffers'][0]['byteLength']=len(binary);js=json.dumps(g,separators=(',',':')).encode();js+=b' '*((-len(js))%4);path.write_bytes(struct.pack('<III',0x46546c67,2,28+len(js)+len(binary))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(binary),0x004e4942)+binary)

def build(style):
 src=P.parent/'catalogue256/pass2/sources'/f'Masculine-{style}-hair256.blend';bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;frozen=protect(s);a.setup();c.reset_head(s)
 for ob in list(s.objects):
  if ob.get('component159')=='hair' and 'Hair256 /' in ob.name:u.delete(ob)
 tips=blend_tips257(s) if style=='taper' else [];marks=sides257();check(s,frozen);u.bake(s);source=W/'sources'/f'Masculine-{style}-hair257.blend';target=W/'components'/f'Masculine-{style}-hair257.glb';assert not source.exists() and not target.exists();bpy.ops.outliner.orphans_purge(do_recursive=True);bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True);ex.export(s,target,'hair');patch257(target,s);c.gpu()
 for angle in ['front','threequarter','profile','rightprofile','rear','rearquarter','top','underside']:
  u.camera(s,'rear' if angle=='rearquarter' else angle,512,False)
  if angle=='rearquarter':
   camera_target=Vector((0,0,1.88));s.camera.location=camera_target+Vector((-4,8,0));s.camera.rotation_euler=(camera_target-s.camera.location).to_track_quat('-Z','Y').to_euler()
  s.camera.data.ortho_scale=1.65;s.cycles.samples=24;s.render.filepath=str(W/'renders'/f'{style}-{angle}.png');floor=s.objects.get('Studio floor');hidden=floor.hide_render if floor else False
  if floor and angle=='underside':floor.hide_render=True
  try:bpy.ops.render.render(write_still=True)
  finally:
   if floor:floor.hide_render=hidden
 return dict(path=str(target),source=str(source),tips=tips,marks=marks,fade_span=.38,shape='B upper locks preserved; only terminal tips thinned and blended',side='Smooth vertex alpha and small sculpted directional marks; no grain coverage atlas',other_geometry_preserved=True)

if __name__=='__main__':
 out={}
 for style in ['taper','curly-top']:out[style]=build(style);(W/'hair257.json').write_text(json.dumps(out,indent=2)+'\n')
 shutil.copy2(__file__,W/'core257.py');(W/'settings.json').write_text(json.dumps(CFG,indent=2)+'\n');print('CORE257_COMPLETE2',flush=True)
