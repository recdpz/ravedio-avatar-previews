"""Continuous, closed Bob volumes with explicit flow coordinates and styled fringes.

The principal surface is authored directly. No deformation of the older lock
meshes, voxel remesh, projected UVs or Boolean intersections is involved.
"""
from pathlib import Path
import sys

import bpy
import bmesh
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'333/tools'))
from build_curtain_bob import strand, sample_path
from study_bob import CENTER, TO_BLENDER, normalized, ease


def material_copy(source):
    result=source.copy()
    result.name='Hair / brushed sculpted brown'
    result.use_fake_user=True
    for node in result.node_tree.nodes:
        if node.type=='NORMAL_MAP':
            node.inputs['Strength'].default_value=.55
        if node.type=='BSDF_PRINCIPLED':
            node.inputs['Coat Weight'].default_value=.32
            node.inputs['Coat Roughness'].default_value=.27
    return result


def meridians(theta,t,style):
    """A continuous shell, including the underturned perimeter of the cut."""
    face=np.abs((theta+np.pi)%(2*np.pi)-np.pi)
    opening=.34+.66*ease((face-.58)/.92)
    progress=t*opening
    # A rounded crown flows into the bob body, then under at the ends.
    profile=sample_path(((0,2.214,0),(.156,2.184,0),(.300,2.100,0),
                         (.391,1.951,0),(.406,1.749,0),(.368,1.578,0),
                         (.318,1.510,0)),401)
    index=progress*400
    r=np.interp(index,np.arange(401),profile[:,0])
    y=np.interp(index,np.arange(401),profile[:,1])
    lower=ease((progress-.30)/.65)
    hem=ease((progress-.88)/.12)
    if style=='blowout':
        back=ease((face-1.35)/.90)
        drift=(.48*np.sin(1.05*np.pi*progress)+.08*progress)*back
        drift+=.14*np.sin(np.pi*progress)*np.sin(theta)*(1-back)
        r+=.014*np.sin(np.pi*progress)**2
        y-=.055*lower
        offset=.075*(1-progress)**2
    elif style=='waves':
        phase=3.25*np.pi*progress+.42*np.sin(5*theta)
        drift=.23*np.sin(phase)*lower
        r+=.049*np.sin(phase+.6)*lower
        y-=.012*lower
        offset=0
    else:
        drift=-.32*np.sin(np.pi*progress)+.05*np.sin(theta)*progress
        r-=.009*lower
        y+=lower*(.062-.040*np.sin(theta))
        offset=-.082*(1-progress)**2
    angle=theta+drift
    # Broad shallow sections; finer brushed strands are texture detail.
    ridges=.0042*np.cos(17*theta+.6*np.sin(np.pi*progress))*np.sin(np.pi*progress)**1.4
    r+=ridges
    y+=hem*(.0055*np.cos(17*theta+.3)+.003*np.sin(7*theta))
    points=np.stack((r*np.sin(angle)+offset,y,CENTER[2]+r*np.cos(angle)),axis=-1)
    relative=points-CENTER
    distance=np.linalg.norm(relative,axis=-1)
    points=CENTER+relative*np.maximum(1,.397/np.maximum(distance,1e-8))[...,None]
    return points


def body(style,material):
    rows,columns=144,256
    theta=np.broadcast_to(np.arange(columns)[None,:]*2*np.pi/columns,(rows,columns))
    t=np.broadcast_to(np.linspace(.0008,1,rows)[:,None],(rows,columns))
    outer=meridians(theta,t,style)
    # Recessed continuous coverage. The visible cut is carried by the broader
    # overlapping sections below, rather than a single exposed helmet surface.
    outer-=normalized(outer-CENTER)*.012
    outer[:,:,1]+=.035*ease((t-.7)/.3)
    face=np.abs((theta+np.pi)%(2*np.pi)-np.pi)
    blend=(1-ease((face-.65)/.55))*ease((t-.42)/.40)
    relative=outer-CENTER
    radius=np.linalg.norm(relative,axis=-1)
    outer=CENTER+normalized(relative)*(radius*(1-blend)+.376*blend)[...,None]
    down=normalized(np.gradient(outer,axis=0))
    across=normalized(np.roll(outer,-1,axis=1)-np.roll(outer,1,axis=1))
    normal=normalized(np.cross(down,across))
    if np.mean(np.sum(normal*(outer-CENTER),axis=-1))<0:
        normal=-normal
    thickness=.018*(.4+.6*ease(t/.10))
    inner=outer-normal*thickness[...,None]
    relative=inner-CENTER
    radius=np.linalg.norm(relative,axis=-1)
    inner=CENTER+normalized(relative)*(radius*(1-blend)+.370*blend)[...,None]
    # Keep the inset surface smooth and close the hem with a bevel, never a
    # separate waistband-like ring or projected row of caps.
    middle=(outer[-1]+inner[-1])*.5+down[-1]*.006
    points=np.concatenate((outer.reshape(-1,3),inner.reshape(-1,3),middle))
    count=rows*columns
    vertices=(points@TO_BLENDER).tolist()
    faces=[]
    for row in range(rows-1):
        for col in range(columns):
            a=row*columns+col
            b=row*columns+(col+1)%columns
            faces.append((a,b,b+columns,a+columns))
            faces.append((a+count,a+columns+count,b+columns+count,b+count))
    for col in range(columns):
        nxt=(col+1)%columns
        a=(rows-1)*columns+col
        b=(rows-1)*columns+nxt
        faces.extend(((b,a,2*count+col,2*count+nxt),
                      (2*count+nxt,2*count+col,a+count,b+count),
                      (col,nxt,nxt+count,col+count)))
    mesh=bpy.data.meshes.new('Bob / continuous styled shell')
    mesh.from_pydata(vertices,[],faces)
    mesh.materials.append(material)
    mesh.update()
    bm=bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    mesh.polygons.foreach_set('use_smooth',np.ones(len(mesh.polygons),dtype=bool))
    layer=mesh.uv_layers.new(name='Lock flow')
    # Texture lines follow these meridians, rather than a closest-surface UV
    # transfer that breaks direction at joins between unrelated donor pieces.
    uv=np.column_stack((theta.ravel()/(2*np.pi)*12,t.ravel()))
    uv=np.concatenate((uv,uv,uv[-columns:]))
    coordinates=[]
    for polygon in mesh.polygons:
        ids=np.array(polygon.vertices)
        coords=uv[ids].copy()
        cols=ids%columns
        if cols.max()-cols.min()>columns//2:
            coords[cols<columns//2,0]+=12
        coordinates.extend(coords)
    layer.data.foreach_set('uv',np.array(coordinates,dtype=np.float32).ravel())
    obj=bpy.data.objects.new('Hair / continuous Bob volume',mesh)
    obj['component269']='hair'
    bpy.context.scene.collection.objects.link(obj)
    return obj


def sections(style,material):
    count=23
    rows,columns=128,25
    v=np.linspace(.004,1,rows)
    cross=np.linspace(-1,1,columns)
    for section in range(count):
        center=2*np.pi*section/count
        if abs((center+np.pi)%(2*np.pi)-np.pi)<.78:
            continue
        # Each section has a narrow rounded finish, varied in length by only
        # millimetres. The profiles merge at the crown and separate at the hem.
        cap=np.sqrt(np.maximum(.0001,1-ease((v-.935)/.065)))
        theta=center+.164*cross[None,:]*cap[:,None]
        t=np.broadcast_to(v[:,None],theta.shape).copy()
        t*=1+.018*np.sin(section*2.1)*ease((t-.7)/.3)
        outer=meridians(theta,np.minimum(t,1),style)
        tangent=normalized(np.gradient(outer,axis=0))
        across=normalized(np.gradient(outer,axis=1))
        normal=normalized(np.cross(tangent,across))
        if np.mean(np.sum(normal*(outer-CENTER),axis=-1))<0:
            normal=-normal
        arch=(.010*(1-cross[None,:]**2)*np.sin(np.pi*v[:,None]*.86)**.7)
        outer+=normal*arch[...,None]
        inner=outer-normal*(.013*cap[:,None]+.0004)[...,None]
        points=np.concatenate((outer.reshape(-1,3),inner.reshape(-1,3)))
        n=rows*columns
        faces=[]
        for i in range(rows-1):
            for j in range(columns-1):
                a=i*columns+j
                faces.extend(((a,a+1,a+1+columns,a+columns),
                              (a+n,a+columns+n,a+columns+1+n,a+1+n)))
        boundary=[*range(columns)]
        boundary += [(i+1)*columns-1 for i in range(1,rows)]
        boundary += list(range(n-2,n-columns-1,-1))
        boundary += [i*columns for i in reversed(range(1,rows-1))]
        for i,a in enumerate(boundary):
            b=boundary[(i+1)%len(boundary)]
            faces.append((b,a,a+n,b+n))
        mesh=bpy.data.meshes.new(f'Bob / flow section {section}')
        mesh.from_pydata((points@TO_BLENDER).tolist(),[],faces)
        mesh.materials.append(material)
        mesh.update()
        bm=bmesh.new();bm.from_mesh(mesh)
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        bm.to_mesh(mesh);bm.free()
        mesh.polygons.foreach_set('use_smooth',np.ones(len(mesh.polygons),dtype=bool))
        layer=mesh.uv_layers.new(name='Lock flow')
        uv=np.array([(j/(columns-1),i/(rows-1)) for i in range(rows) for j in range(columns)]*2)
        indices=np.empty(len(mesh.loops),dtype=np.int32)
        mesh.loops.foreach_get('vertex_index',indices)
        layer.data.foreach_set('uv',uv[indices].astype(np.float32).ravel())
        obj=bpy.data.objects.new(f'Hair / styled section {section}',mesh)
        obj['component269']='hair'
        bpy.context.scene.collection.objects.link(obj)


def style_front(style,material):
    if style=='blowout':
        path=np.array(((.10,2.122,.162),(.115,2.180,.216),(-.045,2.210,.250),
                       (-.260,2.130,.298),(-.392,1.993,.290),
                       (-.420,1.775,.215),(-.358,1.556,.150),(-.282,1.469,.101)))
        path[:,2]+=CENTER[2]
        for j in range(4):
            p=path.copy()
            p[:,2]-=.046*j
            p[:,1]-=.012*j*np.linspace(0,1,len(p))
            strand(f'Blowout / swept section {j}',p,
                   (.006,.082,.088,.076,.034),(.016,.029,.030,.025,.011),material,j*.3)
        for j in range(3):
            p=np.array(((.115,2.153,.155),(.239,2.093,.265),
                        (.353,1.951,.226),(.395,1.723,.135),(.339,1.532,.093)))
            p[:,2]+=CENTER[2]-.032*j
            strand(f'Blowout / short side {j}',p,
                   (.006,.062,.061,.049,.027),(.010,.022,.023,.019,.010),material,j*.4)
    elif style=='waves':
        for side in (-1,1):
            for j in range(3):
                p=np.array(((side*.012,2.182,.110),(side*.055,2.144,.245),
                    (side*.128,2.066,.315),(side*.224,1.991,.292),
                    (side*.310,1.933,.220)))
                p[:,2]+=CENTER[2]-.031*j
                p[:,1]+=.009*j
                strand(f'Waves / curtain {side} {j}',p,
                       (.006,.061,.068,.059,.025),(.011,.020,.022,.019,.010),material,j*.4)
            for j in range(3):
                angle=side*(1.19+j*.29)
                t=np.array((.35,.50,.64,.77,.90,1.0))
                p=meridians(np.full(t.shape,angle),t,style)
                extra=np.array((-.025,-.016,-.012,-.008,-.005,-.003))
                p+=normalized(p-CENTER)*extra[:,None]
                p[-2:,1]-=(.012,.018)
                strand(f'Waves / loose side layer {side} {j}',p,
                       (.021,.041,.044,.036,.017),(.007,.013,.014,.012,.005),material,j*.7)
    else:
        path=np.array(((-.144,2.155,.135),(-.050,2.180,.230),(.130,2.094,.314),
                       (.278,1.965,.275),(.369,1.767,.170),
                       (.345,1.559,.120),(.301,1.490,.087)))
        path[:,2]+=CENTER[2]
        for j in range(4):
            p=path.copy()
            p[:,2]-=.039*j
            p[-2:,1]+=.020*j
            strand(f'Asymmetric / diagonal section {j}',p,
                   (.006,.075,.086,.065,.030),(.012,.025,.029,.025,.009),material,j*.4)


def build(scene,style):
    source=next(o for o in scene.objects if o.type=='MESH' and
                o.get('component269')=='hair' and 'Bob / side sweep' in o.data.name)
    material=material_copy(source.data.materials[0])
    for obj in list(scene.objects):
        if obj.get('component269')=='hair':
            bpy.data.objects.remove(obj,do_unlink=True)
    main=body(style,material)
    sections(style,material)
    style_front(style,material)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in scene.objects:
        if obj.type=='MESH' and obj.get('component269')=='hair':
            obj.select_set(True)
    bpy.context.view_layer.objects.active=main
    bpy.ops.object.join()
    return main
