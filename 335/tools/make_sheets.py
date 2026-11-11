"""Contact sheets for visual review of the exported bob components."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import argparse
from PIL import Image,ImageDraw,ImageFont

OUT=Path('D:/Ravedio-Avatar-Work/native335')
HATS=('none','cap','beanie','bucket','cowboy','ears','headband','pashmina')
COLORS=('default','black','auburn','blonde','platinum','pink','purple','ombre')
ANGLES=('front','threequarter','profile','rightprofile','rear','rearquarter','above','underneath')


def sheet(path,rows,size=250):
    canvas=Image.new('RGB',(max(map(len,rows))*size,len(rows)*(size+25)),'#F1F4FA')
    draw=ImageDraw.Draw(canvas);font=ImageFont.load_default(size=13)
    for row,items in enumerate(rows):
        for col,(label,name) in enumerate(items):
            x,y=col*size,row*(size+25)
            draw.text((x+8,y+4),label,fill='#24313e',font=font)
            with Image.open(OUT/'review'/f'{name}.png') as source:
                picture=source.convert('RGBA').resize((size,size),Image.Resampling.LANCZOS)
            canvas.paste(picture,(x,y+25),picture)
    canvas.save(path,quality=94)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--quick',action='store_true')
    args=parser.parse_args()
    if args.quick:
        for color in ('default','ombre'):
            for group in range(2):
                sheet(OUT/f'quick-{color}-{group}.jpg',[
                    [(hat+' / '+angle,f'{hat}-{color}-{angle}') for angle in ('threequarter','profile','rearquarter')]
                    for hat in HATS[group*4:group*4+4]],275)
        return
    sheet(OUT/'angles.jpg',[[(angle,f'none-default-{angle}') for angle in ANGLES[i:i+4]] for i in (0,4)],275)
    for color,file in (('default','headwear.jpg'),('ombre','ombre.jpg')):
        sheet(OUT/file,[[(hat,f'{hat}-{color}-{angle}') for hat in HATS] for angle in ('threequarter','rearquarter')],250)
    sheet(OUT/'colors.jpg',[[(color,f'none-{color}-{angle}') for color in COLORS] for angle in ('threequarter','rear')],250)
    checks=OUT/'checks';checks.mkdir(exist_ok=True)
    for hat in HATS:
        for color in COLORS:
            sheet(checks/f'{hat}-{color}.jpg',[
                [(angle,f'{hat}-{color}-{angle}') for angle in ANGLES[i:i+4]] for i in (0,4)],260)
    tops=('bandeau','jersey','open','strappy','sweatshirt','tank','triangle','tshirt')
    for hat in ('none','pashmina'):
        sheet(OUT/f'wardrobe-{hat}.jpg',[
            [(top+' / '+angle,f'{top}-{hat}-default-{angle}') for angle in ('front','profile','rear','underneath')]
            for top in tops],240)
    sheet(OUT/'deep-colors.jpg',[
        [(color,f'deep-none-{color}-{angle}') for color in COLORS]
        for angle in ('threequarter','rearquarter')],250)


if __name__=='__main__':main()
