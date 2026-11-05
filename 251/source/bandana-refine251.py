import sys,json
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue251')
import hair251 as h
hair=json.loads((h.P/'hair251.json').read_text())
for style in ['flow','locs']:
 hair[style]=h.build(style);(h.P/'hair251.json').write_text(json.dumps(hair,indent=2))
import female_hats251 as f
q=json.loads((f.P/'female-hats251.json').read_text());f.gpu()
for b,bc in f.CAT251['builds'].items():
 for style in bc['hair']:
  q['bandana'][b+'-'+style]=f.bandana(b,style)
(f.P/'female-hats251.json').write_text(json.dumps(q,indent=2))
import fits251 as g
g.FH=q;out=json.loads((f.P/'fits251.json').read_text());hoods=json.loads((f.P/'pony-hoods251.json').read_text())
for b,bc in f.CAT251['builds'].items():
 for style in bc['hair']:
  key=b+'-'+style+'-headband';out[key]=g.case(b,style,'headband',hoods);(f.P/'fits251.json').write_text(json.dumps(out,indent=2));print('BANDANA_FINAL',key,flush=True)
for style in ['flow','locs']:
 for hat in [x for x in g.HATS if x!='headband']:
  key='Masculine-'+style+'-'+hat;out[key]=g.case('Masculine',style,hat,hoods);(f.P/'fits251.json').write_text(json.dumps(out,indent=2));print('HAIR_FIT_FINAL',key,flush=True)
print('BANDANA_FINAL_COMPLETE',flush=True)
