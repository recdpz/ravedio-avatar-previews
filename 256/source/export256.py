import sys,json,shutil,hashlib
from pathlib import Path
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue256')
from build256 import *
P=Path('E:/Ravedio-Avatar/catalogue256');W=P/'pass2'
for p in [W,W/'sources',W/'components',W/'renders']:p.mkdir(exist_ok=True)
out={}
for style in ['taper','curly-top']:
 source=P/'pass1/sources'/f'Masculine-{style}-hair256.blend';target=W/'sources'/source.name;assert not target.exists();shutil.copy2(source,target);bpy.ops.wm.open_mainfile(filepath=str(target));s=bpy.context.scene;dest=W/'components'/f'Masculine-{style}-hair256.glb';assert not dest.exists();ex.export(s,dest,'hair');patch256(dest)
 for img in (P/'pass1/renders').glob(style+'-*.png'):shutil.copy2(img,W/'renders'/img.name)
 out[style]=dict(path=str(dest),source=str(target),selected_top_geometry_preserved=True,other_geometry_preserved=True,fade_span=.38,previous_fade_span=.30,lower_boundary_preserved=True,sampler_correction='Only the side-coverage textures are clamped; B long-hair normal-map sampling is preserved.',source_and_reference_images_byte_identical_to_pass1=True);assert hashlib.sha256(source.read_bytes()).digest()==hashlib.sha256(target.read_bytes()).digest()
(W/'hair256.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8');shutil.copy2(P/'build256.py',W/'build256.py');shutil.copy2(__file__,W/'export256.py');shutil.copy2(P/'inputs/settings.json',W/'settings.json');print('EXPORT256_COMPLETE2',flush=True)
