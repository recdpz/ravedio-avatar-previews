import sys,json
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue251')
import hair251 as h
q=json.loads((h.P/'hair251.json').read_text())
for style in ['afro','flow','locs']:
 q[style]=h.build(style);(h.P/'hair251.json').write_text(json.dumps(q,indent=2));print('REFRESH_HAIR',style,flush=True)
import female_hats251 as f
q=json.loads((f.P/'female-hats251.json').read_text())
for top in f.CAT251['builds']['Feminine']['tops']:
 q['braidLengths']['pashmina'][top]=f.braid_lengths(top,True);(f.P/'female-hats251.json').write_text(json.dumps(q,indent=2));print('REFRESH_BRAID',top,flush=True)
q['bucket']={b:f.bucket(b) for b in f.CAT251['builds']};(f.P/'female-hats251.json').write_text(json.dumps(q,indent=2));print('REFRESH_COMPLETE',flush=True)
