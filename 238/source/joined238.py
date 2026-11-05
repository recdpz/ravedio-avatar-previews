"""Stitch actual cloth boundaries before normals/thickness are evaluated.

Boundary subdivision includes both original hood vertices and incoming panel
samples. No T junctions, coincident disconnected edges, or hidden filler strips.
"""
import sys,math
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue235')
from common235 import *
import bmesh

FRONT=.008
BACK=.175

def hood_root(hood,side):
    """A continuous root along lower face edge AND adjoining hood side."""
    n=len(hood.data.vertices)//2;uv={}
    for poly in hood.data.polygons:
        if max(poly.vertices)>=n:continue
        for li,vi in zip(poly.loop_indices,poly.vertices):uv[vi]=hood.data.uv_layers.active.data[li].uv.copy()
    def edge(axis,value):return sorted([(float(q[1-axis]),hood.matrix_world@hood.data.vertices[i].co,q.copy()) for i,q in uv.items() if abs(q[axis]-value)<1e-5],key=lambda item:item[0])
    def at(edge,q):
        for (lo,p,a),(hi,r,b) in zip(edge,edge[1:]):
            if lo<=q<=hi:
                t=(q-lo)/(hi-lo);return p.lerp(r,t),a.lerp(b,t)
        return edge[-1][1].copy(),edge[-1][2].copy()
    side_edge=edge(0,0 if side<0 else 1);face=edge(1,0)
    if side<0:
        items=[at(side_edge,BACK)]+[(p,q) for v,p,q in reversed(side_edge) if v<BACK-1e-6]
        items += [(p,q) for v,p,q in face if 1e-6<v<FRONT-1e-6]+[at(face,FRONT)]
    else:
        items=[at(face,1-FRONT)]+[(p,q) for v,p,q in face if v>1-FRONT+1e-6]
        items += [(p,q) for v,p,q in side_edge if 1e-6<v<BACK-1e-6]+[at(side_edge,BACK)]
    length=[0.]
    for (p,q),(r,b) in zip(items,items[1:]):length.append(length[-1]+(r-p).length)
    return [(d/length[-1],p,q) for d,(p,q) in zip(length,items)]

def sample_root(description,w):
    for (lo,p,a),(hi,r,b) in zip(description,description[1:]):
        if lo<=w<=hi:
            t=(w-lo)/(hi-lo);return p.lerp(r,t),a.lerp(b,t)
    return description[-1][1].copy(),description[-1][2].copy()

def join_cloth(hood,panels,mat,seat):
    n=len(hood.data.vertices)//2;layer=hood.data.uv_layers.active
    outer=[list(p.vertices) for p in hood.data.polygons if max(p.vertices)<n]
    old_uv={}
    for poly in hood.data.polygons:
        if max(poly.vertices)>=n:continue
        for li,vi in zip(poly.loop_indices,poly.vertices):old_uv[vi]=layer.data[li].uv.copy()
    used=sorted({i for f in outer for i in f});mapping={old:new for new,old in enumerate(used)}
    verts=[hood.matrix_world@hood.data.vertices[i].co for i in used]
    tex=[old_uv[i].copy() for i in used];faces=[];splits={};seams=set();seam_keys=set();panel_rows={};hood_ids=set(mapping.values());upper={mapping[i]:verts[mapping[i]].copy() for i in used if verts[mapping[i]].z>=1.61}
    def loop(axis,value):
        result=[(float(old_uv[i][1-axis]),mapping[i]) for i in used if abs(old_uv[i][axis]-value)<1e-5]
        result.sort();assert len(result)>10;return result
    def point_on(edge,q):
        for value,index in edge:
            if abs(value-q)<1e-6:return index
        for (lo,ia),(hi,ib) in zip(edge,edge[1:]):
            if lo<q<hi:
                f=(q-lo)/(hi-lo);key=tuple(sorted((ia,ib)));ratio=f if ia<ib else 1-f
                for previous,index in splits.get(key,[]):
                    if abs(previous-ratio)<1e-6:return index
                index=len(verts);verts.append(verts[ia].lerp(verts[ib],f));tex.append(tex[ia].lerp(tex[ib],f));hood_ids.add(index)
                splits.setdefault(key,[]).append((ratio,index));return index
        raise ValueError(('Unmatched hood boundary',q))
    for panel in panels:
        nu=int(panel['cloth_nu238']);nv=int(panel['cloth_nv238']);band='nape and shoulder' in panel.name
        side=-1 if panel.name.endswith('-1') else 1
        description=None if band else hood_root(hood,side)
        candidates=sorted(([max(0,min(1,q)) for q,_ in loop(1,1)] if band else [w for w,p,q in description])+[i/nu for i in range(nu+1)])
        params=[];seen=set()
        for w in candidates:
            if band:index=point_on(loop(1,1),w)
            else:
                p,q=sample_root(description,w)
                index=point_on(loop(0,0 if side<0 else 1),float(q.y)) if abs(q.x-(0 if side<0 else 1))<1e-6 else point_on(loop(1,0),float(q.x))
            if index not in seen:params.append((w,index));seen.add(index)
        params.sort();rows=[[index for w,index in params]];seams.update(rows[0])
        assert len(rows[0])==len(set(rows[0])),'Repeated shared-boundary vertex'
        seam_keys.update(tuple(sorted((a,b))) for a,b in zip(rows[0],rows[0][1:]))
        for j in range(1,nv+1):
            row=[];t=j/nv
            for w,_ in params:
                q=min(nu,max(0,w*nu));lo=min(nu-1,int(q));f=q-lo
                p0=panel.matrix_world@panel.data.vertices[j*(nu+1)+lo].co;p1=panel.matrix_world@panel.data.vertices[j*(nu+1)+lo+1].co
                index=len(verts);verts.append(p0.lerp(p1,f))
                if band:tex.append(Vector((w,1+t*.16)))
                else:
                    root_uv=sample_root(description,w)[1];standard=Vector(((0 if side<0 else 1)+side*.8*t,(w if side>0 else 1-w)*BACK));tex.append(root_uv.lerp(standard,smooth(t/.18)))
                row.append(index)
            rows.append(row)
        for arow,brow in zip(rows,rows[1:]):
            for i in range(len(params)-1):faces.append([arow[i],arow[i+1],brow[i+1],brow[i]])
        panel_rows['band' if band else side]=rows
    for original in outer:
        src=[mapping[i] for i in original];face=[]
        for a0,b0 in zip(src,src[1:]+src[:1]):
            face.append(a0);key=tuple(sorted((a0,b0)));extra=sorted(splits.get(key,[]),reverse=a0>b0)
            face.extend(i for f,i in extra)
        faces.append(face)
    # Connected vertices share their normals. Mild Taubin relaxation is
    # confined to the junction and its immediate neighbors; upper hood stays.
    adjacency=[set() for _ in verts]
    for f in faces:
        for x,y in zip(f,f[1:]+f[:1]):adjacency[x].add(y);adjacency[y].add(x)
    weights={i:1.0 for i in seams}
    for i in list(seams):
        for j in adjacency[i]:weights[j]=max(weights.get(j,0),.35)
    for i in upper:weights.pop(i,None)
    for factor in [.22,-.23,.22,-.23]:
        changes={i:(sum((verts[j] for j in adjacency[i]),Vector())/len(adjacency[i])-verts[i])*factor*w for i,w in weights.items() if adjacency[i]}
        for i,delta in changes.items():verts[i]+=delta
    ob=a.mesh('Pashmina / joined hood wrap and ends238',verts,faces,mat,'headgear')
    uv=ob.data.uv_layers.new(name='Continuous cloth UV238')
    for poly in ob.data.polygons:
        for li,vi in zip(poly.loop_indices,poly.vertices):uv.data[li].uv=tex[vi]
    bm=bmesh.new();bm.from_mesh(ob.data);bm.verts.ensure_lookup_table();bm.edges.ensure_lookup_table()
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    if sum(f.normal.dot(f.calc_center_median()-a.C) for f in bm.faces if f.calc_center_median().z>1.8)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
    assert all(len(e.link_faces) in [1,2] for e in bm.edges),'Non-manifold cloth junction'
    seam_edges=[e for e in bm.edges if tuple(sorted(v.index for v in e.verts)) in seam_keys]
    assert len(seam_edges)==len(seam_keys),'Missing sewn boundary edge'
    assert seam_edges and all(len(e.link_faces)==2 for e in seam_edges),'Open hood/fold seam'
    remaining=set(bm.verts);islands=0
    while remaining:
        islands+=1;pending=[remaining.pop()]
        while pending:
            v=pending.pop()
            for e in v.link_edges:
                other=e.other_vert(v)
                if other in remaining:remaining.remove(other);pending.append(other)
    assert islands==1,('Disconnected main cloth',islands)
    bm.to_mesh(ob.data);bm.free()
    assert all((ob.data.vertices[i].co-p).length<1e-6 for i,p in upper.items())
    solid=ob.modifiers.new('One continuous woven thickness238','SOLIDIFY');solid.thickness=.003;solid.offset=-1
    hem_ob=next(o for o in bpy.context.scene.objects if 'fine face hem238' in o.name)
    hem_mat=hem_ob.data.materials[0];face_ids=sorted([(tex[i].x,i) for i in hood_ids if abs(tex[i].y)<1e-5 and FRONT-1e-6<=tex[i].x<=1-FRONT+1e-6])
    hem_path=[row[-1] for row in reversed(panel_rows[-1][:24])]+[i for q,i in face_ids[1:]]+[row[0] for row in panel_rows[1][1:24]]
    a.tube('Pashmina / continuous face to fold hem238',[verts[i] for i in hem_path],.0014,.0013,hem_mat,n=len(hem_path),sides=6,taper=False,group='headgear');u.delete(hem_ob)
    for old in [hood,*panels]:u.delete(old)
    return dict(surface_islands=islands,shared_boundary_vertices=len(seams),internal_seam_edges=len(seam_edges),open_seam_edges=0,upper_hood_exact=True,continuous_uv=True,single_thickness=True)
