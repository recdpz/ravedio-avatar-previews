import sys,json
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue251')
import female_hats251 as f
q=json.loads((f.P/'female-hats251.json').read_text())
for b,bc in f.CAT251['builds'].items():
 for style in bc['hair']:
  q['bandana'][b+'-'+style]=f.bandana(b,style)
(f.P/'female-hats251.json').write_text(json.dumps(q,indent=2))
import fits251 as g
g.FH=q;out=json.loads((f.P/'fits251.json').read_text());hoods=json.loads((f.P/'pony-hoods251.json').read_text())
for b,bc in f.CAT251['builds'].items():
 for style in bc['hair']:
  key=b+'-'+style+'-headband';out[key]=g.case(b,style,'headband',hoods);(f.P/'fits251.json').write_text(json.dumps(out,indent=2));print('BANDANA_CONNECTED',key,flush=True)
# Publish only the changed headgear/sprout components. Hair and Highlights are untouched.
import shutil
for b,bc in f.CAT251['builds'].items():
 for style in bc['hair']:
  rec=out[b+'-'+style+'-headband']
  for k in ['headgear']:
   shutil.copy2(f.P/rec[k],f.D/rec[k])
  shutil.copy2(f.P/rec['sprout']['path'],f.D/rec['sprout']['path'])
proof=json.loads((f.P/'proof251.json').read_text());proof={k:v for k,v in proof.items() if '-headband-' not in k};(f.P/'proof251.json').write_text(json.dumps(proof,indent=2));print('BANDANA_CONNECTED_COMPLETE',flush=True)
