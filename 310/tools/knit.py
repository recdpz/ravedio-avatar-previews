"""Seat a soft knit shell over each covered hairstyle."""
import importlib.util
from pathlib import Path
import sys

import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("beanie309", ROOT/"309/tools/build.py")
old = importlib.util.module_from_spec(spec)
spec.loader.exec_module(old)
CENTER = old.CENTER
updos = old.updos
sys.path.insert(0, str(ROOT/"299/tools"))
from fit import geometry, warp_normals

SECTORS = np.linspace(0.,2*np.pi,72,endpoint=False)
LEVELS = np.array([0.,.12,.24,.42,.60,.81,.97])
SLICES = old.SLICES
DYES = {"Beanie / knit":(.065,.115,.180),"Beanie / rolled cuff":(.052,.094,.150)}


def head_radius(y):
    return np.sqrt(np.maximum(0.,.384**2-(y-CENTER[1])**2))


def inside(path):
    return updos.surface(path)


def fit_cuff(scalp):
    """Average the hair envelope across panels, not across individual locks."""
    angles = np.column_stack((np.sin(SECTORS),np.zeros(len(SECTORS)),np.cos(SECTORS)))
    widths = []
    for level, allowance, maximum in zip(LEVELS[:3],[.010,.016,.024],[.047,.048,.047],strict=True):
        old_ring = old.cap_ring(SECTORS,np.arcsin(level))
        needs = []
        for point, direction in zip(old_ring,angles,strict=True):
            center = np.array([0.,point[1],CENTER[2]])
            hit = scalp.ray_cast(center+.65*direction,-direction,.65)[0]
            support = max(head_radius(point[1]),float((np.array(hit)-center)@direction) if hit else 0.)
            needs.append(support+allowance-float((point-center)@direction))
        requested = np.asarray(needs)
        softened = sum(weight*np.roll(requested,i-4)
                       for i,weight in enumerate([1,3,7,10,12,10,7,3,1]))/54
        # Clearance still takes precedence where a wide lock is under the hem.
        widths.append(np.clip(np.maximum(softened,requested-.004),-maximum,.008))
    hem = widths[0]
    # Carry the closer seat up the shell as one smooth taper. This avoids
    # a constricted waist between the cuff and the relaxed crown.
    widths[1] = np.maximum(widths[1],hem-.005)
    widths[2] = np.maximum(widths[2],hem-.006)
    return np.array([*widths,.95*hem,.69*hem,.25*hem,np.zeros_like(hem)])


def cap_ring(theta,alpha,widths):
    height = np.sin(alpha)
    i = np.searchsorted(LEVELS,height,side="right") - 1
    if i >= len(LEVELS)-1:
        return old.cap_ring(theta,alpha)
    gap = LEVELS[i+1]-LEVELS[i]
    t = (height-LEVELS[i])/gap
    slopes = np.gradient(widths,LEVELS,axis=0)
    slopes[-1] = 0
    offsets = (widths[i]*(2*t**3-3*t*t+1) + widths[i+1]*(-2*t**3+3*t*t)
               + gap*(slopes[i]*(t**3-2*t*t+t)+slopes[i+1]*(t**3-t*t)))
    depth = np.interp(theta,SECTORS,offsets,period=2*np.pi)
    fit = np.column_stack((depth*np.sin(theta),np.zeros(len(theta)),depth*np.cos(theta)))
    return old.cap_ring(theta,alpha)+fit


def knit_maps():
    """A seamless pair of rounded loops on a small repeated tile."""
    size = 128
    t = np.arange(size)/size
    x,y = np.meshgrid(t,t)
    x = (x+.5)%1-.5
    loop = np.sin(np.pi*y)
    leg = .071+.153*loop**1.35
    yarn = np.exp(-((abs(x)-leg)/.092)**2)*(.16+.84*loop**.62)
    yarn += .18*np.exp(-((x/.17)**2+((y-.92)/.13)**2))
    yarn /= yarn.max()
    weave = .935+.065*yarn
    # Tile derivatives use wraparound so the loop edges share their tangents.
    dx = (np.roll(yarn,-1,1)-np.roll(yarn,1,1))*2.6
    dy = (np.roll(yarn,-1,0)-np.roll(yarn,1,0))*2.6
    normal = np.stack((-dx,-dy,np.ones_like(dx)),axis=2)
    normal = .5+.5*normal/np.linalg.norm(normal,axis=2,keepdims=True)
    maps = []
    for name, values, colorspace in [("Knit stitch tone",np.repeat(weave[:,:,None],3,2),"sRGB"),
                                     ("Knit stitch normal",normal,"Non-Color")]:
        image = bpy.data.images.new(name,width=size,height=size,alpha=False)
        image.colorspace_settings.name = colorspace
        rgba = np.dstack((values,np.ones((size,size)))).astype(np.float32)
        image.pixels.foreach_set(rgba.ravel())
        image.pack()
        maps.append(image)
    return maps


def material(name,color,maps):
    m = old.knit_material(name,color)
    shader = m.node_tree.nodes.get("Principled BSDF")
    shade = m.node_tree.nodes.new("ShaderNodeTexImage")
    shade.image = maps[0]
    m.node_tree.links.new(shade.outputs["Color"],shader.inputs["Base Color"])
    fine = m.node_tree.nodes.new("ShaderNodeTexImage")
    fine.image = maps[1]
    normal = m.node_tree.nodes.new("ShaderNodeNormalMap")
    normal.inputs["Strength"].default_value = .52 if "cuff" in name else .36
    m.node_tree.links.new(fine.outputs["Color"],normal.inputs["Color"])
    m.node_tree.links.new(normal.outputs["Normal"],shader.inputs["Normal"])
    return m


def export(path,widths):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    theta = np.arange(SLICES)*2*np.pi/SLICES
    alphas = np.r_[np.linspace(0.,.258,14,endpoint=False),np.linspace(.258,np.pi/2,26,endpoint=False)]
    rings = len(alphas)
    outer = np.concatenate([cap_ring(theta,alpha,widths) for alpha in alphas])
    pole = cap_ring(np.zeros(1),np.pi/2,widths)[0]
    inner = outer.copy()
    for row,alpha in enumerate(alphas):
        sl = slice(row*SLICES,(row+1)*SLICES)
        inner[sl] -= np.column_stack((.010*np.sin(theta)*np.cos(alpha),
                                     np.full(SLICES,.012*np.sin(alpha)),
                                     .010*np.cos(theta)*np.cos(alpha)))
    layer = len(outer)+1
    points = np.vstack([outer,pole,inner,pole-[0,.012,0]])
    faces, indices, tex = [],[],[]
    for row in range(rings):
        for i in range(SLICES):
            j = (i+1)%SLICES
            a,b = row*SLICES+i,row*SLICES+j
            u = i/SLICES*72
            v = alphas[row]*19
            du = 72/SLICES
            if row < rings-1:
                c,d = b+SLICES,a+SLICES
                next_v = alphas[row+1]*19
                faces.extend([(a,b,c,d),(layer+d,layer+c,layer+b,layer+a)])
                coordinates = [(u,v),(u+du,v),(u+du,next_v),(u,next_v)]
                tex.extend([coordinates,coordinates[::-1]])
            else:
                faces.extend([(a,b,len(outer)),(layer+b,layer+a,2*layer-1)])
                coordinates = [(u,v),(u+du,v),(u+du/2,np.pi/2*19)]
                tex.extend([coordinates,[coordinates[1],coordinates[0],coordinates[2]]])
            indices.extend([int(np.sin(alphas[row])<.214),0])
            if row == 0:
                faces.append((b,a,layer+a,layer+b))
                tex.append([(u+du,0),(u,0),(u,-.4),(u+du,-.4)])
                indices.append(1)
    mesh = bpy.data.meshes.new("Knit shell with fitted cuff")
    mesh.from_pydata(points[:,[0,2,1]]*[1,-1,1],[],faces)
    mesh.update()
    ob = bpy.data.objects.new("Beanie / fitted knit",mesh)
    bpy.context.collection.objects.link(ob)
    uv = mesh.uv_layers.new(name="Knit loops")
    uv.data.foreach_set("uv",np.array([xy for face in tex for xy in face],dtype=np.float32).ravel())
    maps = knit_maps()
    for name,color in DYES.items():
        mesh.materials.append(material(name,color,maps))
    for poly,index in zip(mesh.polygons,indices,strict=True):
        poly.use_smooth = True
        poly.material_index = index
    bpy.ops.export_scene.gltf(filepath=str(path),export_format="GLB",export_materials="EXPORT",
                              export_texcoords=True,export_tangents=True)
    # Store the knitted grain separately from the recolorable dye.
    model,data = updos.read_glb(path)
    for slot in model["materials"]:
        slot["pbrMetallicRoughness"]["baseColorFactor"] = [*DYES[slot["name"]],1.]
    updos.write_glb(path,model,data)


def press_fringe(source,target):
    """Tuck only the front lock bundle where it touches the cuff."""
    def warp(points):
        x,y,z = points.T
        radial = points[:,[0,2]]-CENTER[[0,2]]
        length = np.linalg.norm(radial,axis=1)
        cuff = np.exp(-((y-1.967)/.092)**2) * old.smooth(.15,.29,z)
        pinch = np.minimum(.028*cuff,np.maximum(0.,length-head_radius(y)-.0025))
        result = points.copy()
        result[:,[0,2]] -= radial*(pinch/np.maximum(length,.001))[:,None]
        result[:,1] -= .010*cuff
        return result

    doc,buf = updos.read_glb(source)
    changed = False
    for name,bounds,pos,normal,rotation,offset,_ in geometry(doc,buf):
        if "front locks222" not in name:
            continue
        points = pos@rotation.T+offset
        adjusted = warp(points)
        norm = warp_normals(warp,points,normal@rotation.T)
        pos[:] = (adjusted-offset)@rotation
        normal[:] = norm@rotation
        bounds.update(min=pos.min(0).tolist(),max=pos.max(0).tolist())
        changed = True
    assert changed, source
    updos.write_glb(target,doc,buf)


def seat_sprout(source,target,old_hat,new_hat):
    doc,data = updos.read_glb(source)
    node,rot,offset = next(part for part in updos.node_transforms(doc)
                           if "clip silver235" in part[0].get("name",""))
    index = doc["meshes"][node["mesh"]]["primitives"][0]["attributes"]["POSITION"]
    x,_,z = (updos.vectors(doc,data,index)@rot.T+offset).mean(0)
    before,after = (hat.ray_cast((x,3.,z),(0.,-1.,0.))[0] for hat in (old_hat,new_hat))
    assert before is not None and after is not None
    shift = np.array([0.,after.y-before.y,0.])
    for index in doc["scenes"][doc.get("scene",0)]["nodes"]:
        root = doc["nodes"][index]
        root["translation"] = (root.get("translation",[0.,0.,0.])+shift).tolist()
    updos.write_glb(target,doc,data)
