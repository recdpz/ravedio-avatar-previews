"""Narrow239 collarbone/chest crossings; freeze its full hanging ends."""
import sys,json,math
from pathlib import Path
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue235')
import common235 as c
c.P=Path(__file__).parent
from common235 import *
import bmesh
BASE=P.parent/'catalogue239'
FACTOR=.78

def interpolate(row,w):
    for (lo,p),(hi,q) in zip(row,row[1:]):
        if lo-1e-6<=w<=hi+1e-6:return p.lerp(q,max(0,min(1,(w-lo)/(hi-lo))))
    return row[0][1].copy() if w<row[0][0] else row[-1][1].copy()

def strength(t):return smooth((t-.20)/.10)*(1-smooth((t-.50)/.22))

def run(build,top,quick=False):
    bpy.ops.wm.open_mainfile(filepath=str(BASE/'sources'/f'{build}-{top}-pashmina239.blend'))
    s=bpy.context.scene;ob=next(o for o in s.objects if 'joined hood wrap and ends239' in o.name)
    frozen={k:v for k,v in u.object_geometry(s).items() if k!=ob.name}
    n=len(ob.data.vertices)//2;assert n*2==len(ob.data.vertices)
    old=[ob.matrix_world@v.co for v in ob.data.vertices];assert max((old[i]-old[i+n]).length for i in range(n))<.015
    uv={}
    for face in ob.data.polygons:
        if max(face.vertices)>=n:continue
        for li,vi in zip(face.loop_indices,face.vertices):uv[vi]=ob.data.uv_layers.active.data[li].uv.copy()
    rows={-1:{},1:{}};params={};ends=[]
    for i,q in uv.items():
        if q.x<-.8*.18:side=-1;t=-q.x/.8;w=1-q.y/.175
        elif q.x>1+.8*.18:side=1;t=(q.x-1)/.8;w=q.y/.175
        else:continue
        j=int(round(t*127));assert 23<=j<=127 and -.00001<=w<=1.00001
        if j/127>=.72:ends.extend([i,i+n])
        if strength(j/127)<=1e-8:continue
        rows[side].setdefault(j,[]).append((float(w),old[i]));params[i]=(side,j,float(w))
    assert all(len(r)>50 for r in rows.values())
    for r in rows.values():
        for row in r.values():row.sort(key=lambda p:p[0])
    inv=ob.matrix_world.inverted().to_3x3();moved=set();upper_edge=[];widths={}
    for i,(side,j,w) in params.items():
        anchor=1. if side<0 else 0.
        # Keep the top/inner boundary fixed: reduce coverage of the shirt
        # from the lower edge, preserving the approved neck-opening shape.
        if abs(w-anchor)<1e-6:upper_edge.extend([i,i+n]);continue
        scale=1-(1-FACTOR)*strength(j/127)
        target=interpolate(rows[side][j],anchor+(w-anchor)*scale);delta=target-old[i]
        for k in [i,i+n]:ob.data.vertices[k].co+=inv@delta;moved.add(k)
    for side in [-1,1]:
        j=50;row=rows[side][j];anchor=1. if side<0 else 0.
        before=(interpolate(row,1)-interpolate(row,0)).length
        a=anchor+(0-anchor)*FACTOR;b=anchor+(1-anchor)*FACTOR
        after=(interpolate(row,a)-interpolate(row,b)).length
        widths[str(side)]=dict(at_t=j/127,before=before,after=after,ratio=after/before)
        assert .72<after/before<.85
    assert all((ob.matrix_world@ob.data.vertices[i].co-old[i]).length<1e-9 for i in range(len(old)) if i not in moved),'Protected239 cloth changed'
    assert ends and upper_edge and all(i not in moved for i in ends+upper_edge)
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(len(e.link_faces)==2 for e in bm.edges);bm.to_mesh(ob.data);bm.free()
    assert all(u.object_geometry(s).get(k)==v for k,v in frozen.items()),'Neighbor or fringe changed'
    key=f'{build}-{top}-pashmina241';parts=save(s,key,['headgear']);s=bpy.context.scene
    render(s,key,['front','threequarter','profile'],size=384 if quick else 256,body=True)
    joined=json.loads((BASE/'fits239.json').read_text())[build][top]['joined_surface']
    return dict(source=str(P/'sources'/f'{key}.blend'),component=parts['headgear'],top=top,protected_neighbors_exact=True,joined_surface=joined,hood_and_joins_exact=True,inner_top_edges_exact=True,lower_ends_exact239=True,fringe_exact239=True,unchanged_main_vertices=len(old)-len(moved),crossing_widths=widths,width_factor=FACTOR,method='One-sided row resampling toward the upper/inner edge between t0.20 and0.72. All lower-end vertices and fringe remain exactly239.')

if __name__=='__main__':
    cat=json.loads((R/'239/catalogue239.json').read_text());records=json.loads((P/'fits241.json').read_text()) if (P/'fits241.json').exists() else {}
    for build in (['Feminine'] if '--draft' in sys.argv else ['Feminine','Masculine']):
        for top in (['open'] if '--draft' in sys.argv else cat['builds'][build]['tops']):
            records.setdefault(build,{})[top]=run(build,top,'--draft' in sys.argv);u.dump(P/'fits241.json',records);print('NARROW241',build,top,flush=True)
