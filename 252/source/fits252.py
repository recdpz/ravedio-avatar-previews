import sys,json
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue252')
from common252 import *
from fits251 import fit_roots
HATS=['cap','beanie','bucket','cowboy','headband','ears','pashmina']
HAIR=json.loads((P/'hair252.json').read_text())
def case(style,hat):
 b='Feminine' if style=='straight' else 'Masculine';s,original=load252(b,style,hat);frozen=protect(s);headgear_before={k:v for k,v in u.object_geometry(s).items() if s.objects[k].get('component159')=='headgear'};remove(['hair']);imported(P/HAIR[style]['path'],'hair');a.setup();c.reset_head(s);changed=fit_roots(s,hat);check(s,frozen);now=u.object_geometry(s);assert all(now.get(k)==v for k,v in headgear_before.items());u.bake(s);key=b+'-'+style+'-'+hat;out=P/'components'/f'{key}252-hair.glb';ex.export(s,out,'hair');import accessories235
 sprout=accessories235.sprout();u.bake(s);ep=P/'components'/f'{key}252-sprout.glb';ex.export(s,ep,'extra');sprout['path']='components/'+ep.name;remove(['extra'])
 if '--no-render' not in sys.argv:render252(s,key,('front','profile','rear'),folder='review2',size=256)
 return dict(sprout=sprout,hair='components/'+out.name,headgear=original['headgear'],changed_vertices=changed,body_face_wardrobe_headgear_exact=True)
if __name__=='__main__':
 out=json.loads((P/'fits252.json').read_text()) if (P/'fits252.json').exists() else {};requested=next((x.split('=',1)[1].split(',') for x in sys.argv if x.startswith('--styles=')),list(HAIR))
 for style in requested:
  for hat in HATS:
   key=('Feminine' if style=='straight' else 'Masculine')+'-'+style+'-'+hat
   if '--resume' in sys.argv and key in out:continue
   out[key]=case(style,hat);(P/'fits252.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8');print('FIT252',key,flush=True)
 print('FIT252_COMPLETE',len(out),flush=True)
