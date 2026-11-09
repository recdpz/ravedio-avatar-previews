"""Rebuild the lower scarf as one sewn drape below the preserved hood."""
import json
import sys
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

import numpy as np

REV = Path(__file__).resolve().parents[1]
ROOT = REV.parent
sys.path.insert(0, str(ROOT / "299/tools"))
from fit import CENTER, accessor, ease, local_path, node_transforms, read_glb, surface, triangles, unit, write_glb
from sculpt import add_buffer, deform, smooth

CUT = 1.672
SECTIONS = 46
ROOT_START = 31
THICKNESS = .0028


def read(path):
    return json.loads(path.read_text(encoding="utf8"))


def clip_hood(points, uv, normals, faces):
    """Keep the outer crown and return its one open lower arc."""
    tri = points[faces]
    tex = uv[faces]
    ab, ac = tex[:,1]-tex[:,0], tex[:,2]-tex[:,0]
    winding = ab[:,0]*ac[:,1] - ab[:,1]*ac[:,0]
    selected = faces[(winding>1e-9) & (tri[:,:,1].max(axis=1)>CUT) &
                     (tex[:,:,0].min(axis=1)>-.00001) & (tex[:,:,0].max(axis=1)<1.00001)]
    verts, coords, shade, indices, seen = [], [], [], [], {}

    def vertex(p, q, n):
        key = tuple(np.round(p,7))
        if key not in seen:
            seen[key] = len(verts)
            verts.append(np.array(p,dtype=float))
            coords.append(q)
            shade.append(n)
        return seen[key]

    for face in selected:
        poly = []
        for ia,ib in zip(face,np.roll(face,-1)):
            a,b = points[ia],points[ib]
            in_a,in_b = a[1]>=CUT,b[1]>=CUT
            if in_a:
                poly.append(vertex(a,uv[ia],normals[ia]))
            if in_a != in_b:
                w = (CUT-a[1])/(b[1]-a[1])
                p = a+(b-a)*w
                p[1] = CUT
                poly.append(vertex(p,uv[ia]+(uv[ib]-uv[ia])*w,normals[ia]+(normals[ib]-normals[ia])*w))
        for j in range(1,len(poly)-1):
            t = (poly[0],poly[j],poly[j+1])
            if len(set(t))==3:
                indices.append(t)
    edges = boundary(indices)
    seam = [(a,b) for a,b in edges if abs(verts[a][1]-CUT)<1e-7 and abs(verts[b][1]-CUT)<1e-7]
    adj = defaultdict(list)
    for a,b in seam:
        adj[a].append(b)
        adj[b].append(a)
    ends = [a for a in adj if len(adj[a])==1]
    assert len(ends)==2 and all(len(v)<=2 for v in adj.values()), (len(ends),len(adj))
    start = min(ends,key=lambda a:verts[a][0])
    ring = [start]
    while True:
        options = [v for v in adj[ring[-1]] if len(ring)==1 or v!=ring[-2]]
        if not options:
            break
        ring.append(options[0])
    assert len(ring)==len(adj)
    return verts,coords,shade,indices,ring


def boundary(faces):
    edges={}
    for face in faces:
        for a,b in zip(face,(face[1],face[2],face[0])):
            key = (min(a,b),max(a,b))
            edges[key] = (a,b) if key not in edges else None
    return [edge for edge in edges.values() if edge]


@lru_cache(maxsize=32)
def mesh_tree(path, role):
    if role=="body":
        return surface(path,lambda n:"rounded torso" in n.lower())
    if role=="top":
        return surface(path,lambda n:not any(t in n.lower() for t in ("sleeve","cord","cuff")))
    return surface(path)


class Fields:
    def __init__(self, body, top, hair):
        self.body=[mesh_tree(body,"body")]
        if top:
            self.body.append(mesh_tree(top,"top"))
        self.body=[tree for tree in self.body if tree is not None]
        self.hair=[mesh_tree(p,"hair") for p in hair]
        self.hair=[tree for tree in self.hair if tree is not None]
        # Soft convex support across neckline dips, seams and buttons.
        self.x = np.linspace(-.43,.43,145)
        self.y = np.linspace(.985,1.51,106)
        actual = np.zeros((len(self.y),len(self.x)))
        for i,y in enumerate(self.y):
            for j,x in enumerate(self.x):
                distances = [t.ray_cast((x,y,.65),(0,0,-1),.82)[3] for t in self.body]
                hits = [d for d in distances if d is not None]
                if hits:
                    actual[i,j] = max(0., .65-min(hits))
        padded = np.pad(actual,2,mode="edge")
        broad = np.maximum.reduce([padded[i:i+len(self.y),j:j+len(self.x)] - .008*(abs(i-2)+abs(j-2))
                                  for i in range(5) for j in range(5)])
        self.front = np.maximum(actual, smooth(broad,1.6,1.8))

    def depth(self, xy):
        u = np.clip((xy[:,0]-self.x[0])/(self.x[1]-self.x[0]),0,len(self.x)-1.00001)
        v = np.clip((xy[:,1]-self.y[0])/(self.y[1]-self.y[0]),0,len(self.y)-1.00001)
        j,i = u.astype(int),v.astype(int)
        a,b = u-j,v-i
        return ((1-b)*((1-a)*self.front[i,j]+a*self.front[i,j+1])
                +b*((1-a)*self.front[i+1,j]+a*self.front[i+1,j+1]))

    def radii(self, angle, height, trees):
        result = np.zeros(angle.shape)
        for i in np.ndindex(angle.shape):
            x,z = np.sin(angle[i]),np.cos(angle[i])
            p = (.60*x,height[i],CENTER[2]+.60*z)
            for tree in trees:
                _,_,_,dist = tree.ray_cast(p,(-x,0,-z),.60)
                if dist is not None:
                    result[i] = max(result[i], .60-dist)
        return result


def quads(faces,a,b):
    for j in range(len(a)-1):
        faces.extend(((a[j],a[j+1],b[j+1]),(a[j],b[j+1],b[j])))


def add_row(verts,coords,points,uv):
    start = len(verts)
    verts.extend(points)
    coords.extend(uv)
    return list(range(start,len(verts)))


def angular_filter(values, angle, width):
    grid=np.linspace(angle[-1],angle[0],301)
    values=np.interp(grid,angle[::-1],values[::-1])
    step=grid[1]-grid[0]
    support=int(np.ceil(3*width/step))
    weights=np.exp(-.5*(np.arange(-support,support+1)*step/width)**2)
    weights/=weights.sum()
    filtered=np.convolve(np.pad(values,support,mode="edge"),weights,mode="valid")
    return np.interp(angle,grid,filtered)


def cape(verts,coords,faces,ring,field,upper,normals):
    p=np.asarray([verts[i] for i in ring])
    uv0=np.asarray([coords[i] for i in ring])
    radius=np.hypot(p[:,0],p[:,2]-CENTER[2])
    angle=np.unwrap(np.arctan2(p[:,0],p[:,2]-CENTER[2]))
    angle_fit=np.minimum.accumulate(angle-np.arange(len(angle))*1e-5)
    t=np.linspace(0.,1.,SECTIONS+1)[:,None]
    front=1-ease((-np.cos(angle)+.21)/.49)
    az=angle[None,:]+(angle_fit-angle)*ease(t/.16)+front*np.sign(np.sin(angle))*(.087*ease(t)+.039*np.sin(np.pi*t)**2)
    y_end=1.315+.026*front+.009*np.cos(2*angle+.3)-.004*np.cos(5*angle)
    y=CUT+t*(y_end-CUT)

    # Sample the support in a regular cylindrical grid. Broaden the guard
    # across nearby rows before smoothing so small lock grooves disappear.
    regular_angle=np.linspace(-np.pi,np.pi,241,endpoint=False)
    regular_y=np.linspace(1.29,CUT+.006,99)
    aa,yy=np.meshgrid(regular_angle,regular_y)
    body=field.radii(aa,yy,field.body)
    hair=field.radii(aa,yy,field.hair)
    side=ease((np.abs(aa)-1.12)/.16)
    hair=np.where(hair>0,(hair+.028)*side,0.)
    required=np.maximum(hair,body+.013)
    cushion=required.copy()
    for _ in range(13):
        cushion=np.maximum.reduce((cushion,
            np.roll(cushion,1,1)-.0022,np.roll(cushion,-1,1)-.0022,
            np.vstack((cushion[:1],cushion[:-1]))-.0030,
            np.vstack((cushion[1:],cushion[-1:]))-.0036))
    guard=smooth(cushion,5.5,6.0)
    u=(az+np.pi)/(2*np.pi)*len(regular_angle)
    v=np.clip((y-regular_y[0])/(regular_y[1]-regular_y[0]),0,len(regular_y)-1.00001)
    i,j=np.floor(v).astype(int),np.floor(u).astype(int)
    a,b=u-j,v-i
    left,right=j%len(regular_angle),(j+1)%len(regular_angle)
    support=(1-b)*((1-a)*guard[i,left]+a*guard[i,right])+b*((1-a)*guard[i+1,left]+a*guard[i+1,right])
    toe=np.maximum(field.radii(az[-1],y[-1],field.body)+.015,support[-1]-.004)

    above=(upper[:,1]>=CUT-.014)&(upper[:,1]<=CUT+.020)
    samples=upper[above]
    sample_n=normals[above]
    nearest=np.argmin(np.sum((samples[None,:,:]-p[:,None,:])**2,axis=2),axis=1)
    n=sample_n[nearest]
    radial=n[:,0]*np.sin(angle)+n[:,2]*np.cos(angle)
    slope=np.clip(-n[:,1]/np.maximum(radial,.28),-.62,1.15)*(y_end-CUT)
    slope=angular_filter(slope,angle_fit,.090)
    shape=radius+(angular_filter(radius,angle_fit,.075)-radius)*ease(t/.24)
    toe=angular_filter(toe,angle_fit,.054)
    r=(2*t**3-3*t**2+1)*shape+(t**3-2*t**2+t)*slope+(-2*t**3+3*t**2)*toe
    correction=np.maximum(support-r,0)
    for _ in range(4):
        correction=np.maximum.reduce((correction,
            np.vstack((correction[:1],correction[:-1]))-.007,
            np.vstack((correction[1:],correction[-1:]))-.007))
    correction=smooth(correction,2.4,2.2)
    correction=np.array([angular_filter(row,angle_fit,.042) for row in correction])
    r+=correction*ease(t/.18)
    r+=(.007*np.cos(5*angle+.7)+.003*np.sin(8*angle))*np.sin(np.pi*t)**2
    p3=np.stack((r*np.sin(az),y,r*np.cos(az)+CENTER[2]),axis=-1)
    face=uv0[:,1]
    center=1-np.abs(np.linspace(-1,1,len(angle)))
    uv_end=np.column_stack((uv0[:,0],face+.21*center))
    rows=[ring]
    for i in range(1,len(t)):
        tex=uv0+t[i]*(uv_end-uv0)
        rows.append(add_row(verts,coords,p3[i],tex))
        quads(faces,rows[-2],rows[-1])
    return rows

def curve(values,t):
    values=np.asarray(values,dtype=float)
    k = np.minimum((t*(len(values)-1)).astype(int),len(values)-2)
    f=(t*(len(values)-1)-k)[:,None]
    a,b=values[k],values[k+1]
    da=(b-values[np.maximum(k-1,0)])*.5
    db=(values[np.minimum(k+2,len(values)-1)]-a)*.5
    return (2*f**3-3*f**2+1)*a+(f**3-2*f**2+f)*da+(-2*f**3+3*f**2)*b+(f**3-f**2)*db


def ends(verts,coords,faces,rows,field,style):
    terminal=[]
    for side,col in ((-1,0),(1,-1)):
        root=[row[col] for row in rows[ROOT_START:]]
        anchor=np.asarray([verts[i] for i in root])
        tex0=np.asarray([coords[i] for i in root])
        count=len(root)
        t=np.linspace(0,1,80)
        start=anchor.mean(axis=0)
        path=curve([start[:2],(.183*side,1.403),(.083*side,1.389),(-.018*side,1.365),
                    (-.130*side,1.316),(-.225*side,1.237),(-.221*side,1.141),
                    (-.210*side,1.044+.018*(side>0))],t)
        direction=unit(np.gradient(path,axis=0))
        across=np.column_stack((-direction[:,1],direction[:,0]))*side
        width=np.interp(t,[0,.17,.38,.62,.82,1.],[.081,.065,.057,.078,.099,.112])
        w=np.linspace(-.5,.5,count)
        ribbon=path[:,None,:]+w[None,:,None]*width[:,None,None]*across[:,None,:]
        ribbon+= (anchor[:,:2]-ribbon[0])[None,:,:]*(1-ease(t/.20))[:,None,None]
        xy=ribbon.reshape(-1,2)
        front=field.depth(xy).reshape(ribbon.shape[:2])
        profile=.018+.0035*np.sin(2*np.pi*(w+.25))[None,:]*ease(t/.26)[:,None]
        over=.016 if side>0 else 0.
        z=front+profile+over*(1-ease((t-.58)/.25))[:,None]
        z+=(anchor[:,2]-z[0])[None,:]*(1-ease(t/.17))[:,None]
        z+=.019*np.sin(np.pi*np.clip(t/.22,0,1))[:,None]
        p=np.concatenate((ribbon,z[:,:,None]),axis=-1)
        prior=root
        for j in range(1,len(t)):
            u=(1 if side>0 else 0)+.8*side*t[j]
            tex1=np.column_stack((np.full(count,u), (w+.5 if side>0 else .5-w)*.175))
            tex=tex0+(tex1-tex0)*ease(t[j]/.10)
            new=add_row(verts,coords,p[j],tex)
            quads(faces,prior,new)
            prior=new
        terminal.append(p[-1])
    return terminal


def orient(faces):
    edges=defaultdict(list)
    for i,tri in enumerate(faces):
        for a,b in zip(tri,(tri[1],tri[2],tri[0])):
            edges[(min(a,b),max(a,b))].append((i,a<b))
    neighbors=defaultdict(list)
    for adj in edges.values():
        assert 1<=len(adj)<=2
        if len(adj)==2:
            (a,ab),(b,bb)=adj
            neighbors[a].append((b,ab==bb))
            neighbors[b].append((a,ab==bb))
    state={0:False}
    stack=[0]
    while stack:
        i=stack.pop()
        for j,flip in neighbors[i]:
            value=state[i]^flip
            if j not in state:
                state[j]=value
                stack.append(j)
            else:
                assert state[j]==value
    assert len(state)==len(faces)
    return [tri[::-1] if state[i] else tri for i,tri in enumerate(faces)]


def shell(verts,coords,faces,cape_rows,upper_shade):
    verts=np.asarray(verts)
    faces=orient(faces)
    rim=boundary(faces)
    tri=np.asarray(faces,dtype=np.int32)
    q=verts[tri]
    n=np.cross(q[:,1]-q[:,0],q[:,2]-q[:,0])
    normals=np.zeros_like(verts)
    for j in range(3):
        np.add.at(normals,tri[:,j],n)
    normals=unit(normals)
    upper_count=len(upper_shade)
    normals[:upper_count]=unit(np.asarray(upper_shade))
    ring=cape_rows[0]
    for row,ids in enumerate(cape_rows[1:10],start=1):
        w=ease(row/10)
        normals[ids]=unit(normals[ring]*(1-w)+normals[ids]*w)
    length=len(verts)
    radial=unit(np.column_stack((verts[:,0],np.zeros(length),verts[:,2]-CENTER[2])))
    lower=ease((CUT+.065-verts[:,1])/.065)
    depth=unit(normals+(radial-normals)*lower[:,None])
    first_end=max(cape_rows[-1])+1
    depth[first_end:]=[0.,0.,1.]
    # Constant radial thickness below the crown prevents the inner sheet
    # from buckling at a close fold. Across each free end it follows depth.
    sides=[(b,a,a+length) for a,b in rim]+[(b,a+length,b+length) for a,b in rim]
    return (np.vstack((verts,verts-THICKNESS*depth)),np.vstack((normals,-normals)),
            np.vstack((coords,coords)),np.vstack((tri,tri[:,::-1]+length,sides)).astype("<u4"))


def fringe(terminal):
    """Small suspended threads follow each new free cloth edge."""
    pts,norms,faces=[],[],[]
    for end in terminal:
        for k in range(11):
            j=round((k+.5)/11*(len(end)-1))
            p=end[j].copy()
            for t in (0.,.52,1.):
                for i in range(5):
                    ph=i*2*np.pi/5
                    n=np.array([np.cos(ph),0,np.sin(ph)])
                    pts.append(p+n*.0011*(1-.4*t)+np.array([.001*np.sin(k)*t,-(.013+.003*np.cos(k))*t,0.]))
                    norms.append(n)
            start=len(pts)-15
            for ring in (0,1):
                a=start+ring*5
                quads(faces,[a+i%5 for i in range(6)],[a+5+i%5 for i in range(6)])
    return np.asarray(pts),np.asarray(norms),None,np.asarray(faces,dtype="<u4")


def set_mesh(doc,binary,primitive,geometry,rotation,offset):
    p,n,uv,f=geometry
    attributes=primitive["attributes"]
    for key,values,kind,component in (
        ("POSITION",(p-offset)@rotation,"VEC3",5126),("NORMAL",n@rotation,"VEC3",5126),
        ("TEXCOORD_0",uv,"VEC2",5126),("indices",f.ravel(),"SCALAR",5125)):
        if values is None:
            attributes.pop(key,None)
            continue
        template={"type":kind,"componentType":component}
        if key=="POSITION":
            template["min"]=[]
        dest=primitive if key=="indices" else attributes
        dest[key]=add_buffer(doc,binary,values.astype("<u4" if component==5125 else "<f4"),
                             34963 if key=="indices" else 34962,template)
    assert np.isfinite(p).all() and np.isfinite(n).all()


def build_scarf(source, target, body, top, hair, style):
    field=Fields(body,top,hair)
    doc,binary=read_glb(source)
    nodes=list(node_transforms(doc))
    for node,rotation,offset in nodes:
        if "mesh" not in node:
            continue
        mesh=doc["meshes"][node["mesh"]]
        if "joined hood" not in mesh["name"]:
            continue
        p,=mesh["primitives"]
        a=p["attributes"]
        co=accessor(doc,binary,a["POSITION"],3)@rotation.T+offset
        uv=accessor(doc,binary,a["TEXCOORD_0"],2).copy()
        uv[:,1]=1-uv[:,1]
        normals=accessor(doc,binary,a["NORMAL"],3)@rotation.T
        verts,tex,shade,faces,ring=clip_hood(co,uv,normals,triangles(doc,binary,p["indices"]))
        rows=cape(verts,tex,faces,ring,field,co,normals)
        terminals=ends(verts,tex,faces,rows,field,style)
        tex=np.asarray(tex)
        tex[:,1]=1-tex[:,1]
        set_mesh(doc,binary,p,shell(verts,tex,faces,rows,shade),rotation,offset)
    for node,rotation,offset in nodes:
        if "mesh" not in node:
            continue
        mesh=doc["meshes"][node["mesh"]]
        if "face to fold hem" in mesh["name"]:
            # The print and thickness define the edge of the new drape.
            del node["mesh"]
        if "free fringe" in mesh["name"]:
            set_mesh(doc,binary,mesh["primitives"][0],fringe(terminals),rotation,offset)
    write_glb(target,doc,compact(doc,binary))


def compact(doc,binary):
    # Drop the replaced geometry buffers while retaining the original texture.
    used_meshes=sorted({node["mesh"] for node in doc["nodes"] if "mesh" in node})
    doc["meshes"]=[doc["meshes"][i] for i in used_meshes]
    for node in doc["nodes"]:
        if "mesh" in node:
            node["mesh"]=used_meshes.index(node["mesh"])
    primitives=[p for mesh in doc["meshes"] for p in mesh["primitives"]]
    used_accessors=sorted({i for p in primitives for i in [p["indices"],*p["attributes"].values()]})
    doc["accessors"]=[doc["accessors"][i] for i in used_accessors]
    for p in primitives:
        p["indices"]=used_accessors.index(p["indices"])
        p["attributes"]={k:used_accessors.index(v) for k,v in p["attributes"].items()}
    users=[*doc["accessors"],*doc["images"]]
    used_views=sorted({item["bufferView"] for item in users})
    doc["bufferViews"]=[doc["bufferViews"][i] for i in used_views]
    for item in users:
        item["bufferView"]=used_views.index(item["bufferView"])
    data=bytearray()
    for view in doc["bufferViews"]:
        old=view.get("byteOffset",0)
        data.extend(bytes((-len(data))%4))
        view["byteOffset"]=len(data)
        data.extend(binary[old:old+view["byteLength"]])
    data.extend(bytes((-len(data))%4))
    doc["buffers"][0]["byteLength"]=len(data)
    return data


def hair_under_cloth(points,style):
    x,y,z=points.T
    radius=np.hypot(x,z-CENTER[2])
    angle=np.abs(np.arctan2(x,z-CENTER[2]))
    rear=ease((angle-1.50)/.37)
    if style=="box-braids":
        p=points.copy()
        front=ease((z-.092)/.11)*ease((1.411-y)/.141)
        p[:,2]+=.053*front
        return p
    if style=="straight":
        # Tuck the shortest rear tips above the hem without pulling up the
        # straight locks that frame the face.
        tuck=rear*ease((1.56-y)/.16)
        y=y+.043*tuck
        inward=.012*tuck
    elif style=="curls":
        # Fit the low interior curls under the turn into the nape.
        inward=.052*rear*ease((1.625-y)/.24)*ease((y-1.305)/.045)
    else:
        inward=.018*rear*ease((1.62-y)/.18)
    moved=np.maximum(radius-inward,.001)/np.maximum(radius,.001)
    return np.column_stack((x*moved,y,CENTER[2]+(z-CENTER[2])*moved))


def build(receipt):
    rows=read(receipt)
    scarves=json.loads((ROOT/"299/pashmina-fits.json").read_text(encoding="utf8").replace('"./assets/','"../299/assets/'))
    hair_fits=json.loads((ROOT/"299/hair-fits.json").read_text(encoding="utf8").replace('"./assets/','"../299/assets/'))
    assets=REV/"assets"
    assets.mkdir(exist_ok=True)
    altered={}
    for style in ("curls","bob","box-braids","straight"):
        selection=hair_fits["Feminine"][style]["fits"]["pashmina"]
        for color,uri in selection.items():
            source=(REV/uri).resolve()
            target=assets/f"{style}-covered-{color}.glb"
            deform(source,target,lambda p:hair_under_cloth(p,style))
            selection[color]="./assets/"+target.name
            altered[source]=target
    for row in rows:
        if row["headgearColor"]!="default" or row["revision"]!="299":
            continue
        build,style,top=(row[key] for key in ("build","hair","top"))
        parts=row["parts"]
        hair=[local_path(parts[k]) for k in ("hair","hairLengths") if k in parts]
        hair=[altered.get(part.resolve(),part) for part in hair]
        target=assets/f"{build.lower()}-{style}-{top}.glb"
        build_scarf(local_path(parts["headgear"]),target,local_path(parts["base"]),
                    local_path(parts["top"]) if "top" in parts else None,hair,style)
        scarves[build][style][top]="./assets/"+target.name
        print(build,style,top,flush=True)
    (REV/"hair-fits.json").write_text(json.dumps(hair_fits,indent=2)+"\n",encoding="utf8")
    (REV/"pashmina-fits.json").write_text(json.dumps(scarves,indent=2)+"\n",encoding="utf8")


if __name__=="__main__":
    build(Path(sys.argv[-1]))
