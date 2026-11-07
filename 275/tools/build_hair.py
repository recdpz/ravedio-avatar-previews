"""Author the 275 hair shapes and export fitted, independently selectable GLBs."""
import json
import math
import sys
from pathlib import Path

import bpy
import numpy as np

REV = Path(__file__).resolve().parents[1]
ROOT = REV.parent
ASSETS = REV / "assets"
sys.path.insert(0, str(ROOT / "271/tools"))
from build_bandanas import CAT, CENTER, ease, hit, ordinary, surface, unit
from bake_catalogue import node_transforms, read_glb, vectors, warp_normals, write_glb

BANDANAS = json.loads((ROOT / "274/bandana-fits.json").read_text(encoding="utf8"))
TOPS = CAT["pashminaVariants"]["Feminine"]
BUILDS = CAT["builds"]["Feminine"]
HATS = tuple(CAT["headwear"])
BANGS_COLOR = np.array([.160, .059, .033])
GOLD_COLOR = np.array([.57, .342, .154])
RADIUS = .384


def smooth_max(a, b, width=.027):
    return np.maximum(a,b) + np.maximum(0.,width-np.abs(a-b))**2/(4*width)


def smooth_crown(azimuth, y, length, mask, drape):
    dy = y - CENTER[1]
    spherical = np.sqrt(np.maximum(.003**2, .413**2 - dy**2))
    falling = ease((1.84-y)/.28) * mask
    rz = (1-falling)*spherical + falling*drape
    # Keep the transition tangent to the head as the hair starts to hang.
    scalp = np.sqrt(np.maximum(0., (RADIUS+.021)**2-dy**2))
    rz = rz + mask*(smooth_max(rz,scalp)-rz)
    rx = rz + falling*.017
    turn = .040*np.sin(azimuth*2+.8)*(1-length) + .095*np.sin(length*5+azimuth*3)*falling
    a = azimuth+turn
    grain = (.0038*np.cos(23*a + 4*length)**4 + .0026*np.cos(13*a - 5*length + .6))
    grain += .007*np.cos(8*a + .72*np.sin(length*6+a*3))*falling
    grain *= ease((2.215-y)/.18)
    return np.stack(((rx+grain)*np.sin(a),y,CENTER[2]+(rz+grain)*np.cos(a)), axis=-1)


def release_back(points, hat):
    x, y, z = (points-CENTER).T
    angle = np.arctan2(x,z)
    across = ease((np.abs(angle)-1.12)/.72)
    fall = ease((.177-y)/.305)
    if hat == "pashmina":
        drop = .125 * across * fall
    else:
        drop = (.415 + .025*np.sin(angle*4+.6) + .017*np.cos(angle*9)) * across * fall
    new_y = y-drop
    release = ease(drop/.30)
    radius = np.hypot(x,z)
    old_scalp = np.sqrt(np.maximum(.001, .408**2-y*y))
    new_scalp = np.sqrt(np.maximum(0., .405**2-new_y*new_y))
    drape = .354 + .019*np.sin(new_y*16 + angle*3) + .012*np.cos(angle*8+new_y*9)
    drape -= .018*ease((-new_y-.40)/.15)
    adjusted = (1-release)*old_scalp + release*drape
    r = radius + (smooth_max(adjusted,new_scalp)-old_scalp)*ease(drop/.055)
    turn = angle + across*release*.104*np.sin(new_y*10+angle*3)
    if hat == "pashmina":
        r -= .023*ease(drop/.13)
    return CENTER + np.stack((r*np.sin(turn),new_y,r*np.cos(turn)),axis=-1)


def bangs_body(hat):
    a, t = np.meshgrid(np.linspace(-math.pi,math.pi,193)[:-1], np.linspace(0,1,108))
    shoulder = ease((np.abs(a)-.54)/1.01)
    front = 2.080 + .009*np.sin(a*14+.5) + .004*np.sin(a*31)
    end = front - .706*shoulder
    end += shoulder*(.029*np.sin(a*3+.8) + .017*np.sin(a*8-.9) + .012*np.cos(a*13))
    if hat == "pashmina":
        end += .113*shoulder
    y = 2.2160 + t*(end-2.2160)
    drape = .338 + .022*np.sin(t*7+a*2) + .011*np.sin(a*7+t*4)
    p = smooth_crown(a,y,t,shoulder,drape)
    part = np.exp(-((a-.08-.20*(1-t))/.076)**2)*np.sin(np.pi*t)**2
    edge = (.009+.009*(1-shoulder))*ease((t-.93)/.07) + .010*part
    p -= edge[...,None]*unit(p-CENTER)
    if hat == "pashmina":
        back = ease((1.68-y)/.30)
        p[:,:,0] *= 1-.16*back
        p[:,:,2] += .028*back
    shade = .98 + .050*np.sin(a*13+t*3) + .036*np.cos(a*22+t*4) - .08*part
    return p, ease((1.99-y)/.64)*shoulder, shade


def hair_material(ombre, color, roughness):
    mat = bpy.data.materials.new("Hair / chestnut" + (" ombre" if ombre else ""))
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color,1)
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Coat Weight"].default_value = .17
    shader.inputs["Coat Roughness"].default_value = .24
    if ombre:
        shader.inputs["Base Color"].default_value = (1,1,1,1)
        attr = mat.node_tree.nodes.new("ShaderNodeVertexColor")
        attr.layer_name = "Hair color"
        mat.node_tree.links.new(attr.outputs["Color"],shader.inputs["Base Color"])
    return mat


def grid_mesh(name, p, fraction, shade, material, ombre, color, *, loop=False, radial_normals=True):
    rows, cols, _ = p.shape
    verts = p.reshape(-1,3)
    faces = [(j*cols+i,j*cols+(i+1)%cols,(j+1)*cols+(i+1)%cols,(j+1)*cols+i)
             for j in range(rows-1) for i in range(cols if loop else cols-1)]
    probe = faces[(rows//3)*(cols if loop else cols-1)+cols//3]
    x,y,z = verts[list(probe[:3])]
    reference = x-CENTER if radial_normals else x-p[rows//3].mean(axis=0)
    if np.cross(y-x,z-x)@reference < 0:
        faces = [face[::-1] for face in faces]
    if loop:
        faces += [tuple(reversed(range(cols))), tuple(range((rows-1)*cols,rows*cols))]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([(x,-z,y) for x,y,z in verts],[],faces)
    mesh.update()
    obj = bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)
    for polygon in mesh.polygons:
        polygon.use_smooth = len(polygon.vertices) == 4
    if ombre:
        blend = ease((fraction.ravel()-.21)/.73)[:,None]
        rgba = np.ones((len(verts),4),dtype=np.float32)
        rgba[:,:3] = (color*(1-blend) + GOLD_COLOR*blend)*shade.ravel()[:,None]
        attribute = mesh.color_attributes.new(name="Hair color",type="FLOAT_COLOR",domain="POINT")
        attribute.data.foreach_set("color",rgba.ravel())
        mesh.color_attributes.active_color = attribute
    return obj


def shell(name, p, fraction, shade, mat, ombre, color, loop=False):
    # The visible lip rounds into a narrow inner return without a planar cap.
    if loop:
        # Close only the crown apex. The lower contour remains open around the face.
        cols = p.shape[1]
        obj = grid_mesh(name,p,fraction,shade,mat,ombre,color,loop=True)
        import bmesh
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bottom = next(face for face in bm.faces if len(face.verts)==cols and
                      sum(v.co.z for v in face.verts)/cols < 2.18)
        bmesh.ops.delete(bm,geom=[bottom],context="FACES_ONLY")
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        bm.to_mesh(obj.data)
        bm.free()
    else:
        obj = grid_mesh(name,p,fraction,shade,mat,ombre,color)
    solid = obj.modifiers.new("Inset edge thickness","SOLIDIFY")
    solid.thickness = .010
    solid.offset = -1


def cloth_for(style, hat):
    key = "Feminine-"+style
    if hat == "headband":
        return (ROOT/"274"/BANDANAS[key]["headgear"]).resolve()
    if hat == "pashmina":
        return ordinary(TOPS[CAT["pashminaHairFamilies"]["Feminine"][style]]["sweatshirt"])
    if hat != "none":
        return ordinary(CAT["fits"][key][hat]["headgear"])
    return None


def fit_crown(p, cloth, hat):
    if not cloth or hat == "ears":
        return p
    # Fit in head coordinates, leaving the free ends of the hair undisturbed.
    output = p.copy()
    for index in np.ndindex(p.shape[:2]):
        v = p[index]-CENTER
        r = np.linalg.norm(v)
        if p[index][1] < (1.42 if hat == "pashmina" else 1.79) or r < RADIUS:
            continue
        d = v/r
        inside = hit(cloth,CENTER,d)
        if inside is not None:
            limit = (inside-CENTER)@d-.009
            if p[index][1] > 1.45:
                limit = max(RADIUS+.003,limit)
            if r > limit and (limit < .49 if hat == "pashmina" else limit < .45):
                output[index] = CENTER+d*limit
    return output


def fringe(mat, ombre, hat, cloth):
    # Irregular spacing and cut lengths prevent a comb-like silhouette.
    tips = [(-.179,1.943,.013),(-.138,1.974,.010),(-.091,1.965,.013),
            (-.050,1.981,.008),(-.014,1.957,.011),(.041,1.966,.012),
            (.084,1.990,.009),(.124,1.973,.013),(.172,1.940,.012)]
    t = np.linspace(0,1,38)
    w = np.linspace(0,2*math.pi,12,endpoint=False)
    for i,(tip_x,tip_y,width) in enumerate(tips):
        root_x = tip_x*.77 - .014
        y0 = 2.150 + .006*math.sin(i*1.62)
        if hat == "beanie":
            tip_y += .010
        y = y0 + (tip_y-y0)*t
        x = root_x+(tip_x-root_x)*t + .012*np.sin(np.pi*t)*math.cos(i*1.48)
        base = np.sqrt(np.maximum(0.,RADIUS**2-x*x-(y-CENTER[1])**2))
        lift = .009 + .027*ease((2.108-y)/.066) - .017*ease((t-.57)/.43)
        if hat == "beanie":
            lift -= .015*(1-ease((t-.52)/.30))
        elif hat in {"cap","bucket","cowboy"}:
            lift -= .012*(1-ease((t-.49)/.32))
        z = CENTER[2]+base+lift
        axis = np.stack((x,y,z),axis=-1)
        tangent = unit(np.gradient(axis,axis=0))
        out = unit(axis-CENTER)
        side = unit(np.cross(tangent,out))
        normal = unit(np.cross(side,tangent))
        taper = (1-.96*ease((t-.62)/.38)) * (.76 + .24*ease(t/.37))
        ring = axis[:,None,:] + (width*taper)[:,None,None]*np.cos(w)[None,:,None]*side[:,None,:]
        ring += (.0065*taper)[:,None,None]*np.sin(w)[None,:,None]*normal[:,None,:]
        if hat in {"cap","beanie","headband"}:
            ring = fit_crown(ring,cloth,hat)
        ones = np.ones(ring.shape[:2])
        grid_mesh("Fringe / tapered lock %02d"%(i+1),ring,.16*ones,ones,mat,ombre,BANGS_COLOR,
                  loop=True,radial_normals=False)


def base_buns(hat, ombre):
    key = "Feminine-space-buns"
    if hat == "headband":
        return (ROOT/"274"/BANDANAS[key]["fittedHair"]["ombre" if ombre else "default"]).resolve()
    path = CAT["fits"][key].get(hat,{}).get("hair",BUILDS["hair"]["space-buns"]["path"])
    return ordinary(CAT["ombre"][path] if ombre else path)


def export_buns(path, hat, ombre):
    source = base_buns(hat,ombre)
    model, binary = read_glb(source)
    for node, rotation, offset in node_transforms(model):
        if "mesh" not in node:
            continue
        for primitive in model["meshes"][node["mesh"]]["primitives"]:
            pos, normal = (primitive["attributes"][k] for k in ("POSITION","NORMAL"))
            p,n = vectors(model,binary,pos),vectors(model,binary,normal)
            before = p @ rotation.T+offset
            after = release_back(before,hat)
            changed = np.linalg.norm(after-before,axis=1) > 1.e-10
            p[changed] = (after[changed]-offset) @ rotation
            n[changed] = warp_normals(lambda q: release_back(q,hat),
                                      before[changed],n[changed] @ rotation.T) @ rotation
            model["accessors"][pos].update(min=p.min(axis=0).tolist(),max=p.max(axis=0).tolist())
            if ombre:
                uv_accessor = model["accessors"][primitive["attributes"]["TEXCOORD_0"]]
                uv_view = model["bufferViews"][uv_accessor["bufferView"]]
                assert uv_accessor["type"] == "VEC2" and uv_accessor["componentType"] == 5126
                uv = np.ndarray((uv_accessor["count"],2),dtype="<f4",buffer=binary,
                                offset=uv_view.get("byteOffset",0)+uv_accessor.get("byteOffset",0),
                                strides=(uv_view.get("byteStride",8),4))
                # Use the existing baked color ramp and preserve the upper updo colors.
                tip = ease((1.79-after[:,1])/.51)*ease((before[:,1]-after[:,1])/.26)
                uv[:,1] += (1-uv[:,1])*tip
    write_glb(path,model,binary)


def export_hair(style, hat, ombre, cloth):
    path = ASSETS/(style+"-"+hat+("-ombre" if ombre else "")+".glb")
    if style == "space-buns":
        export_buns(path,hat,ombre)
    else:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        p, fraction, shade = bangs_body(hat)
        p = fit_crown(p,cloth,hat)
        material = hair_material(ombre,BANGS_COLOR,.32)
        shell("Hair / layered lob",p,fraction,shade,material,ombre,BANGS_COLOR,loop=True)
        fringe(material,ombre,hat,cloth)
        bpy.ops.export_scene.gltf(filepath=str(path),export_format="GLB",export_apply=True,
                                  export_materials="EXPORT",export_image_format="AUTO")
    return path


def main():
    result = {}
    for style,label,note in [
        ("space-buns","Space Buns","Half-up buns with loose waves behind the shoulders."),
        ("side-sweep","Wispy Bangs","A shoulder-length cut with a light, separated fringe."),
    ]:
        fits = {}
        for hat in HATS:
            if style == "side-sweep" and hat == "ears":
                fits[hat] = fits["none"]
                continue
            cloth_path = cloth_for(style,hat)
            cloth = surface(cloth_path) if cloth_path else None
            fit = {}
            for ombre in (False,True):
                path = export_hair(style,hat,ombre,cloth)
                fit["ombre" if ombre else "default"] = "./assets/"+path.name
            fits[hat] = fit
        result[style] = {"label":label,"note":note,"fits":fits}
    (REV/"hair-fits.json").write_text(json.dumps({"Feminine":result},indent=2)+"\n",encoding="utf8")


if __name__ == "__main__":
    main()
