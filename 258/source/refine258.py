"""Lower combed Taper, relaxed diagonal Side part, clearer low-glare fade detail."""
import sys,json,math,struct,shutil,hashlib
from pathlib import Path
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue257')
import core257 as prev
from core257 import *
import numpy as np
from mathutils import Matrix,Vector
P=Path('E:/Ravedio-Avatar/catalogue258');W=P/'pass2';R=P.parent/'floating138/mobile-preview'
for d in [W/'sources',W/'components',W/'renders']:d.mkdir(parents=True,exist_ok=True)
CFG=dict(prev.CFG,side_lift=.008,mark_columns=88,mark_width_base=.0008,mark_width_density=.0018,mark_alpha=.46,mark_relief=.00040,mark_shade=.88,tip_alpha_start=.86)
prev.CFG=CFG

def coords258(theta,phi):
 end=old.boundary(phi,False);t=max(0,min(1,(theta-.003)/end));density=smooth((1-t)/CFG['fade_span'])
 return c.sp(theta,phi,.0025+CFG['side_lift']*density),density
prev.coords257=coords258

def sides258():
 before=set(bpy.context.scene.objects);count=prev.sides257()
 for ob in set(bpy.context.scene.objects)-before:
  ob.name=ob.name.replace('257','258')
  for m in ob.data.materials:
   m.name=m.name.replace('257','258');bs=m.node_tree.nodes['Principled BSDF'];bs.inputs['Roughness'].default_value=.56;bs.inputs['Specular IOR Level'].default_value=.18;bs.inputs['Coat Weight'].default_value=0
   if 'directional' in m.name:
    m['hairShade258']=CFG['mark_shade'];col=(.12,.047,.026);bs.inputs['Base Color'].default_value=(*[v*CFG['mark_shade'] for v in col],1)
 return count


def contract_nape(s):
 out=[]
 for ob in [o for o in s.objects if o.type=='MESH' and o.get('component159')=='hair' and 'Side part nape' in o.name and len(o.data.vertices)==2530]:
  j=int(ob.name.split('Side part nape ')[1].split('.')[0]);pts=[(ob.matrix_world@v.co).copy() for v in ob.data.vertices];centers=[pts[0]]+[sum(pts[1+i*32:1+(i+1)*32],Vector())/32 for i in range(79)]+[pts[-1]];height=2.055+.006*math.sin(j*.9);end=next(i for i in range(25,81) if centers[i].z<height);f=(centers[end-1].z-height)/max(1e-6,centers[end-1].z-centers[end].z);endparam=(end-1+f)/80;new=[]
  for row in range(81):
   u=row*endparam;k=min(79,int(u));new.append(centers[k].lerp(centers[k+1],u-k))
  inv=ob.matrix_world.inverted()
  for i,v in enumerate(ob.data.vertices):
   row=0 if i==0 else 80 if i==2529 else (i-1)//32+1;lo=max(0,row-1);hi=min(80,row+1);rotation=(centers[hi]-centers[lo]).rotation_difference(new[hi]-new[lo]);v.co=inv@(new[row]+rotation@(pts[i]-centers[row]))
  out.append(dict(name=ob.name,length_fraction=endparam,rounded_original_cross_sections_preserved=True))
 return out

def mirror_sweep(s):
 import bmesh
 for ob in [o for o in s.objects if o.type=='MESH' and o.get('component159')=='hair']:
  inv=ob.matrix_world.inverted()
  for v in ob.data.vertices:
   p=ob.matrix_world@v.co;p.x=2*a.C.x-p.x;v.co=inv@p
  bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()

def hair_uv(ob):
 if len(ob.data.vertices)!=2530:return
 for layer in list(ob.data.uv_layers):ob.data.uv_layers.remove(layer)
 uv=ob.data.uv_layers.new(name='Authored hair flow258')
 for face in ob.data.polygons:
  seam=any(i not in [0,2529] and (i-1)%32>28 for i in face.vertices)
  for li,i in zip(face.loop_indices,face.vertices):
   row=0 if i==0 else 80 if i==2529 else (i-1)//32+1;col=0 if i in [0,2529] else (i-1)%32;uv.data[li].uv=(1 if seam and col==0 else col/32,1-row/80)

def style_sidepart(s,relaxed):
 mats={};changed=[]
 for ob in [o for o in s.objects if o.type=='MESH' and o.get('component159')=='hair']:
  hair_uv(ob)
  for slot in ob.material_slots:
   base=slot.material
   if base.name not in mats:
    m=base.copy();m.name='Hair258 / sculpted side sweep '+str(len(mats));old.normal_texture(m,'long');bs=m.node_tree.nodes['Principled BSDF'];bs.inputs['Roughness'].default_value=.36;bs.inputs['Coat Weight'].default_value=.06
    for node in m.node_tree.nodes:
     if node.type=='NORMAL_MAP':node.inputs['Strength'].default_value=.12
    mats[base.name]=m
   slot.material=mats[base.name]
  if not relaxed or 'Side part main' not in ob.name or len(ob.data.vertices)!=2530:continue
  j=int(ob.name.split('Side part main ')[1].split('.')[0]);pts=[(ob.matrix_world@v.co).copy() for v in ob.data.vertices];centers=[pts[0]]+[sum(pts[1+i*32:1+(i+1)*32],Vector())/32 for i in range(79)]+[pts[-1]];new=[]
  for row,center in enumerate(centers):
   t=row/80;envelope=math.sin(PI*t)**2;angle=-.22*envelope*(1-.055*j);rotation=Matrix.Rotation(angle,3,'Z');p=a.C+rotation@(center-a.C);p+=Vector((-.010*envelope*math.sin(j*.8),-.048*envelope*(1-j*.12),.012*envelope*math.sin(2*PI*t+j*.55)-.016*envelope*max(0,1-j*.45)));new.append(p)
  inv=ob.matrix_world.inverted()
  for i,v in enumerate(ob.data.vertices):
   row=0 if i==0 else 80 if i==2529 else (i-1)//32+1;lo=max(0,row-1);hi=min(80,row+1);before=centers[hi]-centers[lo];after=new[hi]-new[lo];rotation=before.rotation_difference(after);v.co=inv@(new[row]+rotation@(pts[i]-centers[row]))
  changed.append(ob.name)
 return changed

def tips258(s):
 report=[]
 for ob in [o for o in s.objects if o.type=='MESH' and o.get('component159')=='hair' and len(o.data.vertices)==2530]:
  rgba=[];points=[ob.matrix_world@v.co for v in ob.data.vertices];centers=[points[0]]+[sum(points[1+i*32:1+(i+1)*32],Vector())/32 for i in range(79)]+[points[-1]]
  for i,v in enumerate(ob.data.vertices):
   row=0 if i==0 else 80 if i==2529 else (i-1)//32+1;t=row/80;dv=centers[row]-a.C;q=Vector((dv.x/.48,dv.y/.405,dv.z/.455));theta=math.acos(max(-1,min(1,q.normalized().z)));phi=math.atan2(q.x,-q.y);covered=smooth((old.boundary(phi,False)-theta-.012)/.09);opacity=1-covered*smooth((t-CFG['tip_alpha_start'])/(1-CFG['tip_alpha_start']));rgba.append((1,1,1,opacity))
  vertex_alpha(ob,rgba);originals=list(ob.data.materials);blended={}
  for index,base in enumerate(originals):
   name='Hair258 / blended terminal tips '+base.name;material=bpy.data.materials.get(name)
   if material is None:
    material=base.copy();material.name=name;attr=material.node_tree.nodes.new('ShaderNodeVertexColor');attr.layer_name='Hair257 opacity';material.node_tree.links.new(attr.outputs['Alpha'],material.node_tree.nodes['Principled BSDF'].inputs['Alpha'])
   ob.data.materials.append(material);blended[index]=len(ob.data.materials)-1
  for face in ob.data.polygons:
   if min(rgba[i][3] for i in face.vertices)<.999999:face.material_index=blended[face.material_index]
  report.append(dict(name=ob.name,geometry_undeformed=True,alpha_start=CFG['tip_alpha_start']))
 return report

def patch258(path,s):
 # Standard COLOR_0 carries opacity; only explicit tip/fade materials blend.
 r=path.read_bytes();n=struct.unpack_from('<I',r,12)[0];g=json.loads(r[20:20+n]);binary=bytearray(r[28+n:]);expected={}
 for ob in s.objects:
  if ob.type!='MESH' or ob.get('component159')!='hair' or not ob.data.color_attributes:continue
  col=ob.data.color_attributes[0]
  if col.domain!='POINT':continue
  for m in ob.data.materials:
   table=expected.setdefault(m.name,{})
   for v,cc in zip(ob.data.vertices,col.data):
    p=ob.matrix_world@v.co;table[tuple(round(x,5) for x in (p.x,p.z,-p.y))]=list(cc.color)
 for mesh in g['meshes']:
  for pr in mesh['primitives']:
   m=g['materials'][pr['material']];name=m.get('name','');fade=any(k in name for k in ['blended terminal','smooth side fade','directional fade']);m['alphaMode']='BLEND' if fade else 'OPAQUE';m['doubleSided']=not fade;source=bpy.data.materials.get(name)
   if source:
    m.setdefault('pbrMetallicRoughness',{})['baseColorFactor']=list(source.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value)
    if source.get('hairShade258') is not None:m.setdefault('extras',{})['hairShade258']=source['hairShade258']
   if not fade or name not in expected:continue
   a0=g['accessors'][pr['attributes']['POSITION']];v0=g['bufferViews'][a0['bufferView']];points=np.ndarray((a0['count'],3),dtype='<f4',buffer=binary,offset=v0.get('byteOffset',0)+a0.get('byteOffset',0),strides=(v0.get('byteStride',12),4)).copy();colors=np.asarray([expected[name][tuple(round(float(x),5) for x in point)] for point in points],dtype='<f4');binary.extend(b'\0'*((-len(binary))%4));off=len(binary);binary.extend(colors.tobytes());vi=len(g['bufferViews']);g['bufferViews'].append(dict(buffer=0,byteOffset=off,byteLength=colors.nbytes,target=34962));ai=len(g['accessors']);g['accessors'].append(dict(bufferView=vi,componentType=5126,count=len(colors),type='VEC4'));pr['attributes']['COLOR_0']=ai
 g['buffers'][0]['byteLength']=len(binary);js=json.dumps(g,separators=(',',':')).encode();js+=b' '*((-len(js))%4);path.write_bytes(struct.pack('<III',0x46546c67,2,28+len(js)+len(binary))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(binary),0x004e4942)+binary)

def build(style):
 source=P.parent/'catalogue257/pass3/sources'/f'Masculine-{"curly-top" if style=="curly-top" else "taper"}-hair257.blend';bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;frozen=protect(s);a.setup();c.reset_head(s)
 for ob in list(s.objects):
  if ob.get('component159')=='hair' and (style!='curly-top' or 'Hair257 /' in ob.name):u.delete(ob)
 changed=[]
 if style!='curly-top':
  imported(R/'208/Masculine-hair.glb','hair')
  if style=='taper':
   for ob in list(s.objects):
    if ob.get('component159')=='hair' and not any(k in ob.name for k in ['Side part main','Side part short','Side part crown','Side part nape']):u.delete(ob)
  changed=style_sidepart(s,style=='sidepart')
  if style=='taper':changed+=contract_nape(s)
  else:mirror_sweep(s)
 tips=tips258(s) if style=='taper' else [];marks=sides258() if style!='sidepart' else 0;check(s,frozen);u.bake(s);src=W/'sources'/f'Masculine-{style}-hair258.blend';target=W/'components'/f'Masculine-{style}-hair258.glb';assert not src.exists() and not target.exists();bpy.ops.outliner.orphans_purge(do_recursive=True);bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(src),compress=True);ex.export(s,target,'hair');patch258(target,s);c.gpu()
 for angle in ['front','threequarter','profile','rightprofile','rear','top']:
  u.camera(s,angle,512,False);s.camera.data.ortho_scale=1.65;s.cycles.samples=24;s.render.filepath=str(W/'renders'/f'{style}-{angle}.png');bpy.ops.render.render(write_still=True)
 return dict(path=str(target),source=str(src),changed_banks=changed,tips=tips,marks=marks,other_geometry_preserved=True,taper_basis='Clean current Side part top; no257 radius shrink',fade='Smooth un-rippled field, low-glare short strokes' if marks else 'Retained full sides')

if __name__=='__main__':
 out=json.loads((W/'hair258.json').read_text()) if (W/'hair258.json').exists() else {}
 for style in ['taper','sidepart','curly-top']:
  if style in out:continue
  out[style]=build(style);(W/'hair258.json').write_text(json.dumps(out,indent=2)+'\n')
 shutil.copy2(__file__,W/'refine258.py');(W/'settings.json').write_text(json.dumps(CFG,indent=2)+'\n');print('REFINE258_COMPLETE3',flush=True)
