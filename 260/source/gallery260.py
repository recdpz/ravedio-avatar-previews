from pathlib import Path
from PIL import Image,ImageDraw,ImageOps
import json,sys
P=Path(__file__).parent;D=P.parent/'floating138/mobile-preview/260';selected=json.loads((P/'selected260.json').read_text())
def paste(im,f,x,y,w,h):
 pic=Image.open(f).convert('RGBA');bg=Image.new('RGBA',pic.size,'#29394c');bg.alpha_composite(pic);pic=ImageOps.contain(bg.convert('RGB'),(w,h));im.paste(pic,(x+(w-pic.width)//2,y))
angles=['front','threequarter','profile','rightprofile','rear','rearquarter','top','underside'];S=P/('browser-export' if '--initial' in sys.argv else 'browser-release2')
for key in selected:
 im=Image.new('RGB',(1200,600),'#29394c');dr=ImageDraw.Draw(im)
 for i,a in enumerate(angles):x=i%4*300;y=i//4*300;paste(im,S/f'{key}-none-{a}.png',x,y,300,275);dr.text((x+5,y+279),a,fill='white')
 im.save(D/'references'/f'{key}-angles260.jpg',quality=94)
 im=Image.new('RGB',(1200,600),'#29394c');dr=ImageDraw.Draw(im)
 for i,(kind,a) in enumerate((kind,a) for kind in ['before','none'] for a in ['front','profile','rightprofile','rear']):x=i%4*300;y=i//4*300;paste(im,S/f'{key}-{kind}-{a}.png',x,y,300,275);dr.text((x+5,y+279),('259' if kind=='before' else '260')+' / '+a,fill='white')
 im.save(D/'references'/f'{key}-comparison260.jpg',quality=94)
 im=Image.new('RGB',(1200,4350),'#29394c');dr=ImageDraw.Draw(im)
 for i,(hat,a) in enumerate((hat,a) for hat in ['cap','beanie','bucket','cowboy','headband','ears','pashmina'] for a in angles):x=i%4*300;y=i//4*300;paste(im,S/f'{key}-{hat}-{a}.png',x,y,300,275);dr.text((x+5,y+279),hat+' / '+a,fill='white')
 for i,a in enumerate(['front','rear']):paste(im,S/f'{key}-hidden-{a}.png',i*300,4200,300,140);dr.text((i*300+5,4337),'Cloth off / '+a,fill='white')
 im.save(D/'references'/f'{key}-covered260.jpg',quality=92)
im=Image.new('RGB',(1000,7*250),'#29394c');dr=ImageDraw.Draw(im)
for j,key in enumerate(selected):
 for i,col in enumerate(['default','black','blonde','ombre']):f=S/(f'{key}-none-threequarter.png' if col=='default' else f'{key}-{col}-none.png');paste(im,f,i*250,j*250,250,225);dr.text((i*250+3,j*250+229),key+' / '+col,fill='white')
im.save(D/'references/colors260.jpg',quality=94)
im=Image.new('RGB',(7*180,340),'#29394c');dr=ImageDraw.Draw(im)
for j,key in enumerate(selected):
 for i,skin in enumerate(['0','3']):paste(im,S/f'{key}-small120-{skin}.png',j*180,i*170,120,120);dr.text((j*180+3,i*170+125),key,fill='white')
im.save(D/'references/small260.jpg',quality=95)

print('GALLERY260_COMPLETE')
