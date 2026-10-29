"""One continuous neck wrap with slightly narrower crossing ends.

Upper235 hood and all protected model components stay unchanged. Fits are
authored per top against broad body/garment surfaces, never runtime physics.
"""
import sys
from pathlib import Path
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue235')
import common235 as c
c.P=Path(__file__).parent
from common235 import *
from scarf_support235 import convex_support,cloth_boundary
import headwear235 as hats
from math import sin,cos,pi
OLD=P.parent/'catalogue235'
CAT237=json.loads((R/'235/catalogue235.json').read_text())

def patch(name,fn,nu,nv,mat):
    ob=hats.grid(name,fn,nu,nv,mat,0)
    sub=ob.modifiers.new('Soft woven folds237','SUBSURF');sub.levels=1;sub.render_levels=1
    solid=ob.modifiers.new('Woven thickness237','SOLIDIFY');solid.thickness=.003;solid.offset=-1
    return ob

def interpolate(edge,value):
    for (lo,p),(hi,q) in zip(edge,edge[1:]):
        if lo<=value<=hi:return p.lerp(q,(value-lo)/(hi-lo))
    return edge[0][1].copy() if value<edge[0][0] else edge[-1][1].copy()

def run(build,top,quick=False):
    bpy.ops.wm.open_mainfile(filepath=str(OLD/'sources'/f'{build}-pashmina-knot235.blend'))
    s=bpy.context.scene;a.setup()
    for ob in list(s.objects):
        if ob.get('component159')=='headgear' and 'soft crown and rear' not in ob.name:u.delete(ob)
        elif ob.get('component159') in ['top','clothing'] or ob.name.startswith('Clothing /'):u.delete(ob)
    top_path=CAT237['builds'][build]['tops'][top]['path']
    if top_path:imported((R/'235'/top_path).resolve(),'top')
    frozen={k:v for k,v in u.object_geometry(s).items() if s.objects[k].get('component159')!='headgear'}
    hood=next(ob for ob in s.objects if 'soft crown and rear' in ob.name)
    mat=hood.data.materials[0];mat.name='Headwear / continuous woven pashmina237'
    bodies=[ob for ob in s.objects if ob.type=='MESH' and (ob.name=='Skin / rounded torso' or (ob.get('component159')=='top' and not any(w in ob.name.lower() for w in ['sleeve','string','lace','button','collar','hood','cuff'])))]
    assert any(ob.name=='Skin / rounded torso' for ob in bodies)
    support=convex_support(bodies);actual=tree(bodies)
    # Radial sections retain the torso's actual shoulder-to-chest curvature.
    # A convex major-form envelope bridges necklines and small garment hollows.
    def seat(p,offset=.004):
        radial=Vector((p.x,p.y,0))
        if radial.length<1e-5:radial=Vector((0,-1,0))
        radial.normalize();hit,normal,_,_=support.ray_cast(Vector((0,0,p.z)),radial,1.5)
        if hit is None:return p.copy()
        if normal.dot(radial)<0:normal=-normal
        return hit+normal*offset
    n=len(hood.data.vertices)//2;uv={};original={}
    for poly in hood.data.polygons:
        if max(poly.vertices)>=n:continue
        for li,vi in zip(poly.loop_indices,poly.vertices):uv[vi]=hood.data.uv_layers.active.data[li].uv.copy()
    # Gather the *existing* lower cloth onto the upper back and shoulders.
    # Its final row turns inward within the same mesh; no added nape half-ring.
    for i,q in uv.items():
        old=hood.matrix_world@hood.data.vertices[i].co;original[i]=old.copy()
        weight=smooth((1.61-old.z)/.18)
        target=old.copy();target.z=1.32+.26*(old.z-1.20)
        target=seat(target,.004)
        p=old.lerp(target,weight)
        tuck=smooth((q.y-.91)/.09)*weight
        radial=Vector((p.x,p.y,0))
        if radial.length:radial.normalize();p-=radial*.008*tuck
        p.z+=.007*tuck
        delta=hood.matrix_world.inverted().to_3x3()@(p-old)
        hood.data.vertices[i].co+=delta;hood.data.vertices[i+n].co+=delta
    hem=a.material('Headwear / face edge237',(.045,.085,.10),.96)
    face=[p for _,p in cloth_boundary(hood,1,0)]
    a.tube('Pashmina / fine face hem237',face,.0014,.0013,hem,n=len(face),sides=6,taper=False,group='headgear')
    # The same woven cloth continues from the hood's rear/nape edge around
    # both shoulders. Its front tips underlap the crossed ends, completing a
    # single wrap instead of a disconnected partial ring or a bare nape.
    rear=cloth_boundary(hood,1,1)
    def collar(w,t):
        origin=interpolate(rear,w)
        lower=origin.copy();lower.z-=.052+.006*sin(pi*w)
        lower=seat(lower,.005)
        p=origin.lerp(lower,t)
        fit=smooth(t/.28)
        # Turn the two front corners under the continuing crossed lengths.
        # Preserve the exact hood attachment at t=0; avoid exposed square tabs.
        turn=(1-smooth(min(w,1-w)/.16))*smooth(t/.20)
        radius=Vector((p.x,p.y,0)).length
        theta=math.atan2(p.x,p.y)+(-1 if w<.5 else 1)*.40*turn
        p.x=radius*sin(theta);p.y=radius*cos(theta)
        p=p.lerp(seat(p,.0025+.0012*sin(pi*t)**2),fit)
        return p
    band=patch('Pashmina / continuous nape and shoulder wrap237',collar,96,16,mat)
    for loop in band.data.uv_layers.active.data:
        w,t=loop.uv;loop.uv=(w,1+t*.16)
    changed=0;roots=[];contact=[]
    for side in [-1,1]:
        edge=cloth_boundary(hood,0,0 if side<0 else 1)
        def root(w):return interpolate(edge,(w if side>0 else 1-w)*.175)
        origin=root(.5);upper=side>0
        endz=1.035 if side<0 else 1.055
        centers=[origin,Vector((side*.195,-.135,1.345)),Vector((side*.105,-.19,1.315)),Vector((0,-.21,1.295)),Vector((-side*.135,-.22,1.265)),Vector((-side*.175,-.245,1.205)),Vector((-side*.175,-.235,1.13)),Vector((-side*.165,-.21,endz))]
        rootB=(root(1)-root(0)).normalized()
        spans=[rootB,Vector((.48,0,-.88*side)),Vector((.45,0,-.89*side)),Vector((.40,0,-.92*side)),Vector((.67,0,-.74*side)),Vector((.94,0,-.34*side)),Vector((1,0,0)),Vector((1,0,0))]
        widths=[(root(1)-root(0)).length,.118,.114,.114,.12,.13,.135,.135]
        L=a.sample([p-b*w/2 for p,b,w in zip(centers,spans,widths)],128)
        RR=a.sample([p+b*w/2 for p,b,w in zip(centers,spans,widths)],128)
        L[0]=root(0);RR[0]=root(1)
        def sheet(w,t):
            j=min(126,int(t*127));f=t*127-j
            p=L[j].lerp(L[j+1],f).lerp(RR[j].lerp(RR[j+1],f),w)
            p+=(root(w)-root(0).lerp(root(1),w))*(1-smooth(t/.15))
            fit=smooth(t/.15)
            # Two woven sheets cross. Only the upper sheet gets one cloth
            # thickness of clearance where they overlap; no suspended knot.
            layer=.006*smooth((t-.15)/.08)*(1-smooth((t-.66)/.10)) if upper else 0
            folded=.0015*(1+sin(2*pi*w+.5*t))
            p=p.lerp(seat(p,.004+layer+folded),fit)
            p.z+=.002*sin(pi*w+.4*side)*smooth((t-.85)/.15)
            return p
        roots.append(max((sheet(w,0)-root(w)).length for w in np.linspace(0,1,25)))
        ob=patch('Pashmina / continuous crossed end237 '+str(side),sheet,24,127,mat)
        # Long-edge borders follow the scarf continuously out of the hood.
        for loop in ob.data.uv_layers.active.data:
            w,t=loop.uv;loop.uv=((0 if side<0 else 1)+side*.8*t,(w if side>0 else 1-w)*.175)
        for t in np.linspace(.18,.96,30):
            for w in [.15,.5,.85]:
                p=sheet(float(w),float(t));hit=actual.find_nearest(p)
                if hit[0] is not None:contact.append(float(hit[3]))
        thread=a.material('Headwear / fine fringe237',(.12,.17,.17),.96)
        for k in range(11):
            p=sheet((k+.5)/11,1)
            a.tube('Pashmina / free fringe237 '+str(side)+' '+str(k),[p,p+Vector((.001*sin(k),0,-.015-.002*cos(k)))],.0012,.0010,thread,n=6,sides=5,taper=False,group='headgear')
    now=u.object_geometry(s);assert all(now.get(k)==v for k,v in frozen.items()),'Protected model changed'
    assert max(roots)<1e-6
    assert all((hood.matrix_world@hood.data.vertices[i].co-original[i]).length<1e-6 for i in original if original[i].z>=1.61)
    key=build+'-'+top+'-pashmina237';u.camera(s,'front',512,True);parts=save(s,key,['headgear']);s=bpy.context.scene
    render(s,key,['front','profile','rear'] if quick else ['front','threequarter','profile','rightprofile','rear','top','underside'],size=384 if quick else 512,body=True)
    for angle in (['front','profile','rear'] if top==('open' if build=='Feminine' else 'tank') else []):
        u.camera(s,angle,768,True);s.camera.data.ortho_scale=1.35;s.camera.location.z-=.02;s.cycles.samples=16;s.render.filepath=str(P/'review1'/f'{key}-detail-{angle}.png');bpy.ops.render.render(write_still=True)
    return dict(source=str(P/'sources'/f'{key}.blend'),component=parts['headgear'],top=top,protected_neighbors_exact=True,upper_hood_exact_above=1.61,root_error=max(roots),surface_contact_median=float(np.median(contact)),surface_contact_p90=float(np.quantile(contact,.9)),construction='Hood nape continues into one shoulder-seated neck wrap, with two12-percent narrower crossing sections and10-percent narrower hanging ends. Ends underlap the same rear/side wrap; no independent half ring or bow. Top-specific fit retained.')

if __name__=='__main__':
    builds=next((v.split('=',1)[1].split(',') for v in sys.argv if v.startswith('--builds=')),['Feminine','Masculine'])
    tops=next((v.split('=',1)[1].split(',') for v in sys.argv if v.startswith('--tops=')),None)
    records=json.loads((P/'fits237.json').read_text()) if (P/'fits237.json').exists() else {}
    for build in builds:
        for top in (['open' if build=='Feminine' else 'tank'] if '--defaults' in sys.argv else tops or CAT237['builds'][build]['tops']):
            if top not in CAT237['builds'][build]['tops']:continue
            records.setdefault(build,{})[top]=run(build,top,'--quick' in sys.argv);u.dump(P/'fits237.json',records)
            print('PASH237',build,top,records[build][top]['surface_contact_median'],flush=True)
