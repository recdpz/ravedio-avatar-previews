import sys,json,math,shutil
from pathlib import Path
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue259')
import build259 as b
from build259 import *
P=Path('E:/Ravedio-Avatar/catalogue259');W=P/'pass4';b.W=W
for name in ['sources','components','renders']:(W/name).mkdir(parents=True,exist_ok=True)
report=json.loads((P/'pass3/hair259.json').read_text())
for style in ['taper','curly-top']:
 for group,ext in [('sources','.blend'),('components','.glb')]:
  src=P/'pass3'/group/f'Masculine-{style}-hair259{ext}';dst=W/group/src.name;assert not dst.exists();shutil.copy2(src,dst)
 report[style].update(source=str(W/'sources'/f'Masculine-{style}-hair259.blend'),path=str(W/'components'/f'Masculine-{style}-hair259.glb'),pass3_geometry_and_materials_exact=True)
 for src in (P/'pass3/renders').glob(style+'-*.png'):shutil.copy2(src,W/'renders'/src.name)
bpy.ops.wm.open_mainfile(filepath=str(P/'pass3/sources/Masculine-sidepart-hair259.blend'));s=bpy.context.scene;frozen=protect(s);a.setup();c.reset_head(s)
for ob in list(s.objects):
 if ob.get('component159')=='hair' and 'continuous forward Crop' in ob.name:u.delete(ob)
mat=a.material('Hair259 / textured forward Crop',(.12,.047,.026),.35);old.normal_texture(mat,'long');bs=mat.node_tree.nodes['Principled BSDF'];bs.inputs['Specular IOR Level'].default_value=.34;bs.inputs['Coat Weight'].default_value=.055
for n in mat.node_tree.nodes:
 if n.type=='NORMAL_MAP':n.inputs['Strength'].default_value=.18
edge_mat=mat.copy();edge_mat.name='Hair259 / blended terminal Crop edges';attr=edge_mat.node_tree.nodes.new('ShaderNodeVertexColor');attr.layer_name='Hair257 opacity';edge_mat.node_tree.links.new(attr.outputs['Alpha'],edge_mat.node_tree.nodes['Principled BSDF'].inputs['Alpha'])
nu,nv=144,176;verts=[];under=[];uvs=[];rgba=[];faces=[]
for j in range(nv+1):
 t=j/nv;width=.36*(1-t)+.345*t+.068*math.sin(PI*t)
 for i in range(nu+1):
  side=i/nu*2-1;x=side*width+.027*math.sin(PI*t)*(1-side*side)
  def phase(t):return (side+1)*3.35+.16*math.sin(t*4.7)+.12*math.sin(side*5+t*1.6)
  endangle=.84+.085*(.5+.5*math.cos(phase(1)*2*PI))**.8+.010*math.sin(side*7)+.005*math.sin(side*19);endx=side*.345;endy=-.405*math.sqrt(max(.015,math.sin(endangle)**2-(endx/.48)**2));startx=side*.36;starty=.405*math.sqrt(max(.015,math.sin(1.05)**2-(startx/.48)**2));y=starty*(1-t)+endy*t;hit=c.surf(x,y,0);N=(hit-a.C).normalized();ph=phase(t);envelope=math.sin(PI*t)**.60;ridge=.025*(.5+.5*math.cos(ph*2*PI))**1.35*envelope;grain=.0015*math.cos(ph*2*PI*5+.3*math.sin(t*5))*envelope;clumps=0
  for sc,amp in [(-.53,.010),(.07,.016),(.59,.011)]:clumps+=amp*math.exp(-((side-sc-.07*math.sin(t*3))/.18)**2)*math.sin(PI*t)**1.8
  edge=smooth((1-abs(side))/.12)*smooth(t/.07)*smooth((1-t)/.035);lift=.0028+edge*(.012+.022*math.sin(PI*t)**.70+ridge+grain+clumps);verts.append(tuple(hit+N*lift));under.append(tuple(hit+N*.0017));uvs.append(((side+1)/2+.022*math.sin(t*4.7),1-t));alpha=smooth((1-abs(side))/.025)*smooth(t/.035)*smooth((1-t)/.015);rgba.append((1,1,1,alpha))
count=len(verts);verts+=under;uvs+=uvs;rgba+=list(rgba)
for j in range(nv):
 for i in range(nu):
  k=j*(nu+1)+i;faces.append((k,k+nu+1,k+nu+2,k+1));faces.append((count+k,count+k+1,count+k+nu+2,count+k+nu+1))
edge=list(range(nu+1))+[j*(nu+1)+nu for j in range(1,nv+1)]+list(range(nv*(nu+1)+nu-1,nv*(nu+1)-1,-1))+[j*(nu+1) for j in range(nv-1,0,-1)]
for i,k in enumerate(edge):n=edge[(i+1)%len(edge)];faces.append((k,n,count+n,count+k))
ob=a.mesh('Hair259 / textured forward Crop',verts,faces,mat,'hair');ob.data.materials.append(edge_mat);prev258.vertex_alpha(ob,rgba);uv=ob.data.uv_layers.new(name='Forward Crop flow259')
for face in ob.data.polygons:
 if min(rgba[k][3] for k in face.vertices)<.999999:face.material_index=1
 for li,k in zip(face.loop_indices,face.vertices):uv.data[li].uv=uvs[k]
check(s,frozen);u.bake(s);source=W/'sources/Masculine-sidepart-hair259.blend';target=W/'components/Masculine-sidepart-hair259.glb';assert not source.exists() and not target.exists();bpy.ops.outliner.orphans_purge(do_recursive=True);bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True);ex.export(s,target,'hair');prev258.patch258(target,s);report['sidepart'].update(source=str(source),path=str(target),construction='Closed forward-flow sculpt with varied rounded fringe clumps, shallow coherent grooves, and narrow edge transitions into the short groom',edge_treatment='Main surface opaque; only narrow terminal boundaries use vertex alpha. Geometric lift tapers into side/back coverage, removing raised shell rim.');b.render_views(s,'sidepart');(W/'hair259.json').write_text(json.dumps(report,indent=2)+'\n');shutil.copy2(__file__,W/'finish-sculpt259.py');print('FINAL_SCULPT259_COMPLETE3',flush=True)
