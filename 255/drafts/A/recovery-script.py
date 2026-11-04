import sys,json,math,struct,shutil,hashlib
from pathlib import Path
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue252')
from common252 import *
import hair252 as old
P=Path('E:/Ravedio-Avatar/recovery255');PI=math.pi

def restore_long(s,cfg):
 count=0
 for ob in [o for o in s.objects if o.type=='MESH' and o.get('component159')=='hair']:
  n=len(ob.data.vertices)
  if n!=2530:continue
  inv=ob.matrix_world.inverted();pts=[ob.matrix_world@v.co for v in ob.data.vertices];centers=[pts[0]]+[sum(pts[1+i*32:1+(i+1)*32],Vector())/32 for i in range(79)]+[pts[-1]]
  for i,v in enumerate(ob.data.vertices):
   row=0 if i==0 else 80 if i==n-1 else (i-1)//32+1;t=row/80;weight=smooth((t-cfg['start'])/(1-cfg['start']))
   if weight<=0:continue
   center=centers[row];dv=center-a.C;q=Vector((dv.x/.48,dv.y/.405,dv.z/.455));theta=math.acos(max(-1,min(1,q.normalized().z)));phi=math.atan2(q.x,-q.y);target=cfg['target']+.10*smooth((abs(phi)-1.6)/.8);nth=theta-max(0,theta-target)*weight*cfg['angle_weight'];N=dv.normalized();hit,_,_,dist=c.HEAD.ray_cast(a.C,N,2);dep=max(.003,dv.length-dist);newcenter=c.sp(nth,phi,dep*(1-cfg['depth_reduce']*weight));delta=pts[i]-center;rad=N*delta.dot(N);tan=delta-rad;v.co=inv@(newcenter+tan*(1-cfg['width_reduce']*weight)+rad*(1-cfg['radial_reduce']*weight));count+=1
  if cfg['rear']:
   for v in ob.data.vertices:
    p=ob.matrix_world@v.co;w=smooth((p.y-.06)/.20)*.78;dv=p-a.C;hit,_,_,dist=c.HEAD.ray_cast(a.C,dv.normalized(),2);dep=max(.003,dv.length-dist)
    if w>0:v.co=inv@(hit+dv.normalized()*(dep*(1-.65*w)))
  for m in ob.data.materials:
   old.normal_texture(m,'long');m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.36
   for node in m.node_tree.nodes:
    if node.type=='NORMAL_MAP':node.inputs['Strength'].default_value=cfg['normal_strength']
 return count

def restore_sides(folder,cfg):
 mat=a.material('Hair255 / reconstructed coverage '+folder.name,(.12,.047,.026),cfg['rough']);bs=mat.node_tree.nodes['Principled BSDF'];bs.inputs['Specular IOR Level'].default_value=.30;bs.inputs['Coat Weight'].default_value=.035;tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(folder/'coverage.png'),check_existing=True);tex.image.pack();tex.extension='EXTEND' if cfg['clamp'] else 'REPEAT';mix=mat.node_tree.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[2].default_value=(.12,.047,.026,1);mat.node_tree.links.new(tex.outputs['Color'],mix.inputs[1]);mat.node_tree.links.new(mix.outputs[0],bs.inputs['Base Color']);mat.node_tree.links.new(tex.outputs['Alpha'],bs.inputs['Alpha']);nm=mat.node_tree.nodes.new('ShaderNodeTexImage');nm.image=bpy.data.images.load(str(folder/'normal.png'),check_existing=True);nm.image.colorspace_settings.name='Non-Color';nm.image.pack();nm.extension='EXTEND' if cfg['clamp'] else 'REPEAT';normal=mat.node_tree.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.33;mat.node_tree.links.new(nm.outputs['Color'],normal.inputs['Color']);mat.node_tree.links.new(normal.outputs[0],bs.inputs['Normal']);nu,nv=384,112;vv=[];ff=[]
 for j in range(nv+1):
  t=j/nv
  for i in range(nu):
   phi=i/nu*2*PI;theta=.003+t*old.boundary(phi,False);density=smooth((1-t)/cfg['fade_span']);lift=.0025+cfg['lift']*density**1.25;ridge=cfg['ridge']*math.cos(phi*122+theta*4)*density*smooth(t/.15)*smooth((1-t)/.06);vv.append(tuple(c.sp(theta,phi,lift+ridge)))
 for j in range(nv):
  for i in range(nu):x=j*nu+i;y=j*nu+(i+1)%nu;ff.append((x,y,y+nu,x+nu))
 ff.append(tuple(range(nu-1,-1,-1)));ob=a.mesh('Hair255 / reconstructed smooth sides '+folder.name,vv,ff,mat,'hair');uv=ob.data.uv_layers.new(name='Clipped coverage255')
 for f in ob.data.polygons:
  seam=any(k%nu>nu*.9 for k in f.vertices)
  for li,k in zip(f.loop_indices,f.vertices):row,col=divmod(k,nu);uv.data[li].uv=(1 if seam and col==0 else col/nu,1-row/nv)

def patch(path):
 r=path.read_bytes();n=struct.unpack_from('<I',r,12)[0];g=json.loads(r[20:20+n]);found=False
 for m in g['materials']:
  if m.get('name','').startswith('Hair255 / reconstructed coverage'):
   m['alphaMode']='BLEND';m['doubleSided']=False;m['pbrMetallicRoughness']['baseColorFactor']=[.12,.047,.026,1];found=True
 # Clamp exported coverage borders to avoid the discarded repeated-edge line.
 for sm in g.get('samplers',[]):sm.update(wrapS=33071,wrapT=33071)
 assert found;js=json.dumps(g,separators=(',',':')).encode();js+=b' '*((-len(js))%4);binary=r[28+n:];path.write_bytes(struct.pack('<III',0x46546c67,2,28+len(js)+len(binary))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(binary),0x004e4942)+binary)

def views(s,folder):
 c.gpu()
 for angle in ['front','threequarter','profile','rightprofile','rear','top','underside']:
  target=folder/(angle+'.png');assert not target.exists();u.camera(s,angle,512,False);s.camera.data.ortho_scale=1.65;s.cycles.samples=24;s.render.filepath=str(target);floor=s.objects.get('Studio floor');hidden=floor.hide_render if floor else False
  if floor and angle=='underside':floor.hide_render=True
  try:bpy.ops.render.render(write_still=True)
  finally:
   if floor:floor.hide_render=hidden

def build(key):
 folder=P/'drafts'/key;cfg=json.loads((folder/'settings.json').read_text());assert not (folder/'source.blend').exists() and not (folder/'hair.glb').exists();bpy.ops.wm.open_mainfile(filepath=cfg['geometry_source']);s=bpy.context.scene;frozen=protect(s);a.setup();c.reset_head(s)
 for ob in list(s.objects):
  if ob.get('component159')=='hair' and any('fade coverage' in m.name or 'buzz edge' in m.name for m in ob.data.materials):u.delete(ob)
 count=restore_long(s,cfg);restore_sides(folder,cfg);check(s,frozen);u.bake(s);bpy.ops.outliner.orphans_purge(do_recursive=True);bpy.ops.file.pack_all();u.camera(s,'front',512,False);s.camera.data.ortho_scale=1.65;bpy.ops.wm.save_as_mainfile(filepath=str(folder/'source.blend'),compress=True);ex.export(s,folder/'hair.glb','hair');patch(folder/'hair.glb');shutil.copy2(__file__,folder/'recovery-script.py');shutil.copy2(P/'texture255.py',folder/'texture-script.py');views(s,folder);check(s,frozen);receipt=dict(draft=key,label=cfg['label'],status='Reconstruction, not an exact recovered checkpoint',modified_vertices=count,other_geometry_preserved=True,settings=u.settings(s),original_log_sha256=hashlib.sha256(Path(cfg['original_log']).read_bytes()).hexdigest());(folder/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8');print('RECOVERED255',key,flush=True)
if __name__=='__main__':
 for key in ['A','B','C']:build(key)
 print('RECOVERY255_COMPLETE3',flush=True)
