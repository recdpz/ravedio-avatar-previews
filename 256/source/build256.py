import sys,json,math,struct,shutil,hashlib
from pathlib import Path
sys.path.insert(0,'E:/Ravedio-Avatar/recovery255')
from recover255 import *
P=Path('E:/Ravedio-Avatar/catalogue256');W=P/'pass1';CFG=json.loads((P/'inputs/settings.json').read_text())

def patch256(path):
 r=path.read_bytes();n=struct.unpack_from('<I',r,12)[0];g=json.loads(r[20:20+n]);found=False
 for m in g['materials']:
  if m.get('name','').startswith('Hair256 / selected B sides'):
   m['alphaMode']='BLEND';m['doubleSided']=False;m['pbrMetallicRoughness']['baseColorFactor']=[.12,.047,.026,1];found=True
 for m in g['materials']:
  if m.get('name','').startswith('Hair256 / selected B sides'):
   ids=[m['pbrMetallicRoughness']['baseColorTexture']['index']]
   if 'normalTexture' in m:ids.append(m['normalTexture']['index'])
   for ti in ids:
    tx=g['textures'][ti];sm=dict(g.get('samplers',[])[tx['sampler']]) if 'sampler' in tx else {};sm.update(wrapS=33071,wrapT=33071);tx['sampler']=len(g.setdefault('samplers',[]));g['samplers'].append(sm)
 assert found;js=json.dumps(g,separators=(',',':')).encode();js+=b' '*((-len(js))%4);binary=r[28+n:];path.write_bytes(struct.pack('<III',0x46546c67,2,28+len(js)+len(binary))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(binary),0x004e4942)+binary)

def build(style):
 source=Path('E:/Ravedio-Avatar/recovery255/drafts/B/source.blend') if style=='taper' else P.parent/'catalogue254/sources/Masculine-curly-top-hair254.blend';bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;frozen=protect(s);a.setup();c.reset_head(s)
 for ob in list(s.objects):
  if ob.get('component159')=='hair' and any(m.name.startswith(('Hair255 / reconstructed coverage','Hair254 / rooted short groom')) for m in ob.data.materials):u.delete(ob)
 longer={k:v for k,v in u.object_geometry(s).items() if s.objects[k].get('component159')=='hair'};assert longer
 before=set(s.objects);restore_sides(P/'inputs',CFG)
 for ob in set(s.objects)-before:
  if ob.type=='MESH':
   ob.name='Hair256 / selected B fuller sides';ob.data.materials[0].name='Hair256 / selected B sides'
 now=u.object_geometry(s);assert all(now.get(k)==v for k,v in longer.items()),'Selected top shape changed';check(s,frozen);u.bake(s);source_out=W/'sources'/f'Masculine-{style}-hair256.blend';target=W/'components'/f'Masculine-{style}-hair256.glb';assert not source_out.exists() and not target.exists();bpy.ops.outliner.orphans_purge(do_recursive=True);bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(source_out),compress=True);ex.export(s,target,'hair');patch256(target);c.gpu()
 for angle in ['front','threequarter','profile','rightprofile','rear','top','underside']:
  out=W/'renders'/f'{style}-{angle}.png';assert not out.exists();u.camera(s,angle,512,False);s.camera.data.ortho_scale=1.65;s.cycles.samples=24;s.render.filepath=str(out);floor=s.objects.get('Studio floor');hidden=floor.hide_render if floor else False
  if floor and angle=='underside':floor.hide_render=True
  try:bpy.ops.render.render(write_still=True)
  finally:
   if floor:floor.hide_render=hidden
 return dict(path=str(target),source=str(source_out),selected_top_geometry_preserved=True,other_geometry_preserved=True,fade_span=.38,previous_fade_span=.30,lower_boundary_preserved=True)
if __name__=='__main__':
 out={}
 for style in ['taper','curly-top']:out[style]=build(style);(W/'hair256.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8')
 shutil.copy2(__file__,W/'build256.py');shutil.copy2(P/'inputs/settings.json',W/'settings.json');print('BARE256_COMPLETE2',flush=True)
