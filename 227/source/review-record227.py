"""Durable checkpoint with explicit evidence gates; never infer visual acceptance."""
from pathlib import Path
import json,hashlib,shutil,datetime
P=Path(__file__).parent;O=P/'revision227';D=P.parent/'floating138/mobile-preview/227'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
proof=read(O/'export-proof.json')
for key,item in proof.items():
 assert sha(Path(item['source']))==item['source_sha256'],('stale source',key)
 for group,path in item['components'].items():assert sha(O/path)==item['component_sha256'][group],('stale GLB',key,group)
review={
 'revision':227,'retained_checkpoint':224,'status':'Implementation and export checkpoint; component acceptance and native qualification remain separate',
 'protected':['209 face and feature placement','224 retained head/body geometry','selected224 ponytail and cap','178 floating arms','current clothing and bottoms','skin palette','fixed authoring studio'],
 'implemented':[
  'Rebuilt scalp support against the actual retained head instead of an approximate ellipsoid for crop/fade construction.',
  'Removed exposed loose-hair scalp skirt construction; reused developed cartoon root topology with newly shaped falling lengths.',
  'Built denser open curl clusters over recessed support, plus real vertex-density and short-grain taper.',
  'Constructed separate twin gathers, woven braids, compact wrapped buns, and smoother loc ends.',
  'Rebuilt hat crowns/brims and continuous pashmina drape/ends.',
  'Separated thin transmitting lenses from frames and corrected planar lens normals to remove false prism distortion.',
  'Exported ordinary uncompressed GLBs in the original shared coordinates; consolidated only within component/material roles.',
  'Added a bounded-cache review viewer, full angle controls, separate visibility, four tones and matched exported-asset references.'
 ],
 'technical_export':{'cases':len(proof),'components':sum(len(x['components']) for x in proof.values()),'maximum_world_vertex_error':max(e for x in proof.values() for e in x['max_bidirectional_world_position_error'].values()),'source_and_export_hashes_verified':True,'compression':'none'},
 'visual_review':{'construction':'Reviewed source renders; multiple corrections made for coverage, attachment, clipping and lens distortion.','final_exports':'Pending explicit final-angle dispositions. Render completion alone is not a pass.','owner_approval':'pending','native_app':'not tested','portrait_depth_compositor':'transmission still requires a separate implementation/test','phone_performance':'not tested'},
 'catalogue_notes':['Faceted frames are a hexagonal-frame shape, not validated kaleidoscope optical distortion.','The selected224 ponytail/cap remain unchanged. New headwear combinations require their own fit dispositions.','These are authored assets, not mobile-budget derivatives. No profile-bit allocations changed.'],
 'next_gates':['Resolve recorded artistic holds: curls, locs, masculine flow, bucket/cowboy character and pashmina folds','Owner artwork review','Separate optimized derivatives and matched visual comparison','Native 3D and lightweight-portrait fidelity','Actual iOS/Android workload measurement'],
 'assets':{k:{'source_sha256':v['source_sha256'],'component_sha256':v['component_sha256'],'status':'candidate; see final visual dispositions'} for k,v in proof.items()}
}
if (O/'fit-dispositions.json').exists():review['hair_headwear_fit']=read(O/'fit-dispositions.json')
if (O/'visual-dispositions.json').exists():review['visual_review']['final_exports']=read(O/'visual-dispositions.json')
if (O/'browser-proof227.json').exists():review['browser_check']=read(O/'browser-proof227.json')
if (O/'browser-fit-proof227.json').exists():review['fit_browser_check']=read(O/'browser-fit-proof227.json')
fits=read(O/'fit-proof.json')
for key,record in fits.items():
 for hat,item in record['combinations'].items():
  path=item.get('specific_component') or (record['component'] if item['covered_variant'] else proof[key]['components']['hair'])
  assert sha(O/path)==item['rendered_hair_sha256'],('stale fit',key,hat)
  assert sha(D/path)==item['rendered_hair_sha256'],('stale staged fit',key,hat)
review['technical_export']['fit_combinations_hash_verified']=sum(len(r['combinations']) for r in fits.values())
(O/'review227.json').write_text(json.dumps(review,indent=2)+'\n');shutil.copy2(O/'review227.json',D/'review227.json')
source=D/'source';source.mkdir(exist_ok=True)
for name in ['hair227.py','accessories227.py','review227.py','accessory_review227.py','export227.py','export226.py','build226.py','sculpt226.py','rebuild_hair226.py','fit226.py','fit227.py','package227.py','package-fits227.py','view227.py','browser227.cjs','browser-fits227.cjs','additional-sheets227.py','small227.py','dispositions227.py','review-record227.py']:
 shutil.copy2(P/name,source/name)
(D/'README227.txt').write_text('Ravedio227 — catalogue correction checkpoint\n\nRetained224 is unchanged. New artwork is a review candidate, not an owner-approved catalogue or phone-qualified renderer.\n\nView index.html via HTTP. Each look uses independently selectable shared-coordinate GLBs and unchanged224 base components. See looks227.json and asset-statistics227.json. Frames/lenses remain separate. Transmitting lenses use KHR_materials_transmission; OPAQUE does not mean opaque glass.\n\nSource Blender assemblies remain at E:/Ravedio-Avatar/catalogue226/revision227/sources; exact hashes are in export-proof227.json. The public source directory holds the modeling/export scripts; it is not a standalone substitute for retained224 authoring inputs.\n\nThe native/ images are actual exported GLBs reopened in Blender, not screenshots of the native app. Browser lighting is an approximation. No native-app or phone-performance claim is made. No profile wire changes.\n\nRead review227.json for explicit visual/fit dispositions and remaining gates.\n',encoding='utf8')
print('VERIFIED227',len(proof),'sources and all exported component hashes')
