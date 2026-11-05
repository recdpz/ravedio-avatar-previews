import sys
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue235')
from common235 import *
import fits235 as fits
records=json.loads((P/'fits235.json').read_text());sprites=json.loads((P/'sprouts235.json').read_text())
for key,item in records.items():
 build,style=key.split('-',1)
 for hat in ['none']+list(item):
  s=load(build);remove(['hair','headgear','extra'])
  if hat=='none':imported(fits.hair_path(build,style),'hair')
  else:
   for group,path in item[hat].items():imported((P/path if path.startswith('components/') else R/'234'/path).resolve(),group)
  imported(P/sprites[key+'--'+hat]['path'],'extra');render(s,key+'--'+hat,['underside'],'review2',192,body=hat=='pashmina');print('UNDER235',key,hat,flush=True)
