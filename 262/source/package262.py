from pathlib import Path
import json,copy,shutil,re
P=Path('E:/Ravedio-Avatar/catalogue262');R=P.parent/'floating138/mobile-preview';OLD=R/'261';D=R/'262'
for sub in ['components','references','source','assemblies']:(D/sub).mkdir(parents=True,exist_ok=True)
def rebase(x):
 if isinstance(x,dict):return {('../261/'+k if k.startswith('components/') else k):rebase(v) for k,v in x.items()}
 if isinstance(x,list):return [rebase(v) for v in x]
 if isinstance(x,str) and x.startswith('components/'):return '../261/'+x
 return x
c=rebase(json.loads((OLD/'catalogue261.json').read_text()));c.pop('before260',None);c['before261']={k:copy.deepcopy(c[k]) for k in ['builds','fits','sprouts','pashminaVariants','pashminaHairFamilies','braidLengths','ombre','colors']}
trial=json.loads((P/'pass3/catalogue261.json').read_text());selected={}
for b,bc in c['builds'].items():
 bc['eyes']={k:v for k,v in bc['eyes'].items() if k in ['original','tapered','hooded','bean']}
 if 'lashes'in bc:bc['lashes']={k:v for k,v in bc['lashes'].items() if k in bc['eyes']}
 bc['pantsBases']={}
 for kind,path in trial['builds'][b]['pantsBases'].items():
  name=path.replace('fix262-','');shutil.copy2(P/'pass3/components'/path,D/'components'/name);bc['pantsBases'][kind]='components/'+name
 for top,r in trial['builds'][b]['tops'].items():
  if r['path'] and r['path'].startswith('fix262-'):
   name=r['path'].replace('fix262-','');name=name.replace('sweatshirt','hoodie');shutil.copy2(P/'pass3/components'/r['path'],D/'components'/name);bc['tops'][top]['path']='components/'+name;selected[b+'-'+top]=bc['tops'][top]['path']
for key in ['top','bottom','hair','headgear']:
 c['colors'][key][0][1]='Original (review)'
for row in c['colors']['hair']:
 if row[0]=='darkbrown':row[1]='Brown'
c['colorAliases']={'hair':{'Feminine':'darkbrown','Masculine':'darkbrown'},'top':{'Feminine':{'bandeau':'black','triangle':'teal','strappy':'pink','tshirt':'teal','jersey':'black','open':'purple','tank':'teal','sweatshirt':'purple'},'Masculine':{'shirtless':None,'tank':'teal','tshirt':'teal','jersey':'black','buttonup':'blue','sweatshirt':'purple'}},'bottom':{'Feminine':{k:'black' for k in c['builds']['Feminine']['bottoms']},'Masculine':{k:'black' for k in c['builds']['Masculine']['bottoms']}},'headgear':{b:{'none':None,'cap':'red' if b=='Feminine' else 'navy','beanie':'blue','bucket':'gray','cowboy':'khaki','headband':'black','ears':'gray','pashmina':'black'} for b in c['builds']}}
c['catalogueDecisions']={'status':'Owner-directed artwork catalogue; no wire IDs or encoders changed','eyes':['original','tapered','hooded','bean'],'retired_review_eyes':{'almond':'tapered','squint':'hooded'},'canonical_colors':{k:[r[0] for r in c['colors'][k] if r[0]!='default'] for k in ['hair','top','bottom','headgear']},'default_rule':'Original (review) is a source-color preset, not a ninth color. It resolves to the contextual authored palette entry. Selecting that entry retains the original fabric/hair material variation rather than flattening it to one HEX.','brown':'Brown uses authored brown materials; the redundant darker-brown review treatment is retired with261.','lens_rule':'Dark by default except Reading clear; alternative lens preview and lash hiding are review controls, not new profile bits.'}
(D/'catalogue262.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf8');(P/'selected262.json').write_text(json.dumps(selected,indent=2))
s=(OLD/'viewer261.js').read_text().replace('261','262').replace('before260','before261')
s=s.replace("const s={...defaults(b),...raw};", "const s={...defaults(b),...raw};if(catalogue.catalogueDecisions.retired_review_eyes[s.eyes])s.eyes=catalogue.catalogueDecisions.retired_review_eyes[s.eyes];")
s=s.replace("['original','almond','tapered','hooded','bean','squint']", "['original','tapered','hooded','bean']")
s=s.replace("if(b==='Feminine'&&showLashes)","if(s.bottom==='pants'&&c.pantsBases)p.base=c.pantsBases[s.top==='shirtless'?'shirtless':'clothed'];if(b==='Feminine'&&showLashes)",1)
s=s.replace("const old=catalogue.before261;p.hair=", "const old=catalogue.before261,oc=old.builds[b];p.base=s.top==='shirtless'?oc.shirtlessBase:oc.base;p.top=oc.tops[s.top].path;p.bottom=oc.bottoms[s.bottom].path;p.hair=")
# Contextual authored colors make the review preset and canonical entry exact aliases.
insert="function authoredKey(role,s){const m=catalogue.colorAliases[role]?.[build];return role==='hair'?m:m?.[role==='top'?s.top:role==='bottom'?s.bottom:s.headwear]}\nfunction tint(role,id,s){return id==='default'||id===authoredKey(role,s)?null:pick(role,id)}\n"
s=s.replace('async function colors(target,s){',insert+'async function colors(target,s){')
s=s.replace("pick('hair',s.hairColor),hat=pick('headgear',s.headgearColor),top=pick('top',s.topColor),bottom=pick('bottom',s.bottomColor)","tint('hair',s.hairColor,s),hat=tint('headgear',s.headgearColor,s),top=tint('top',s.topColor,s),bottom=tint('bottom',s.bottomColor,s)")
s=s.replace("span=(mode==='face'?1.5:2.7)/zoom,y=mode==='face'?1.88:1.28", "span=(mode==='chat'?(choices().headwear==='cowboy'?1.75:1.35):mode==='face'?1.5:2.7)/zoom,y=mode==='chat'?1.90:mode==='face'?1.88:1.28")
s=s.replace("['face','body']","['face','chat','body']")
s=s.replace("const arm=/swept.*arm/i.test(o.name),sleeve=o.name.startsWith('Sleeve');", "const arm=/swept.*arm/i.test(o.name),sleeve=o.name.startsWith('Sleeve')||o.userData.partRole262==='sleeve';")
(D/'viewer262.js').write_text(s,encoding='utf8')
s=(OLD/'index.html').read_text().replace('261','262').replace('Compare260','Compare261');s=re.sub('<h1>.*?</h1><p>.*?</p>','<h1>Wardrobe and accessory finishing</h1><p>Pants assembly, seated hood folds and clean top edges. Four final eye shapes, explicit color aliases, and chat-portrait framing. Compare261 shows the previous geometry with the other selections retained.</p>',s,count=1)
s=s.replace('<button id="body"','<button id="chat" aria-pressed="false">Chat portrait</button><button id="body"',1)
for k in ['almond','squint']:s=re.sub(r'<figure><img id="compare-'+k+r'".*?</figure>','',s,flags=re.S);s=re.sub(r'<button[^>]*data-eye="'+k+r'".*?</button>','',s,flags=re.S)
a=s.index('<details open><summary>Exported angle checks');z=s.index('<details><summary>Matched face references',a)
s=s[:a]+'<details open><summary>Wardrobe, accessories and small portraits</summary><p>Final comparison boards and handoff are being prepared.</p></details>'+s[z:]
s=re.sub(r'<nav>.*?</nav>','<nav><a href="README262.txt">Handoff</a><a href="../261/">Previous261</a></nav>',s,flags=re.S);(D/'index.html').write_text(s,encoding='utf8');(D/'README262.txt').write_text('Ravedio262 - Wardrobe and accessory finishing. Local candidate; final checks pending.\n',encoding='utf8')
(P/'catalogue-decisions262.json').write_text(json.dumps(c['catalogueDecisions'],indent=2));print('PACKAGE262_COMPLETE',len(selected))
