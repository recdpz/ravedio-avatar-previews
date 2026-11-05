"""Narrow existing239 free ends while freezing its approved hood and joins."""
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

def run(build,top,quick=False):
    bpy.ops.wm.open_mainfile(filepath=str(BASE/'sources'/f'{build}-{top}-pashmina239.blend'))
    s=bpy.context.scene
    ob=next(o for o in s.objects if 'joined hood wrap and ends239' in o.name)
    frozen={k:v for k,v in u.object_geometry(s).items() if k!=ob.name and 'free fringe239' not in k}
    n=len(ob.data.vertices)//2;assert n*2==len(ob.data.vertices)
    old=[ob.matrix_world@v.co for v in ob.data.vertices]
    assert max((old[i]-old[i+n]).length for i in range(n))<.015
    uv={}
    for face in ob.data.polygons:
        if max(face.vertices)>=n:continue
        for li,vi in zip(face.loop_indices,face.vertices):uv[vi]=ob.data.uv_layers.active.data[li].uv.copy()
    rows={-1:{},1:{}};params={}
    for i,q in uv.items():
        if q.x<-.8*.4:side=-1;t=-q.x/.8;w=1-q.y/.175
        elif q.x>1+.8*.4:side=1;t=(q.x-1)/.8;w=q.y/.175
        else:continue
        j=int(round(t*127));assert 51<=j<=127 and -.00001<=w<=1.00001
        rows[side].setdefault(j,[]).append((float(w),old[i]));params[i]=(side,j,float(w))
    assert all(len(r)==77 for r in rows.values())
    for r in rows.values():
        for row in r.values():row.sort(key=lambda p:p[0])
    inv=ob.matrix_world.inverted().to_3x3();moved=set();widths={}
    for i,(side,j,w) in params.items():
        scale=1-(1-FACTOR)*smooth((j/127-.40)/.22)
        target=interpolate(rows[side][j],.5+(w-.5)*scale);delta=target-old[i]
        for k in [i,i+n]:ob.data.vertices[k].co+=inv@delta;moved.add(k)
    for side in [-1,1]:
        row=rows[side][127];before=(interpolate(row,1)-interpolate(row,0)).length
        after=(interpolate(row,.5+.5*FACTOR)-interpolate(row,.5-.5*FACTOR)).length
        widths[str(side)]=dict(before=before,after=after,ratio=after/before)
        assert .74<after/before<.83
    # Tassels translate with their own attached cloth sample, retaining their
    # original small width and length rather than squashing each tassel.
    for tassel in [o for o in s.objects if 'free fringe239' in o.name]:
        parts=tassel.name.split();side=int(parts[-2]);k=int(parts[-1]);w=(k+.5)/11
        delta=interpolate(rows[side][127],.5+(w-.5)*FACTOR)-interpolate(rows[side][127],w)
        local=tassel.matrix_world.inverted().to_3x3()@delta
        for v in tassel.data.vertices:v.co+=local
    assert all((ob.matrix_world@ob.data.vertices[i].co-old[i]).length<1e-9 for i in range(len(old)) if i not in moved),'Approved hood/wrap/joins changed'
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(len(e.link_faces)==2 for e in bm.edges),'Open cloth edge';bm.to_mesh(ob.data);bm.free()
    assert all(u.object_geometry(s).get(k)==v for k,v in frozen.items()),'Protected neighbor changed'
    key=f'{build}-{top}-pashmina240';parts=save(s,key,['headgear']);s=bpy.context.scene
    render(s,key,['front','threequarter','profile'] if quick else ['front','threequarter','profile','rightprofile','rear','top','underside'],size=384 if quick else 256,body=True)
    baseline=json.loads((BASE/'fits239.json').read_text())[build][top]['joined_surface']
    return dict(source=str(P/'sources'/f'{key}.blend'),component=parts['headgear'],top=top,protected_neighbors_exact=True,joined_surface=baseline,approved239_upper_cloth_exact=True,unchanged_main_vertices=len(old)-len(moved),moved_tail_vertices=len(moved),width_factor=FACTOR,end_widths=widths,method='Resample existing cloth row curves below t0.40; full narrowing by t0.62; translate fringe anchors with their fabric. Preserve length, support curvature, upper cloth, shared seams, UVs and thickness.')

if __name__=='__main__':
    catalogue=json.loads((R/'239/catalogue239.json').read_text());records=json.loads((P/'fits240.json').read_text()) if (P/'fits240.json').exists() else {}
    builds=['Feminine'] if '--draft' in sys.argv else ['Feminine','Masculine']
    for build in builds:
        for top in (['open'] if '--draft' in sys.argv else catalogue['builds'][build]['tops']):
            records.setdefault(build,{})[top]=run(build,top,'--draft' in sys.argv);u.dump(P/'fits240.json',records);print('NARROW240',build,top,flush=True)
