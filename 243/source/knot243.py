"""Raise the actual crossed cloth into a loose neck knot and outer drape."""
import sys,json,math
from pathlib import Path
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue235')
import common235 as c
c.P=Path(__file__).parent
from common235 import *
from scarf_support235 import convex_support
import bmesh
BASE=P.parent/'catalogue242'

def interp(row,t):
    for (lo,p),(hi,q) in zip(row,row[1:]):
        if lo-1e-7<=t<=hi+1e-7:return p+(q-p)*max(0,min(1,(t-lo)/(hi-lo)))
    return row[0][1] if t<row[0][0] else row[-1][1]

def curve(keys,t):
    for i,((lo,p),(hi,q)) in enumerate(zip(keys,keys[1:])):
        if lo<=t<=hi:
            before=keys[max(0,i-1)];after=keys[min(len(keys)-1,i+2)]
            m0=(q-before[1])/(hi-before[0]);m1=(after[1]-p)/(after[0]-lo)
            u0=(t-lo)/(hi-lo)
            return p*(2*u0**3-3*u0**2+1)+m0*((u0**3-2*u0**2+u0)*(hi-lo))+q*(-2*u0**3+3*u0**2)+m1*((u0**3-u0**2)*(hi-lo))
    return keys[0][1] if t<keys[0][0] else keys[-1][1]

def run(build,top,quick=False):
    bpy.ops.wm.open_mainfile(filepath=str(BASE/'sources'/f'{build}-{top}-pashmina242.blend'))
    s=bpy.context.scene;ob=next(o for o in s.objects if 'joined hood wrap and ends239' in o.name)
    changed_names={ob.name}|{o.name for o in s.objects if o.get('component159')=='headgear' and ('free fringe239' in o.name or 'continuous face to fold hem239' in o.name)}
    frozen={k:v for k,v in u.object_geometry(s).items() if k not in changed_names}
    n=len(ob.data.vertices)//2;old=[ob.matrix_world@v.co for v in ob.data.vertices];assert n*2==len(old)
    uv={}
    for f in ob.data.polygons:
        if max(f.vertices)>=n:continue
        for li,vi in zip(f.loop_indices,f.vertices):uv[vi]=ob.data.uv_layers.active.data[li].uv.copy()
    reliable={-1:{},1:{}}
    for i,q in uv.items():
        if q.x<-.8*.18:side=-1;t=-q.x/.8;w=1-q.y/.175
        elif q.x>1+.8*.18:side=1;t=(q.x-1)/.8;w=q.y/.175
        else:continue
        j=int(round(t*127));reliable[side].setdefault(j,[]).append((i,float(w)))
    grids={};oldrows={}
    for side in [-1,1]:
        ref=sorted(reliable[side][30]);count=len(ref);start=ref[0][0]-29*count
        for j,items in reliable[side].items():assert sorted(i for i,w in items)==list(range(start+(j-1)*count,start+j*count))
        grids[side]={j:[(start+(j-1)*count+k,w) for k,(i,w) in enumerate(ref)] for j in range(1,128)}
        oldrows[side]={j:sorted([(w,old[i]) for i,w in row]) for j,row in grids[side].items()}
    bodies=[o for o in s.objects if o.type=='MESH' and (o.name=='Skin / rounded torso' or (o.get('component159')=='top' and not any(w in o.name.lower() for w in ['sleeve','string','lace','button','collar','hood','cuff'])))]
    support=convex_support(bodies)
    heads=[o for o in s.objects if o.type=='MESH' and any(m and m.name.startswith('Skin') for m in o.data.materials) and min((o.matrix_world@v.co).z for v in o.data.vertices)>1.42 and max((o.matrix_world@v.co).z for v in o.data.vertices)>2.0]
    head=tree(heads) if heads else None
    def front_y(x,z):
        hit,normal,_,_=support.ray_cast(Vector((x,-2,z)),Vector((0,1,0)),4)
        if hit is None and head:hit,normal,_,_=head.ray_cast(Vector((x,-2,z)),Vector((0,1,0)),4)
        return float(hit.y) if hit is not None else -.075
    def seat(p,clear):
        radial=Vector((p.x,p.y,0));radial.normalize()
        hit,normal,_,_=support.ray_cast(Vector((0,0,p.z)),radial,1.5)
        if hit is None and head:hit,normal,_,_=head.ray_cast(Vector((0,0,p.z)),radial,1.5)
        if hit is None:return Vector((p.x,min(p.y,front_y(p.x,p.z))-clear,p.z))
        if normal.dot(radial)<0:normal=-normal
        return hit+normal*clear
    inverse=ob.matrix_world.inverted().to_3x3();deltas={};centers_out={};newrows={};metrics={}
    for side in [-1,1]:
        root=interp(oldrows[side][1],.5);endz=1.035 if side<0 else 1.055
        centers=[root,Vector((side*.145,-.09,1.394)),Vector((side*.055,-.10,1.400)),Vector((-side*.018,-.12,1.390+(0.008 if side>0 else 0))),Vector((-side*.090,-.15,1.362)),Vector((-side*.210,-.17,1.315)),Vector((-side*.252,-.18,1.225)),Vector((-side*.238,-.17,1.125)),Vector((-side*.222,-.16,endz))]
        path=a.sample(centers,128)
        rootspan=(oldrows[side][1][-1][1]-oldrows[side][1][0][1]).normalized()
        spans=a.sample([rootspan,Vector((.45,0,-.89*side)),Vector((.60,0,-.80*side)),Vector((.78,0,-.63*side)),Vector((.70,0,-.71*side)),Vector((.76,0,-.65*side)),Vector((.98,0,-.20*side)),Vector((1,0,0)),Vector((1,0,0))],128)
        endrow=oldrows[side][127];endwidth=sum((b[1]-a0[1]).length for a0,b in zip(endrow,endrow[1:]))
        width=interp(oldrows[side][1],1)-interp(oldrows[side][1],0)
        widths=[(0,width.length),(.13,.085),(.26,.070),(.38,.073 if side>0 else .060),(.46,.062),(.60,.084),(.74,.114),(.87,.129),(1,endwidth)]
        newrows[side]={};centers_out[side]=[]
        for j,row in grids[side].items():
            t=j/127;center=path[j].copy()
            if side>0:
                # One cloth length turns down and tucks back through the
                # crossing, rather than suggesting a knot with a flat X.
                keys=[(.22,Vector((.080,-.10,1.396))),(.29,Vector((.025,-.10,1.396))),(.35,Vector((-.035,-.11,1.387))),(.40,Vector((-.035,-.12,1.365))),(.445,Vector((.008,-.13,1.368))),(.505,Vector((-.090,-.15,1.350))),(.58,Vector((-.180,-.17,1.329)))]
                amount=smooth((t-.22)/.04)*(1-smooth((t-.54)/.06))
                center=center.lerp(curve(keys,t),amount)
            knot=smooth((t-.20)/.10)*(1-smooth((t-.49)/.12))
            if side<0:center.z-=.010*knot
            center.y=front_y(center.x,center.z)
            span=spans[j].normalized();want=interp(widths,t)
            if side>0:want*=1-.24*math.exp(-((t-.42)/.055)**2)
            layer=.012*knot if side>0 else .002*knot
            def point(w,scale):
                p=center+span*((w-.5)*scale);p.y=center.y
                # Soft gathers belong to the actual crossing lengths.
                tuck=.015*math.exp(-((t-.385)/.055)**2) if side>0 else 0.
                relief=.004+layer+(.008*knot+tuck)*math.sin(math.pi*w)**2+.0018*math.sin(3*math.pi*w+.6*t)**2
                return seat(p,relief)
            scale=want
            for iteration in range(4):
                samples=[point(w,scale) for w in np.linspace(0,1,25)]
                arc=sum((q-p).length for p,q in zip(samples,samples[1:]));scale*=max(.7,min(1.45,want/max(.001,arc)))
            fit=smooth((t-.045)/.20);new=[]
            for i,w in row:
                target=old[i].lerp(point(w,scale),fit);delta=target-old[i]
                for k in [i,i+n]:ob.data.vertices[k].co+=inverse@delta;deltas[k]=delta
                new.append((w,target))
            newrows[side][j]=new;centers_out[side].append(list(interp(new,.5)))
        actual=sum((b[1]-a0[1]).length for a0,b in zip(newrows[side][127],newrows[side][127][1:]));assert abs(actual/endwidth-1)<.04
        metrics[str(side)]=dict(end_width_before=endwidth,end_width_after=actual,tip=list(interp(newrows[side][127],.5)),knot_center=list(interp(newrows[side][48],.5)),outer_drape=list(interp(newrows[side][92],.5)))
    # Follow the sewn root-edge geometry with the existing border tube.
    hem=next(o for o in s.objects if 'continuous face to fold hem239' in o.name)
    edge=[]
    for side in [-1,1]:
        for j,row in grids[side].items():
            if j>23:continue
            i,w=row[-1] if side<0 else row[0];edge.append((old[i],deltas[i]))
    assert len(hem.data.vertices)%6==0
    for k in range(0,len(hem.data.vertices),6):
        center=sum((hem.matrix_world@v.co for v in hem.data.vertices[k:k+6]),Vector())/6
        p,delta=min(edge,key=lambda item:(item[0]-center).length)
        if (p-center).length<.002:
            d=hem.matrix_world.inverted().to_3x3()@delta
            for v in hem.data.vertices[k:k+6]:v.co+=d
    for tassel in [o for o in s.objects if 'free fringe239' in o.name]:
        fields=tassel.name.split();side=int(fields[-2]);k=int(fields[-1]);w=(k+.5)/11
        delta=interp(newrows[side][127],w)-interp(oldrows[side][127],w);local=tassel.matrix_world.inverted().to_3x3()@delta
        for v in tassel.data.vertices:v.co+=local
    assert all((ob.matrix_world@ob.data.vertices[i].co-old[i]).length<1e-9 for i in range(len(old)) if i not in deltas),'Hood, root or under-wrap changed'
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(len(e.link_faces)==2 for e in bm.edges);bm.to_mesh(ob.data);bm.free()
    assert all(u.object_geometry(s).get(k)==v for k,v in frozen.items()),'Protected model changed'
    key=f'{build}-{top}-pashmina243';parts=save(s,key,['headgear']);s=bpy.context.scene
    render(s,key,['front','threequarter','profile'],size=384 if quick else 256,body=True)
    if quick:
        for angle in ['front','threequarter','profile']:
            u.camera(s,angle,640,True);s.camera.data.ortho_scale=1.4;s.camera.location.z+=.10;s.cycles.samples=24;s.render.filepath=str(P/'review1'/f'{build}-close243-{angle}.png');bpy.ops.render.render(write_still=True)
    return dict(source=str(P/'sources'/f'{key}.blend'),component=parts['headgear'],top=top,protected_neighbors_exact=True,hood_roots_and_underwrap_exact242=True,closed_surface=True,end_metrics=metrics,center_paths=centers_out,construction='Two continuous crossing cloth lengths form the raised soft knot; flared outer-chest drape follows major body/garment support. End width retained; root border and fringe follow their own attached fabric samples.')

if __name__=='__main__':
    cat=json.loads((R/'242/catalogue242.json').read_text());records=json.loads((P/'fits243.json').read_text()) if (P/'fits243.json').exists() else {}
    for build in (['Feminine'] if '--draft' in sys.argv else ['Feminine','Masculine']):
        for top in (['open'] if '--draft' in sys.argv else cat['builds'][build]['tops']):
            records.setdefault(build,{})[top]=run(build,top,'--draft' in sys.argv);u.dump(P/'fits243.json',records);print('KNOT243',build,top,flush=True)
