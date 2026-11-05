from pathlib import Path
exec((Path(__file__).parent/'boards262.py').read_text(encoding='utf-8-sig').replace("print('BOARDS262_COMPLETE')",''))
C=json.loads((D/'catalogue262.json').read_text())
for b in C['builds']:
 for a in ['front','profile','rearquarter']:
  board(b+'-headgear-glasses-'+a+'262.jpg',[(P/'final-accessories'/f'{b}-{hat}-{g}-{a}.png',hat+' / '+g) for hat in C['headwear'] for g in C['glasses']],cols=8,w=170,h=190)
 board(b+'-hair-sprout262.jpg',[(P/'final-accessories'/f'{b}-{st}-{hat}-sprout.png',st+' / '+hat)for st in C['builds'][b]['hair']for hat in ['none','cap','beanie','headband','pashmina']],cols=5,w=220,h=245)
 board(b+'-hair-sport262.jpg',[(P/'final-accessories'/f'{b}-{st}-{hat}-sport.png',st+' / '+hat)for st in C['builds'][b]['hair']for hat in ['cap','beanie','pashmina']],cols=3,w=250,h=275)
 # Exact pixel outputs are placed at native size; 32px stress detail is separately enlarged by nearest-neighbor.
 im=Image.new('RGB',(590,16*150+30),BG);dr=ImageDraw.Draw(im);dr.text((8,4),'Chat portraits: actual32 /48 /64 /120px +32px enlarged4x',fill='white')
 for row,(eye,skin) in enumerate((e,k)for e in ['original','tapered','hooded','bean']for k in range(4)):
  y=30+row*150;dr.text((6,y),f'{eye} / skin{skin}',fill='white')
  for x,size in zip([6,58,126,210],[32,48,64,120]):
   f=P/'final-small'/f'{b}-{eye}-skin{skin}-{size}.png';pic=Image.open(f).convert('RGBA');assert pic.size==(size,size),(f,pic.size);bg=Image.new('RGBA',pic.size,BG);bg.alpha_composite(pic);im.paste(bg.convert('RGB'),(x,y+18))
  im.paste(Image.open(P/'final-small'/f'{b}-{eye}-skin{skin}-32.png').convert('RGB').resize((128,128),Image.Resampling.NEAREST),(365,y+18))
 im.save(out/(b+'-chat-small262.jpg'),quality=97)
if (P/'groom-contacts/stubble-none-front.png').exists():
 board('groom-contacts262.jpg',[(P/'groom-contacts'/f'{g}-{hat}-{a}.png',g+' / '+hat+' / '+a)for g in C['builds']['Masculine']['grooms']for hat in ['none','cap','pashmina']for a in ['front','profile','rearquarter']],cols=3,w=230,h=255)
print('EXTRA_BOARDS262_COMPLETE')
