from pathlib import Path
import json,struct
import numpy as np
from PIL import Image,ImageOps

def paste(im,f,x,y,w,h):
 pic=Image.open(f).convert('RGBA');bg=Image.new('RGBA',pic.size,'#29394c');bg.alpha_composite(pic);pic=ImageOps.contain(bg.convert('RGB'),(w,h));im.paste(pic,(x+(w-pic.width)//2,y))

def glb(f):
 raw=f.read_bytes();n=struct.unpack_from('<I',raw,12)[0];return json.loads(raw[20:20+n]),raw[28+n:]

def array(g,b,i):
 a=g['accessors'][i];v=g['bufferViews'][a['bufferView']];dt={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']];width={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];step=np.dtype(dt).itemsize
 values=np.ndarray((a['count'],width),dtype=dt,buffer=b,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',width*step),step)).copy()
 return values.astype('f')/np.iinfo(dt).max if a.get('normalized') else values

def positions(f):
 g,b=glb(f);return {m['name']:np.vstack([array(g,b,p['attributes']['POSITION']) for p in m['primitives']]) for m in g['meshes']}
