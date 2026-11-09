"""Paint the ombré through the authored Ponytail lengths and front wisps."""
import struct
import zlib

import numpy as np
from fit import accessor, node_transforms, read_glb, write_glb

ROOT = [.160,.059,.030]
MID = [.355,.166,.074]
ENDS = [.575,.340,.151]


def gradient():
    t = np.linspace(0,1,512)
    def fade(a,b):
        v = np.clip((t-a)/(b-a),0,1)
        return v*v*(3-2*v)
    first,second=fade(.12,.53)[:,None],fade(.41,.88)[:,None]
    rgb=np.array(ROOT)*(1-first)+np.array(MID)*first
    rgb=rgb*(1-second)+np.array(ENDS)*second
    srgb=np.where(rgb<=.0031308,rgb*12.92,1.055*rgb**(1/2.4)-.055)
    raw=b"".join(b"\0"+bytes(row)*8 for row in np.rint(srgb*255).astype("u1"))
    def chunk(name,data):
        return struct.pack(">I",len(data))+name+data+struct.pack(">I",zlib.crc32(name+data))
    return b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",struct.pack(">IIBBBBB",8,512,8,2,0,0,0))+chunk(b"IDAT",zlib.compress(raw,9))+chunk(b"IEND",b"")


def recolor(source, brown, target):
    model,buf=read_glb(source)
    plain,default=read_glb(brown)
    plain_meshes={n["name"]:(n,r,o) for n,r,o in node_transforms(plain) if "mesh" in n}
    images=set()
    stages={}
    for node,r,o in node_transforms(model):
        if "mesh" not in node:
            continue
        name=node["name"]
        primitives=model["meshes"][node["mesh"]]["primitives"]
        original=plain_meshes[name][0]
        original_primitives=plain["meshes"][original["mesh"]]["primitives"]
        for p,q in zip(primitives,original_primitives,strict=True):
            m=model["materials"][p["material"]]
            sampler=m["pbrMetallicRoughness"].get("baseColorTexture")
            if sampler is None:
                continue
            a,b=p["attributes"],q["attributes"]
            xyz=accessor(model,buf,a["POSITION"],3)
            assert np.array_equal(xyz,accessor(plain,default,b["POSITION"],3)),name
            uv=accessor(model,buf,a["TEXCOORD_0"],2)
            if "roots220" in name:
                x,y,z=(xyz@r.T+o).T
                sweep=np.clip((-.015-z)/.30,0,1)
                gathering=np.exp(-((x+.055)/.23)**2)*np.clip((y-1.84)/.27,0,1)
                t=.32*sweep*gathering
            elif "front" in name.lower():
                u=accessor(plain,default,b["TEXCOORD_0"],2)[:,0]
                t=.82*np.clip((u-.23)/.77,0,1)
            elif "TEXCOORD_0" in b:
                u=accessor(plain,default,b["TEXCOORD_0"],2)[:,0]
                # Slightly stagger the transitions between neighboring locks.
                phase=(sum(name.encode())%7-3)*.013
                t=np.clip(u+phase*np.sin(np.pi*u),0,1)
            else:
                height=(xyz@r.T+o)[:,1]
                t=np.clip((np.quantile(height,.965)-height)/np.ptp(height),0,1)
            uv[:,0]=.5
            uv[:,1]=np.clip(t,.003,.997)
            stages[name]=np.quantile(t,[.2,.5,.8]).round(3).tolist()
            images.add(model["textures"][sampler["index"]]["source"])
    assert images and stages,source
    image=gradient()
    buf.extend(bytes((-len(buf))%4))
    offset=len(buf)
    buf.extend(image)
    view=len(model["bufferViews"])
    model["bufferViews"].append({"buffer":0,"byteOffset":offset,"byteLength":len(image)})
    for i in images:
        model["images"][i].update(bufferView=view,mimeType="image/png",name="Ponytail chestnut to caramel 304")
    model["buffers"][0]["byteLength"]=len(buf)
    write_glb(target,model,buf)
    return stages
