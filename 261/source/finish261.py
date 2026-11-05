from pathlib import Path
import json,shutil,ast
from PIL import Image,ImageOps,ImageDraw
P=Path(__file__).parent;R=P.parent/'floating138/mobile-preview';D=R/'261';S=P/'browser-release';selected=json.loads((P/'selected261.json').read_text());c=json.loads((D/'catalogue261.json').read_text());browser=json.loads((P/'browser261.json').read_text());assert not browser['errors'] and not browser['http'];patch=json.loads((P/'browser-female5261.json').read_text());flow=json.loads((P/'browser-flow-final261.json').read_text());assert not flow['errors'] and not flow['http'];browser['checks']=[r for r in browser['checks'] if not(r[:2]==['Masculine','flow'])]+flow['checks'];assert not patch['errors'] and not patch['http'];browser['checks']=[r for r in browser['checks'] if r[-1]!='prior completed capture/checkpoint']+patch['checks'];browser['final_female_pass5']=patch;browser['initial_completed_batch']=json.loads((P/'capture-batch1.json').read_text())
angles=['front','threequarter','profile','rightprofile','rear','rearquarter','top','underside']
def paste(im,f,x,y,w,h):
 pic=Image.open(f).convert('RGBA');bg=Image.new('RGBA',pic.size,'#29394c');bg.alpha_composite(pic);pic=ImageOps.contain(bg.convert('RGB'),(w,h));im.paste(pic,(x+(w-pic.width)//2,y))
for key in selected:
 im=Image.new('RGB',(1200,600),'#29394c');d=ImageDraw.Draw(im)
 for i,a in enumerate(angles):x=i%4*300;y=i//4*300;paste(im,S/f'{key}-none-{a}.png',x,y,300,275);d.text((x+5,y+279),a,fill='white')
 im.save(D/'references'/f'{key}-angles261.jpg',quality=94)
 im=Image.new('RGB',(1200,600),'#29394c');d=ImageDraw.Draw(im)
 for i,(kind,a) in enumerate((kind,a) for kind in ['before','none'] for a in ['front','profile','rightprofile','rear']):x=i%4*300;y=i//4*300;paste(im,S/f'{key}-{kind}-{a}.png',x,y,300,275);d.text((x+5,y+279),('260' if kind=='before' else '261')+' / '+a,fill='white')
 im.save(D/'references'/f'{key}-comparison261.jpg',quality=94)
 im=Image.new('RGB',(1200,4350),'#29394c');d=ImageDraw.Draw(im)
 for i,(hat,a) in enumerate((hat,a) for hat in ['cap','beanie','bucket','cowboy','headband','ears','pashmina'] for a in angles):x=i%4*300;y=i//4*300;paste(im,S/f'{key}-{hat}-{a}.png',x,y,300,275);d.text((x+5,y+279),hat+' / '+a,fill='white')
 for i,a in enumerate(['front','rear']):paste(im,S/f'{key}-hidden-{a}.png',i*300,4200,300,140);d.text((i*300+5,4337),'Cloth off / '+a,fill='white')
 im.save(D/'references'/f'{key}-covered261.jpg',quality=92)
keys=[b+'-'+st for b,bc in c['builds'].items() for st in bc['hair']]
for b in c['builds']:
 bk=[k for k in keys if k.startswith(b+'-')];im=Image.new('RGB',(1500,2400),'#29394c');d=ImageDraw.Draw(im)
 for row,key in enumerate(bk):
  for col,a in enumerate(['front','profile','rightprofile','rear','top']):paste(im,S/f'{key}-none-{a}.png',col*300,row*300,300,275);d.text((col*300+4,row*300+279),key+' / '+a,fill='white')
 im.save(D/'references'/f'{b}-all-styles261.jpg',quality=92)
im=Image.new('RGB',(1000,len(keys)*250),'#29394c');d=ImageDraw.Draw(im)
for j,key in enumerate(keys):
 for i,col in enumerate(['default','black','blonde','ombre']):f=S/(f'{key}-none-threequarter.png' if col=='default' else f'{key}-{col}-none.png');paste(im,f,i*250,j*250,250,225);d.text((i*250+3,j*250+229),key+' / '+col,fill='white')
im.save(D/'references/colors261.jpg',quality=92)
im=Image.new('RGB',(8*180,4*160),'#29394c');d=ImageDraw.Draw(im)
for j,key in enumerate(keys):
 for i,skin in enumerate(['0','3']):x=(j%8)*180;y=(j//8)*320+i*160;paste(im,S/f'{key}-small120-{skin}.png',x,y,120,120);d.text((x+3,y+125),key,fill='white')
im.save(D/'references/small261.jpg',quality=95)
im=Image.new('RGB',(1200,4*320),'#29394c');d=ImageDraw.Draw(im)
for i,key in enumerate(['Feminine-side-sweep','Feminine-straight','Feminine-curls','Feminine-bob']):
 for j,kind in enumerate(['before','none']):
  pic=Image.open(S/f'{key}-{kind}-front.png').convert('RGBA');bg=Image.new('RGBA',pic.size,'#29394c');bg.alpha_composite(pic);bg=ImageOps.fit(bg.convert('RGB'),(600,600));im.paste(bg.crop((0,35,600,335)),(j*600,i*320+20));d.text((j*600+5,i*320+3),key+' / '+('260' if kind=='before' else '261'),fill='white')
im.save(D/'references/hairline-closeups261.jpg',quality=95)
# All source manifests/packed scenes are independent from previous reviews.
assemblies=json.loads((P/'assemblies261.json').read_text());assert len(assemblies)==6
for r in assemblies.values():shutil.copy2(r['source'],D/r['packed_path'])
files=list(S.glob('*.png'));images=len(files);assert images>=900,images
review={'revision':261,'status':'New corrections pending owner review','styles_audited':16,'bare_and_headwear_selections':128,'geometry_unique_files':121,'actual_exported_images':images,'checks':len(browser['checks']),'prior_unchanged_styles_checks':44,'second_pass':'Rear scalp gaps caught in exported review: extend the recessed coverage while retaining curl/lock geometry and a low edge. Source, silhouette and root close-ups; actual GLB bare/worn color and small portraits. Isolated Curls export exposed a residual support wedge; fourth pass removes it. Fifth pass extends the recessed rear coverage; rejected Flow bridge removed after a raised nub was spotted.','not_a_perfection_claim':'Retained styles had no confirmed related defect in this audit. Native/phone qualification is separate.'}
finalfits=json.loads((P/'fits/fits261.json').read_text());finalfits.update(json.loads((P/'fits-curls4/fits261.json').read_text()));finalfits.update(json.loads((P/'fits-female5/fits261.json').read_text()));finalfits.update(json.loads((P/'fits-flow-final/fits261.json').read_text()))
for name,data in [('review261.json',review),('findings261.json',json.loads((P/'findings261.json').read_text())),('technical261.json',json.loads((P/'technical261.json').read_text())),('dependencies261.json',json.loads((P/'dependencies261.json').read_text())),('assemblies261.json',assemblies),('selected-settings261.json',selected),('fits261.json',finalfits),('ombre261.json',json.loads((P/'ombre261.json').read_text())),('browser261.json',browser),('geometry-audit-before261.json',json.loads((P/'geometry-audit-before.json').read_text()))]:
 (D/name).write_text(json.dumps(data,indent=2)+'\n',encoding='utf8')
for name in ['repair261.py','repair-curls261.py','flow-junction261.py','curl-coverage261.py','rear-coverage261.py','fits-flow-final261.py','reference-flow-final261.py','browser-flow-final261.cjs','fits-female5261.py','reference-female5261.py','browser-female5261.cjs','fits261.py','fits-curls261.py','package261.py','package-fits261.py','ombre261.py','audit261.cjs','browser261.cjs','reference261.py','reference-curls261.py','technical261.py','finish261.py','plan261.json']:
 f=P/name
 if f.suffix=='.py':ast.parse(f.read_text(encoding='utf-8-sig'))
 shutil.copy2(f,D/'source'/name)
hand={'revision':261,'baseline_commit':'b40c9c9de2875054e9400d6af8b76771402860da','scope':'Hair construction cleanup; no profile/wire/product code changes','corrected_styles':list(selected),'retained_styles':json.loads((P/'findings261.json').read_text())['retained_after_bare_visual_review'],'components':'144 ordinary GLBs:48 corrected hair,48 matching Ombré,48 seated sprouts. Six packed final-GLB assemblies and24 matched color/32-bit-Z references.','coordinates':'Shared coordinates unchanged; hair/headwear/clothes/lenses/frames remain independent; existing colors retained.','fit_strategy':'Retained headgear geometry; proportional compression for closed hats, existing authored root seating for bandanas/pashminas; reviewed actual exports.','rendering':'Material/COLOR_0 opacity remains distinct from transmission. No compression or quantization added. Preserve ordinary GLBs for native and offline bakers.','depth':'Color and depth regenerated together from final geometry, same camera, at120/512. Previous depth fixtures are not reused for these changed assemblies.','blender_transfer':'Packed scenes retain the reference studio and color management. Procedural bump/normal effects, environment, view transform and some shader responses require explicit native matching; GLB alone is not the complete Blender appearance.','qualification':'Source/export validation; native renderer and phone performance remain separate.','comparison':'Compare260 keeps matching prior hair and the other selected components, including separate Twin braid lengths.'}
(D/'handoff261.json').write_text(json.dumps(hand,indent=2)+'\n',encoding='utf8')
(D/'README261.txt').write_text('Ravedio261 - Hair geometry cleanup\n\nAll sixteen styles audited for exposed support, jagged boundaries, deformed sections, gaps and headwear intersections. Targeted changes: Bob/Straight/Side sweep/Curls recessed roots; Curls complete side cross-sections and rear coverage beneath long locks; Flow/Middle part root coverage. The ten other bare styles retain their exact assets. Twin braid lengths now remain present in Compare260.\n\n144 ordinary GLBs, six packed assembled sources,24 matched color/depth pairs. Independent feature/color controls, shared transforms, fixed studio, zoom and rotation retained. Use Compare260 and the close-up comparisons.\n\nNew corrections await owner review. This is source/export artwork verification, not native/phone performance qualification. See findings261.json, technical261.json, assemblies261.json, depth261.json and handoff261.json.\n',encoding='utf8')
s=(D/'index.html').read_text();insert='<details><summary>All sixteen audited styles and hairline close-ups</summary><div class="shape-grid">'
for f in ['Feminine-all-styles261.jpg','Masculine-all-styles261.jpg','hairline-closeups261.jpg']:insert+=f'<figure><a href="references/{f}"><img src="references/{f}" loading="lazy" alt="{f}"></a></figure>'
insert+='</div></details>';s=s.replace('</nav>', '</nav>'+insert,1);(D/'index.html').write_text(s,encoding='utf8');print('FINISH261_COMPLETE',images,len(browser['checks']))
