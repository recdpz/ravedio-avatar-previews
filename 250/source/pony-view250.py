import sys
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue250')
from common250 import *
bpy.ops.wm.open_mainfile(filepath=str(P/'sources/Feminine-ponytail-open-pashmina250.blend'));s=bpy.context.scene
for o in s.objects:
 if o.get('component159')=='headgear':o.hide_render=True
close(s,'ponytail-root-final',['profile','rear'],'review1',512)
