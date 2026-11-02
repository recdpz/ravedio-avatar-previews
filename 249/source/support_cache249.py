import sys
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue249')
from fit249 import *
(P/'support').mkdir(exist_ok=True)
fits=json.loads((P/'fits249.json').read_text())
for b in CAT249['builds']:
 for style in CAT249['builds'][b]['hair']:
  top='open' if b=='Feminine' else 'tank';bpy.ops.wm.open_mainfile(filepath=fits[b+'-'+style+'-'+top]['source']);s=bpy.context.scene
  _,count=broad_support(s,P/'support'/f'{b}-{style}.npz');print('SUPPORT249',b,style,count,flush=True)
print('SUPPORT249_COMPLETE',16)
