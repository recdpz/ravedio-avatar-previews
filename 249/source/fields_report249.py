from pathlib import Path
import numpy as np,json
P=Path(__file__).parent;rows=[]
for path in sorted((P/'fields').glob('*.npz')):
 f=np.load(path);p=f['positions'][f['ids']];d=f['delta']
 crossing=(p[:,1]<-.255)&(p[:,2]<1.62)
 rows.append(dict(name=path.stem,moved=len(p),front_crossing_changes=int(crossing.sum()),max_delta=float(np.linalg.norm(d,axis=1).max())))
assert all(x['front_crossing_changes']==0 for x in rows),rows
(P/'fields-proof249.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf8')
print('FIELD249',len(rows),'deformation fields; front crossing regions untouched')
