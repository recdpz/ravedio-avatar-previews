import sys
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue250')
from fit250 import *
out=json.loads((P/'fits250.json').read_text())
for b,bc in CAT250['builds'].items():
 for style in bc['hair']:
  default='open' if b=='Feminine' else 'tank';ref=out[b+'-'+style+'-'+default]
  for top in bc['tops']:
   if top==default:continue
   key=b+'-'+style+'-'+top
   if '--resume' in sys.argv and key in out:continue
   s,paths=load250(b,style,top);frozen=u.object_geometry(s);shape=hood_shape(s,b,style);now=u.object_geometry(s);assert all(now.get(k)==v for k,v in frozen.items() if s.objects[k].get('component159')!='headgear')
   path=P/'components'/f'{key}-pashmina250-headgear.glb';ex.export(s,path,'headgear');out[key]={**ref,'top':top,'headgear':'components/'+path.name,'hood':shape,'source':FITS249[key]['source'],'source_recipe':'Reconstruct249 native fit via common250.load250, then apply hood_shape; shared250 covered hair from default style.'};(P/'fits250.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8');print('TOP250',key,flush=True)
print('TOP250_COMPLETE',len(out),flush=True)
