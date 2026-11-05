import sys,json,math,hashlib,shutil
from pathlib import Path
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue259')
from build259 import *
import hair252 as old
P=Path('E:/Ravedio-Avatar/catalogue260');R=P.parent/'floating138/mobile-preview';BASE=R/'259';CAT=json.loads((BASE/'catalogue259.json').read_text())
STYLES={'Masculine':['afro','flow','locs','middle-part'],'Feminine':['straight','side-sweep','box-braids']}
ANGLES=['front','threequarter','profile','rightprofile','rear','rearquarter','top','underside']

def proportional260(s):
 count=0
 for ob in [o for o in s.objects if o.type=='MESH' and o.get('component159')=='hair']:
  inv=ob.matrix_world.inverted()
  for v in ob.data.vertices:
   p=ob.matrix_world@v.co;d=p-a.C;N=d.normalized();hit,_,_,distance=c.HEAD.ray_cast(a.C,N,2)
   if hit is None or d.length<=distance:continue
   factor=.065+.935*smooth((2.15-p.z)/.35);v.co=inv@(hit+N*(.0015+(d.length-distance)*factor));count+=1
 return count

def load260(build,style):
 bpy.ops.wm.open_mainfile(filepath=str(P.parent/'catalogue251/sources'/f'{build}-assembly251.blend'));s=bpy.context.scene
 for o in list(s.objects):
  if o.type in ['MESH','CURVE'] and o.name!='Studio floor':u.delete(o)
 bc=CAT['builds'][build];top='open' if build=='Feminine' else 'tank'
 paths=dict(base=bc['base'],top=bc['tops'][top]['path'],bottom=bc['bottoms']['skirt' if build=='Feminine' else 'shorts']['path'],eyes=bc['eyes']['original']['path'],mouth=bc['mouths']['line']['path'],hair=bc['hair'][style]['path'])
 if build=='Feminine':paths['lashes']=bc['lashes']['original']['path']
 for group,path in paths.items():
  if path:imported((BASE/path).resolve(),group)
 u.tone(s,1);a.setup();c.reset_head(s);s['build235']=build;s['hairStyle235']=style;s['revision260']=True;return s

def clean_normals(ob):
 if ob.data.has_custom_normals:ob.data.normals_split_custom_set([(0.,0.,0.)]*len(ob.data.loops))
 ob.data.update()
 for f in ob.data.polygons:f.use_smooth=True

def save260(s,build,style,stage,report):
 W=P/stage
 for d in ['sources','components']:(W/d).mkdir(parents=True,exist_ok=True)
 u.bake(s)
 for ob in s.objects:
  if ob.type=='MESH' and ob.get('component159')=='hair':clean_normals(ob)
 bpy.ops.outliner.orphans_purge(do_recursive=True);bpy.ops.file.pack_all()
 src=W/'sources'/f'{build}-{style}-hair260.blend';out=W/'components'/f'{build}-{style}-hair260.glb';assert not src.exists() and not out.exists()
 bpy.ops.wm.save_as_mainfile(filepath=str(src),compress=True);ex.export(s,out,'hair');prev258.patch258(out,s)
 report.update(source=str(src),path=str(out),shared_coordinates=True,non_hair_geometry_protected=True)
 f=W/'hair260.json';data=json.loads(f.read_text()) if f.exists() else {};data[build+'-'+style]=report;f.write_text(json.dumps(data,indent=2)+'\n',encoding='utf8');print('SOURCE260',build,style,stage,flush=True)

if __name__=='__main__':
 out={}
 for build,styles in STYLES.items():
  for style in styles:
   s=load260(build,style);rows=[]
   for ob in s.objects:
    if ob.type!='MESH' or ob.get('component159')!='hair':continue
    pts=np.array([ob.matrix_world@v.co for v in ob.data.vertices]);rows.append(dict(name=ob.name,vertices=len(pts),min=pts.min(0).tolist(),max=pts.max(0).tolist(),materials=[m.name for m in ob.data.materials]))
   out[build+'-'+style]=rows
 (P/'baseline-objects260.json').write_text(json.dumps(out,indent=2)+'\n');print('INVENTORY260_COMPLETE',flush=True)
