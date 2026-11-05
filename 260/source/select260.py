from pathlib import Path
import json,shutil
P=Path(__file__).parent;rows={}
for stage in ['pass2','pass3','pass4','pass5','pass6','pass7']:
 rows.update(json.loads((P/stage/'hair260.json').read_text()))
assert len(rows)==7
for k,row in rows.items():
 assert Path(row['source']).exists() and Path(row['path']).exists()
for stage in ['pass2','pass3','pass4','pass5','pass6','pass7']:
 for name in ['build260.py','female260.py']:
  f=P/stage/name
  if not f.exists():shutil.copy2(P/name,f)
(P/'selected260.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf8');print('SELECTED260',list(rows))
