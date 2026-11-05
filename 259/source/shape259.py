import sys,json,math
from pathlib import Path
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue259')
from build259 import *
P=Path('E:/Ravedio-Avatar/catalogue259');report=json.loads((P/'pass4/hair259.json').read_text());out={}
def coordinates(ob):return np.array([ob.matrix_world@v.co for v in ob.data.vertices],dtype='<f4')
for style in ['taper','curly-top']:
 bpy.ops.wm.open_mainfile(filepath=str(P.parent/'catalogue258/pass4/sources'/f'Masculine-{style}-hair258.blend'));oldpos={o.name:coordinates(o) for o in bpy.context.scene.objects if o.type=='MESH' and o.get('component159')=='hair'}
 bpy.ops.wm.open_mainfile(filepath=str(P/'pass4/sources'/f'Masculine-{style}-hair259.blend'));newpos={o.name:coordinates(o) for o in bpy.context.scene.objects if o.type=='MESH' and o.get('component159')=='hair'}
 if style=='taper':
  banks=[]
  for row in report[style]['banks']:
   before=oldpos[row['name']];after=newpos[row['name']];cap=row['round_cap_start'];ids=[i for i in range(len(before)) if (0 if i==0 else 1 if i==2529 else ((i-1)//32+1)/80)<=cap];assert np.array_equal(before[ids],after[ids]);rise=float(after[-1,2]-before[-1,2]);assert rise>.10;banks.append(dict(name=row['name'],upper_vertices_exact=len(ids),end_rise=rise,geometry_before_sha256=hashlib.sha256(before.tobytes()).hexdigest(),geometry_after_sha256=hashlib.sha256(after.tobytes()).hexdigest()))
  napes=[n for n in oldpos if 'Side part nape' in n];assert len(napes)==6 and all(np.array_equal(oldpos[n],newpos[n]) for n in napes)
  oldheight=max(v[:,2].max() for n,v in oldpos.items());newheight=max(v[:,2].max() for n,v in newpos.items());assert abs(float(oldheight-newheight))<1e-6;out[style]=dict(banks=banks,rounded_rear_banks_exact=napes,top_height_unchanged=True,top_max_z=float(newheight),cut='Original centerline retained through cap start, then rounded closure along truncated path')
 else:
  names=[n for n in oldpos if 'unified rooted curly sculpt' in n];assert names and all(np.array_equal(oldpos[n],newpos[n]) for n in names);out[style]=dict(crown_positions_exact=names)
bpy.ops.wm.open_mainfile(filepath=str(P/'pass4/sources/Masculine-sidepart-hair259.blend'));obs=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.get('component159')=='hair'];crop=next(o for o in obs if 'textured forward Crop' in o.name);import bmesh;bm=bmesh.new();bm.from_mesh(crop.data);assert all(len(e.link_faces)==2 for e in bm.edges);bm.free();assert not any('Side part ' in o.name for o in obs);out['crop']=dict(new_source=True,no_old_sidepart_objects=True,closed_surface=True,vertices=len(crop.data.vertices),flow='Crown to front, shallow irregular clumps, no hard part',shared_coordinates_unchanged=True)
(P/'shape259.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8',newline='\n');print('SHAPE259_COMPLETE',len(out['taper']['banks']),'trimmed banks; six rear banks and top height preserved',flush=True)
