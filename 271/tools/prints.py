"""Draw the bandana prints at their native UV resolution (Pillow)."""
from pathlib import Path
import math

from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parents[1] / "assets"
BG = (37, 40, 46)
INK = (177, 173, 159)
SOFT = (151, 150, 141)


def curve(points, n=17):
    result = []
    p = points[0]
    for a, b, c in zip(points[1::3], points[2::3], points[3::3]):
        for i in range(n):
            t = i / n
            s = 1 - t
            result.append(tuple(s**3*x + 3*s*s*t*y + 3*s*t*t*z + t**3*w
                                for x, y, z, w in zip(p, a, b, c)))
        p = c
    return result + [p]


PAISLEY = curve([
    (-0.43, 0.13),
    (-0.47, 0.47), (-0.03, 0.53), (0.22, 0.23),
    (0.39, 0.01), (0.26, -0.22), (0.53, -0.46),
    (0.19, -0.41), (0.14, -0.07), (-0.01, -0.13),
    (-0.10, -0.23), (-0.40, -0.20), (-0.43, 0.13),
])


def paisley(draw, x, y, width, height, angle=0):
    co, si = math.cos(angle), math.sin(angle)

    def transform(u, v):
        return x + width*(u*co-v*si), y + height*(u*si+v*co)

    for scale, color, line in [(1, INK, 4), (.78, SOFT, 2)]:
        draw.line([transform(u*scale, v*scale) for u, v in PAISLEY],
                  fill=color, width=line*2, joint="curve")
    cx, cy = transform(-.16, .13)
    for i in range(6):
        t = 2*math.pi*i/6
        a, b = cx + .075*width*math.cos(t), cy + .075*height*math.sin(t)
        draw.ellipse((a-3, b-3, a+3, b+3), fill=INK)
    draw.ellipse((cx-5, cy-5, cx+5, cy+5), fill=INK)


def diamond(draw, x, y, a, b):
    draw.polygon([(x, y-b), (x+a, y), (x, y+b), (x-a, y)], fill=SOFT)


def band():
    w,h=4096,256
    image=Image.new("RGB",(2*w,2*h),BG)
    d=ImageDraw.Draw(image)
    for y in [22, 234]:
        d.line([(0,2*y),(2*w,2*y)],fill=INK,width=7)
    for y in [33, 223]:
        for x in range(0,2*w,26):
            d.line([(x,2*y),(x+13,2*y)],fill=SOFT,width=3)
    step=2*w/12
    for i in range(12):
        x=(i+.5)*step
        paisley(d,x,h,step*.52,260,angle=(-.26 if i%2 else .21))
        diamond(d,(i+1)*step-32,h,16,19)
    return image.resize((w,h),Image.Resampling.LANCZOS)


def scarf():
    w=1024
    image=Image.new("RGB",(2*w,2*w),BG)
    d=ImageDraw.Draw(image)
    for y in [40,62,1986,2008]:
        d.line([(0,y),(2048,y)],fill=INK,width=(7 if y in {40,2008} else 3))
    for row,y in enumerate(range(232,2000,318)):
        for col,x in enumerate(range(160,2050,295)):
            paisley(d,x+(row%2)*124,y,186,225,angle=(-.38 if (row+col)%2 else .45))
            diamond(d,x+121+(row%2)*124,y+115,9,12)
    return image.resize((w,w),Image.Resampling.LANCZOS)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    band().save(OUT / "bandana-print.png", optimize=True)
    scarf().save(OUT / "scarf-print.png", optimize=True)
