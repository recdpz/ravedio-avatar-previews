"""Consolidate export copies within one component/material/attribute boundary."""
import bpy,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent.parent/'refinement224'));import utils224 as u
def export(s,path,group):
 originals=[o for o in s.objects if o.type=='MESH' and not o.hide_render and o.get('component159')==group];copies=[];buckets={}
 try:
  for o in originals:
   n=o.copy();n.data=o.data.copy();s.collection.objects.link(n);copies.append(n);o.hide_render=True
   signature=(tuple(m.name if m else '' for m in n.data.materials),tuple((c.name,c.domain,c.data_type) for c in n.data.color_attributes))
   buckets.setdefault(signature,[]).append(n)
  for sig,parts in buckets.items():
   bpy.ops.object.select_all(action='DESELECT')
   for o in parts:o.select_set(True)
   bpy.context.view_layer.objects.active=parts[0]
   if len(parts)>1:bpy.ops.object.join()
   parts[0].name='226 '+group+' / '+(sig[0][0] if sig[0] else 'surface');parts[0]['component159']=group
  return u.export(s,path,group)
 finally:
  for o in list(s.objects):
   if o not in originals and o.get('component159')==group and not o.hide_render:u.delete(o)
  for o in originals:o.hide_render=False
