"""Sculpt the fringe and crown as a continuous surface with feathered edges."""
import sys
from pathlib import Path

import bpy
import numpy as np

REV = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(REV.parent/"277/tools"))
from refine_fringe import build_fringe
from build_hair import (BANGS_COLOR, GOLD_COLOR, CENTER, RADIUS, bangs_body, ease,
                        fit_crown, hair_material, unit)

# Angular center and width at the crown edge, tip height, and sideward drift.
# Close pairs share a direction, with open spaces left between the groups.
FEATHERS = (
    (-.636,.049,1.939,-.028),(-.568,.056,1.947,-.034),
    (-.492,.067,1.962,-.031),(-.421,.039,1.986,-.021),
    (-.333,.048,1.978,-.026),(-.262,.044,1.993,-.014),
    (-.181,.066,1.975,.014),(-.106,.042,1.991,.021),
    (-.040,.046,1.980,.045),(.036,.067,1.953,.055),
    (.112,.042,1.979,.049),(.186,.055,1.972,.054),
    (.264,.053,1.991,.046),(.344,.068,1.967,.058),
    (.428,.044,1.981,.052),(.499,.065,1.953,.050),
    (.591,.057,1.939,.036),(.654,.043,1.942,.024),
)
ANGLE_GRID = np.linspace(-np.pi,np.pi,193)[:-1]
FRONT = .79


def shape_edge(a, original):
    # Root heights trace a small sweep across the forehead. The temple
    # contour merges into the existing side locks.
    wave = 2.113 + .011*np.sin(a*6+.7) + .006*np.sin(a*13-1.2)
    wave -= .014*ease((np.abs(a)-.46)/.24)
    front = 1-ease((np.abs(a)-.66)/.18)
    return original + front*(wave-original)


def cubic(t, a, b, c, d):
    s = 1-t
    return (s*s*s)*a + (3*s*s*t)*b + (3*s*t*t)*c + t*t*t*d


def feather_rows(anchor, previous, end, drift, hat, index):
    count = anchor.shape[0]
    mid = count//2
    start = anchor[mid]
    start_r = np.linalg.norm((start-CENTER)[[0,2]])
    start_a = np.arctan2(start[0],start[2]-CENTER[2])
    closed = hat in {"cap","beanie","bucket","cowboy"}
    if closed:
        end += .010
    end_a = start_a+drift
    tip_r = np.sqrt(max(0.,RADIUS**2-(end-CENTER[1])**2))+.005
    t = np.linspace(0,1,39)
    # Follow the crown tangent into the roll and ease the ends inward.
    step = unit(start-previous[mid])
    y = cubic(t,start[1],start[1]+.062*step[1],end+.072,end)
    rise = .402 if closed else .424-.007*ease((abs(start_a)-.37)/.29)
    r = cubic(t,start_r,start_r+.062*np.dot(step[[0,2]], [np.sin(start_a),np.cos(start_a)]),
              rise,tip_r)
    tip_x = tip_r*np.sin(end_a)
    x = cubic(t,start[0],start[0]+.062*step[0],tip_x+.008*np.sin(index*.79),tip_x)
    axis = np.column_stack((x,y,CENTER[2]+np.sqrt(np.maximum(.000001,r*r-x*x))))
    tangent = unit(np.gradient(axis,axis=0))
    side = unit(np.cross(tangent,unit(axis-CENTER)))
    side *= np.sign((anchor[-1]-anchor[0]) @ side[0])
    normal = unit(np.cross(side,tangent))
    normal *= np.sign(normal[0]@(start-CENTER))
    u = np.linspace(-1,1,count)
    root_offsets = anchor-start
    half_width = .5*np.linalg.norm(anchor[-1]-anchor[0])
    taper = (1+.13*np.sin(np.pi*t))*(1-(.63+.06*np.sin(index*2.2))*ease((t-.20)/.77))
    taper *= np.sqrt(np.maximum(.025,1-np.clip((t-.961)/.039,0,1)**2))
    width = half_width*taper
    crown = (1-u*u)*(1+.13*np.sin(u*6.8+index))
    relief = .0026*np.sin(np.pi*t)**1.26
    airy = axis[:,None,:]+width[:,None,None]*u[None,:,None]*side[:,None,:]
    airy += (relief[:,None]*crown[None,:])[:,:,None]*normal[:,None,:]
    # The first row uses the actual crown vertices. A soft cross-section
    # transition keeps the width and surface tangent continuous at the root.
    start_shape = axis[:,None,:] + root_offsets[None,:,:]*taper[:,None,None]
    blend = ease(t/.23)[:,None,None]
    points = (1-blend)*start_shape + blend*airy
    points[0] = anchor
    return points


def crown_grid(hat):
    samples = [np.linspace(a-w/2,a+w/2,9) for a,w,_,_ in FEATHERS]
    # Refine only the front, including all the feather junction vertices.
    front = np.linspace(-FRONT,FRONT,73)
    angles = np.unique(np.concatenate((ANGLE_GRID[np.abs(ANGLE_GRID)>FRONT],front,*samples)))
    points, fraction, shade = bangs_body(hat,hairline=shape_edge,angles=angles)
    # Keep the front surface round all the way to the shared edge.
    a = np.arctan2(points[:,:,0],points[:,:,2]-CENTER[2])
    y = points[:,:,1]
    mask = (1-ease((np.abs(a)-.58)/.30))*ease((2.208-y)/.057)
    shell_radius = .411 - .013*ease((2.197-y)/.105)
    radial = np.sqrt(np.maximum(.000001,shell_radius**2-(y-CENTER[1])**2))
    horizontal = np.hypot(points[:,:,0],points[:,:,2]-CENTER[2])
    feather_texture = .0026*np.cos(19*a+(2.18-y)*11)**4
    feather_texture += .0015*np.sin(13*a+(2.18-y)*19)
    radial = horizontal + mask*(radial+feather_texture-horizontal)
    points[:,:,0] = radial*np.sin(a)
    points[:,:,2] = CENTER[2]+radial*np.cos(a)
    # Use the contiguous crown columns, including any background samples
    # that fall inside a root window, so the joins are topologically shared.
    windows = [np.flatnonzero((angles >= block[0]) & (angles <= block[-1])) for block in samples]
    rows = np.r_[0:len(points):2,len(points)-1]
    return points[rows],fraction[rows],shade[rows],windows


def geometry(hat, cloth):
    points,fraction,shade,windows = crown_grid(hat)
    rows,cols,_ = points.shape
    fitted = fit_crown(points,cloth,hat)
    verts = fitted.reshape(-1,3).tolist()
    faces = [(j*cols+i,(j+1)*cols+i,(j+1)*cols+(i+1)%cols,j*cols+(i+1)%cols)
             for j in range(rows-1) for i in range(cols)]
    faces.append(tuple(range(cols)))
    progress = fraction.ravel().tolist()
    tones = shade.ravel().tolist()
    thickness = [1.] * len(verts)
    for index,(ids,(_,_,end,drift)) in enumerate(zip(windows,FEATHERS,strict=True)):
        ribbon = feather_rows(points[-1,ids],points[-2,ids],end,drift,hat,index)
        ribbon = fit_crown(ribbon,cloth,hat)
        previous = ((rows-1)*cols + ids).tolist()
        for j,row in enumerate(ribbon[1:],1):
            start = len(verts)
            verts.extend(row.tolist())
            current = list(range(start,start+len(row)))
            faces.extend((previous[k],current[k],current[k+1],previous[k+1])
                         for k in range(len(row)-1))
            progress.extend([.16]*len(row))
            tones.extend([float(x) for x in shade[-1,ids]])
            thickness.extend([float(1-.80*ease(j/10))]*len(row))
            previous = current
    return verts,faces,np.array(progress),np.array(tones),thickness


def export_layered(_style, hat, ombre, cloth, *, output, **_):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    verts,faces,progress,shade,thickness = geometry(hat,cloth)
    mesh = bpy.data.meshes.new("Wispy bangs / continuous crown")
    mesh.from_pydata([(x,-z,y) for x,y,z in verts],[],faces)
    mesh.update()
    hair = bpy.data.objects.new(mesh.name,mesh)
    bpy.context.collection.objects.link(hair)
    mesh.materials.append(hair_material(ombre,BANGS_COLOR,.33))
    for poly in mesh.polygons:
        poly.use_smooth = len(poly.vertices)==4
    if ombre:
        blend = ease((progress-.21)/.73)[:,None]
        colors = np.ones((len(verts),4),dtype=np.float32)
        colors[:,:3] = (BANGS_COLOR*(1-blend)+GOLD_COLOR*blend)*shade[:,None]
        attr = mesh.color_attributes.new(name="Hair color",type="FLOAT_COLOR",domain="POINT")
        attr.data.foreach_set("color",colors.ravel())
        mesh.color_attributes.active_color = attr
    group = hair.vertex_groups.new(name="Tapered edge")
    for i,weight in enumerate(thickness):
        group.add([i],weight,"REPLACE")
    solid = hair.modifiers.new("Inset surface","SOLIDIFY")
    solid.thickness = .010
    solid.offset = -1
    solid.vertex_group = group.name
    path = output/("side-sweep-"+hat+("-ombre" if ombre else "")+".glb")
    bpy.ops.export_scene.gltf(filepath=str(path),export_format="GLB",export_apply=True,
                              export_materials="EXPORT",export_image_format="AUTO")
    return path


if __name__ == "__main__":
    build_fringe(REV,export=export_layered)
