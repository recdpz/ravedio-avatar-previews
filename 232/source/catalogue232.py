from pathlib import Path
import json,shutil
P=Path(__file__).parent;R=P.parent/'floating138/mobile-preview';D=R/'232';D.mkdir(exist_ok=True)
old=json.loads((R/'224/looks224.json').read_text());new=json.loads((R/'227/looks227.json').read_text());fits=json.loads((R/'227/fits227.json').read_text())
def asset(path):
 assert (D/path).is_file(),path
 return path
def option(label,path,**kw):return dict(label=label,path=asset(path) if path else None,**kw)
cat={'builds':{},'headwear':{},'glasses':{},'details':{},'fits':{},'colors':{}}
tops={'Feminine':[('bandeau','Pasties',213),('triangle','Triangle top',214),('strappy','Strappy crop',213),('tshirt','T-shirt',214),('jersey','Jersey',213),('open','Button-up',215),('tank','Tank',213),('sweatshirt','Hoodie',215)],'Masculine':[('shirtless','Shirtless',None),('tank','Tank',208),('tshirt','T-shirt',203),('jersey','Jersey',203),('buttonup','Button-up',208),('sweatshirt','Hoodie',215)]}
hairIDs={'Feminine':['bob','ponytail','straight','curls','side-sweep','space-buns','twin-braids','box-braids'],'Masculine':['sidepart','taper','buzz','curly-top','afro','flow','locs']}
for b,case in [('Feminine','Feminine-uncovered'),('Masculine','Masculine-taper')]:
 parts=old[case]['components'];entry={'base':asset('../224/'+parts['base']),'hair':{},'tops':{},'bottoms':{},'eyes':{},'mouths':{},'noses':{},'grooms':{}}
 if b=='Masculine':entry['shirtlessBase']=asset('../208/Masculine-shirtless-base.glb')
 for h in hairIDs[b]:
  k=b+'-'+h
  if k in new:path='../227/'+new[k]['components']['hair'];note=new[k]['note']
  elif h in ['ponytail','taper']:path='../224/'+parts['hair'];note='Retained224 selected hairstyle.'
  else:path=f'../208/{b}-hair.glb';note='Existing developed cartoon hairstyle.'
  entry['hair'][h]=option({'bob':'Bob','sidepart':'Side part','side-sweep':'Side sweep','curly-top':'Curly top','space-buns':'Space buns','twin-braids':'Twin braids','box-braids':'Box braids'}.get(h,h.capitalize()),path,note=note)
 for id,label,rev in tops[b]:entry['tops'][id]=option(label,f'../{rev}/{b}-{id}-top.glb' if rev else None)
 for id in (['shorts','skirt','bikini','pants'] if b=='Feminine' else ['shorts','pants']):entry['bottoms'][id]=option('Bikini bottoms' if id=='bikini' else id.capitalize(),f'../{216 if b=="Feminine" and id!="bikini" else 215}/{b}-{id}-bottom.glb')
 for id,label in [('original','Original'),('almond','Almond'),('squint','Curved squint')]:entry['eyes'][id]=option(label,f'components/{b}-eyes-squint.glb' if id=='squint' else f'../{192 if id=="almond" else 181}/{b}-eyes-{id}.glb')
 for id,label in [('tapered','Tapered oval'),('hooded','Soft hooded'),('bean','Rounded bean')]:entry['eyes'][id]=option(label,f'components/{b}-eyes-{id}.glb')
 for id,label in [('none','None'),('line','Smile'),('smile','Open smile'),('lips','Closed mouth')]:entry['mouths'][id]=option(label,None if id=='none' else f'../209/{b}-mouth-{id}.glb')
 entry['noses']={'none':option('None',None),'rounded':option('Rounded',f'../190/{b}-nose-rounded.glb')}
 entry['grooms']['none']=option('None',None)
 if b=='Masculine':
  for id,label in [('stubble','Stubble'),('mustache','Mustache'),('patch','Mustache + patch'),('goatee','Goatee'),('short','Short beard'),('long','Long beard')]:entry['grooms'][id]=option(label,f'../{209 if id=="stubble" else 208}/Masculine-groom-{id}.glb')
 cat['builds'][b]=entry
cat['headwear']['none']=option('None',None)
cat['headwear']['cap']=option('Cap',None)
for id in ['beanie','bucket','cowboy','headband','ears','pashmina']:cat['headwear'][id]=option({'bucket':'Bucket hat','cowboy':'Cowboy hat','ears':'Animal ears'}.get(id,id.capitalize()),'../227/'+new['Feminine-'+id]['components']['headgear'])
cat['glasses']['none']=option('None',None)
cat['glasses']['rectangular']=option('Rectangular',None)
for id in ['reading','wayfarer','cat-eye','heart','wraparound','kaleidoscope']:
 c=new['Feminine-'+id]['components'];cat['glasses'][id]=option({'cat-eye':'Cat eye','kaleidoscope':'Faceted frames','wraparound':'Sport'}.get(id,id.capitalize()),'../227/'+c['glasses'],lenses=asset('../227/'+c['lenses']))
cat['details']={'none':option('None',None),'hot':option('HOT sticker',None)}
for id in ['sprout','gems']:cat['details'][id]=option('Face gems' if id=='gems' else 'Sprout','../227/'+new['Feminine-'+id]['components']['extra'])
for b in cat['builds']:
 detail='Feminine-details' if b=='Feminine' else 'Masculine-details'
 cat['builds'][b]['rectangular']={g:asset('../224/'+old[detail]['components'][g]) for g in ['glasses','lenses']}
 cat['builds'][b]['hot']=asset('../212/'+b+'-extra.glb')
 for h in cat['builds'][b]['hair']:
  key=b+'-'+h;valid={}
  for hat in cat['headwear']:
   fk=key+'--'+hat
   if fk in fits:
    parts=fits[fk]['components'];valid[hat]={g:asset('../227/'+parts[g]) for g in ['hair','headgear']}
  if h in ['ponytail','taper']:
   capcase='Feminine-cap' if b=='Feminine' else 'Masculine-details';valid['cap']={g:asset('../224/'+old[capcase]['components'][g]) for g in ['hair','headgear']}
  if h in ['bob','sidepart']:valid['cap']={'hair':asset(f'../213/{b}-{h}-cap-hair.glb'),'headgear':asset('../224/'+old[detail]['components']['headgear'])}
  cat['fits'][key]=valid
cat['colors']['top']=[['default','Default',None],['black','Black','#24252C'],['white','White','#EBE8E3'],['blue','Blue','#366EBA'],['teal','Teal','#368F91'],['purple','Purple','#8C62BD'],['pink','Pink','#D57FA9'],['red','Red','#C3485C'],['lime','Lime','#A6BB57']]
cat['colors']['bottom']=[['default','Default',None],['black','Black','#22242A'],['white','White','#EAE8E3'],['gray','Gray','#85878C'],['navy','Navy','#25354F'],['blue','Blue','#3C6A9C'],['khaki','Khaki','#B7A17A'],['red','Red','#B83546'],['pink','Pink','#D46D9C']]
cat['colors']['hair']=[['default','Default',None],['black','Black','#28232A'],['brown','Brown','#68402C'],['darkbrown','Dark brown','#39251E'],['auburn','Auburn','#984A30'],['blonde','Blonde','#B78F51'],['platinum','Platinum','#CCC2B0'],['pink','Pink','#B75C88'],['purple','Purple','#725887']]
cat['colors']['headgear']=cat['colors']['bottom']
(D/'catalogue232.json').write_text(json.dumps(cat,indent=2)+'\n')
shutil.copy2(P.parent/'refinement209/face-palette209.json',D/'face-palette209.json')
print('CATALOGUE232',sum(len(x['hair']) for x in cat['builds'].values()),'hairstyles; independent wardrobe and face controls restored')
