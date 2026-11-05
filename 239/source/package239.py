from pathlib import Path
import json,shutil,re
P=Path(__file__).parent;R=P.parent/'floating138/mobile-preview';D=R/'239';OLD=R/'238'
for folder in ['','components','references','assemblies','source']:(D/folder).mkdir(exist_ok=True)
def remap(obj):
    if isinstance(obj,dict):return {k:remap(v) for k,v in obj.items()}
    if isinstance(obj,list):return [remap(v) for v in obj]
    if isinstance(obj,str) and obj.startswith('components/'):return '../238/'+obj
    return obj
c=remap(json.loads((OLD/'catalogue238.json').read_text()));fits=json.loads((P/'fits239.json').read_text())
c['previousPashminaTops']=c['pashminaTops'];c['pashminaTops']={};c['previousPashminaFits']={key:dict(pairs['pashmina']) for key,pairs in c['fits'].items()}
for build,tops in fits.items():
    c['pashminaTops'][build]={}
    for top,item in tops.items():
        shutil.copy2(P/item['component'],D/item['component']);c['pashminaTops'][build][top]=item['component']
    for key,pairs in c['fits'].items():
        if key.startswith(build+'-'):pairs['pashmina']['headgear']=c['pashminaTops'][build]['open' if build=='Feminine' else 'tank']
(D/'catalogue239.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf8',newline='\n')
viewer=(OLD/'viewer238.js').read_text().replace('238','239')
viewer=re.sub(r"Updating selected feature[^']*",'Updating selected feature...',viewer)
(D/'viewer239.js').write_text(viewer,encoding='utf8',newline='\n')
html=(OLD/'index.html').read_text().replace('238','239').replace('Compare237 pashmina','Compare238 pashmina')
html=html.replace('Repaired joins between the hood and neck folds. Compare237 keeps the same outfit and view.','Rounded inner neck corners joining the hood into both crossed ends. Compare238 keeps the same outfit and view.')
html=html.replace('<a href="../237/">Previous237</a>','<a href="../238/">Previous238</a>')
html=html.replace('Matched Blender crops:237 on the left,239 on the right.','Matched Blender crops:238 on the left,239 on the right.')
html=html.replace('Neck joins · close comparison','Inner corners - close comparison')
# Normalize inherited broken punctuation in review-only copy.
html=html.replace('Ravedio Ãƒâ€šÃ‚Â·','Ravedio -').replace('AVATAR REVIEW Ãƒâ€šÃ‚Â·','AVATAR REVIEW -').replace('No nose Ãƒâ€šÃ‚Â·','No nose /').replace('Final export references Ã‚Â·','Final export references -').replace('LoadingÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¦','Loading...')
html=re.sub(r'<title>.*?</title>','<title>Ravedio - 239</title>',html)
html=re.sub(r'<div class="eyebrow">.*?</div>','<div class="eyebrow">AVATAR REVIEW - 239</div>',html)
html=re.sub(r'No nose [^<]*Regular smile','No nose / Regular smile',html)
html=re.sub(r'<summary>Final export references[^<]*</summary>','<summary>Final export references - seven angles</summary>',html)
html=re.sub(r'(<p id="status" role="status">).*?(</p>)',r'\1Loading...\2',html)
(D/'index.html').write_text(html,encoding='utf8',newline='\n')
for name in ['scarf239.py','joined239.py','verify239.py','package239.py','browser239.cjs','close239.cjs']:
    if (P/name).exists():shutil.copy2(P/name,D/'source'/name)
print('PACKAGED239',sum(len(v) for v in fits.values()),'joined wrap fits')
