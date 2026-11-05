from pathlib import Path
P=Path(__file__).parent
s=(P/'fits260.py').read_text(encoding='utf8').replace("W=P/'fits'","W=P/'fits4'")
s=s.replace(" build,style=key.split('-',1)\n"," build,style=key.split('-',1)\n if key not in ['Feminine-straight','Feminine-side-sweep']:continue\n")
s=s.replace("count=fit_roots(s,hat) if hat!='none' else 0","count=(proportional260(s) if hat in ['cap','beanie','bucket','cowboy'] else fit_roots(s,hat)) if hat!='none' else 0")
(P/'female-fits260.py').write_text(s,encoding='utf8',newline='\n')
s=(P/'reference260.py').read_text(encoding='utf8').replace("out=P/'reference'","out=P/'reference2'").replace("P/'packed'","P/'packed2'")
s=s.replace("records=[];assemblies={}","records=[r for r in json.loads((D/'depth260.json').read_text())['pairs'] if r['build']!='Feminine' or r['hair'] not in ['straight','side-sweep']];assemblies=json.loads((P/'assemblies260.json').read_text())")
s=s.replace(" build,style=key.split('-',1);"," if key not in ['Feminine-straight','Feminine-side-sweep']:continue\n build,style=key.split('-',1);")
(P/'reference-patch260.py').write_text(s,encoding='utf8',newline='\n')
s=(P/'browser260.cjs').read_text(encoding='utf8').replace("groups={Masculine:['afro','flow','locs','middle-part'],Feminine:['straight','side-sweep','box-braids']}","groups={Feminine:['straight','side-sweep']}")
s=s.replace("browser-export","browser-patch").replace("(pub?'public260':verify?'browser-verify260':'browser260')","'browser-patch260'")
(P/'browser-patch260.cjs').write_text(s,encoding='utf8',newline='\n');print('PATCH_RECIPES260_READY')
