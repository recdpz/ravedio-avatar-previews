"""Refine the fitted 314 assets and keep the 316 Aero Gloss source finish."""
import argparse
from copy import deepcopy
from functools import lru_cache
from itertools import product
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"310/tools"))
import knit
from fit import geometry, warp_normals
from sculpt import accessor, node_transforms, read_glb, surface, triangles, write_glb

spec = importlib.util.spec_from_file_location("gloss_source",ROOT/"316/tools/source.py")
gloss = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gloss)

CENTER = knit.CENTER
CROWN_START = 2.045
CROWN_TOP = 2.298
GROOMS = ("mustache","patch","goatee","short","long")


def smooth(low, high, value):
    t = np.clip((value-low)/(high-low),0,1)
    return t*t*(3-2*t)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def crown(points, lowering, tuck, start, rear_only):
    x,y,z = points.T
    rise = smooth(start,CROWN_TOP,y)
    rear = 1-smooth(-.25,.03,z)
    if rear_only:
        rise *= 1-smooth(-.25,-.12,z)
    result = points.copy()
    result[:,1] -= rise*lowering
    result[:,2] += rise*rear*tuck
    return result


def cap_surface(parts, warp):
    vertices, faces = [], []
    offset = 0
    for _,_,pos,nor,rot,origin,index in parts:
        points = pos@rot.T+origin
        # The inner lining can rest against the hair. Audit the visible
        # shell for break-through, using the existing normals to select it.
        outward = np.sum((nor@rot.T)*(points-CENTER),axis=1)>0
        active = index[np.all(outward[index],axis=1)&(np.max(points[index,1],axis=1)>CROWN_START-.004)]
        vertices.append(warp(points))
        faces.append(active+offset)
        offset += len(points)
    return BVHTree.FromPolygons(np.vstack(vertices).tolist(),np.vstack(faces).tolist(),all_triangles=True)


def update_meshes(doc, binary, select):
    count = 0
    for node,rot,origin in node_transforms(doc):
        if "mesh" not in node:
            continue
        mesh = doc["meshes"][node["mesh"]]
        warp = select(mesh["name"])
        if warp is None:
            continue
        for primitive in mesh["primitives"]:
            attrs=primitive["attributes"]
            pos=accessor(doc,binary,attrs["POSITION"],3)
            nor=accessor(doc,binary,attrs["NORMAL"],3)
            points=pos@rot.T+origin
            old_normal=nor@rot.T
            after=warp(points)
            changed=np.linalg.norm(after-points,axis=1)>1e-7
            if not changed.any():
                continue
            normals=warp_normals(warp,points[changed],old_normal[changed])
            if "TANGENT" in attrs:
                tangents=accessor(doc,binary,attrs["TANGENT"],4)
                tangent=tangents[changed,:3]@rot.T
                d=warp(points[changed]+tangent*1e-4)-after[changed]
                d -= normals*np.sum(d*normals,axis=1,keepdims=True)
                d /= np.maximum(np.linalg.norm(d,axis=1,keepdims=True),1e-8)
                tangents[changed,:3]=d@rot
            pos[changed]=(after[changed]-origin)@rot
            nor[changed]=normals@rot
            doc["accessors"][attrs["POSITION"]].update(min=pos.min(0).tolist(),max=pos.max(0).tolist())
            count += int(np.count_nonzero(changed))
    return count


@lru_cache(maxsize=24)
def collider(relative):
    return surface(ROOT/relative)


def refine_hat(row, alternate, result, pin):
    source = ROOT/row["headgear"]
    doc,binary = read_glb(source)
    parts=list(geometry(doc,binary))
    hair_paths={r["hair"] for r in (row,alternate)}
    tail_paths={r["hairLengths"] for r in (row,alternate) if r.get("hairLengths")}
    supports=[collider(p) for p in sorted(hair_paths|tail_paths)]
    original = cap_surface(parts,lambda p:p)
    contacts = [len(original.overlap(s)) for s in supports]
    old_hat = surface(source)
    choices = [(*p,False) for p in product(
        (.044,.040,.036,.032,.028,.024,.018,.012),
        (CROWN_START,2.075,2.105,2.135,2.16,2.185),(.016,.010,.004,0.))]
    # A high curl can require its original apex. Pull in the loose back
    # while leaving the clearance over the front crown for this fit.
    choices.extend((drop,2.07,tuck,True) for drop,tuck in product((.044,.032,.024),(.018,.012,.007)))
    for drop,start,tuck,rear_only in choices:
        def warp(points):
            return crown(points,drop,tuck,start,rear_only)
        after = cap_surface(parts,warp)
        after_contacts = [len(after.overlap(s)) for s in supports]
        if any(a>b for a,b in zip(after_contacts,contacts,strict=True)):
            continue
        for _,_,pos,_,rot,origin,_ in parts:
            points=pos@rot.T+origin
            changed=points[:,1]>start
            if changed.any() and np.min(np.linalg.norm(warp(points[changed])-CENTER,axis=1)) < .385:
                break
        else:
            moved=update_meshes(doc,binary,lambda _:warp)
            assert moved>0
            write_glb(result,doc,binary)
            new_hat=surface(result)
            for tail in tail_paths:
                assert len(collider(tail).overlap(new_hat))<=len(collider(tail).overlap(old_hat))
            knit.seat_sprout(ROOT/row["sprout"],pin,old_hat,new_hat)
            return {"lowering":drop,"rear_tuck":tuck,"crown_blend_start":start,"rear_only":rear_only,"vertices":moved,
                    "crown_contacts_before":contacts,"crown_contacts_after":after_contacts,
                    "hat_sha256":sha(result),"sprout_sha256":sha(pin)}
    raise ValueError("No lower beanie fit with baseline clearance")


def head_front(x,y):
    return CENTER[2]+np.sqrt(np.maximum(0,.384**2-x*x-(y-CENTER[1])**2))


def mustache(points):
    x,y,z=points.T
    t=np.clip(np.abs(x)/.12333,0,1)
    shrink=smooth(.47,1,t)
    old_axis=1.653-.013*t**1.7
    new_axis=1.648-.0085*t**1.55
    x2=x*(.865-.06*smooth(.72,1,t))
    y2=new_axis+(y-old_axis)*(.89-.56*shrink)
    z2=head_front(x2,y2)+(z-head_front(x,y))*.78
    return np.column_stack((x2,y2,z2))


def append_accessor(doc,binary,values,component,kind,target):
    payload=values.tobytes()
    offset=len(binary)
    binary.extend(payload)
    binary.extend(b"\0"*(-len(binary)%4))
    views=doc["bufferViews"]
    views.append({"buffer":0,"byteOffset":offset,"byteLength":len(payload),"target":target})
    index=len(doc["accessors"])
    doc["accessors"].append({"bufferView":len(views)-1,"componentType":component,"count":len(values),"type":kind})
    return index


def soften_beard(doc,binary,style):
    body_name="short body" if style=="short" else "rounded long"
    for node,rot,origin in node_transforms(doc):
        if "mesh" not in node:
            continue
        mesh=doc["meshes"][node["mesh"]]
        if body_name not in mesh["name"]:
            continue
        for prim in list(mesh["primitives"]):
            attrs=prim["attributes"]
            assert "COLOR_0" not in attrs
            points=accessor(doc,binary,attrs["POSITION"],3)@rot.T+origin
            x,y,z=points.T
            x=np.abs(x)
            bins=np.arange(.033,.229,.005)
            gate=smooth(.035,.068,x)*(1-smooth(.178,.230,x))*smooth(.176,.236,z)
            upper=np.array([np.max(y[(np.abs(x-mid)<.008)&(z>.20)],initial=1.55) for mid in bins])
            top=np.interp(x,bins,upper)
            edge=1-smooth(.002,.040 if style=="long" else .033,top-y)
            opacity=np.clip(1-.76*edge*gate,0,1)
            colors=np.ones((len(points),4),dtype="<f4")
            colors[:,3]=opacity
            vertex_color=append_accessor(doc,binary,colors,5126,"VEC4",34962)
            material=doc["materials"][prim["material"]]
            if style=="short":
                assert material["alphaMode"]=="BLEND"
                attrs["COLOR_0"]=vertex_color
            else:
                # Keep the main Long Beard opaque. Only triangles at the
                # two mouth corners use a blended copy of its material.
                faces=triangles(doc,binary,prim["indices"]).copy()
                feather=np.any(opacity[faces]<.999,axis=1)
                assert feather.any() and (~feather).any()
                soft=deepcopy(material)
                soft["name"]+=" / mouth edge"
                soft["alphaMode"]="BLEND"
                doc["materials"].append(soft)
                opaque=faces[~feather].astype("<u4").ravel()
                fading=faces[feather].astype("<u4").ravel()
                prim["indices"]=append_accessor(doc,binary,opaque,5125,"SCALAR",34963)
                mesh["primitives"].append({**prim,"material":len(doc["materials"])-1,
                    "indices":append_accessor(doc,binary,fading,5125,"SCALAR",34963),
                    "attributes":{**attrs,"COLOR_0":vertex_color}})
    doc["buffers"][0]["byteLength"]=len(binary)


def refine_groom(source, target, mouth):
    doc,binary=read_glb(source)
    moved=update_meshes(doc,binary,lambda name:mustache if "shared mustache" in name else None)
    assert moved>0
    style=target.stem.removeprefix("groom-")
    if style in ("short","long"):
        soften_beard(doc,binary,style)
    write_glb(target,doc,binary)
    shape=surface(target,lambda name:"shared mustache" in name)
    assert not shape.overlap(mouth)
    return {"changed_mustache_vertices":moved,"sha256":sha(target)}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("output",type=Path)
    p.add_argument("baseline",type=Path)
    a=p.parse_args(sys.argv[sys.argv.index("--")+1:])
    output=a.output
    out=output/"assets"
    out.mkdir(parents=True,exist_ok=True)
    before=json.loads((a.baseline/"source-receipt.json").read_bytes())
    inputs=json.loads((ROOT/"315/catalogue-input.json").read_bytes())
    recipe=json.loads((ROOT/"316/finish.json").read_bytes())
    hats,grooms,rows={},{},inputs["rows"]
    changed={}
    for build,styles in inputs["options"]["builds"].items():
        for hair in styles["hair"]:
            top="open" if build=="Feminine" else "tank"
            default,ombre=(rows["/".join((build,hair,"beanie",top,finish))] for finish in ("default","ombre"))
            name=build.lower()+"-"+hair
            hat,pin=(out/f"{role}-{name}.glb" for role in ("beanie","sprout"))
            hats[name]=refine_hat(default,ombre,hat,pin)
            assert default["headgear"]==ombre["headgear"] and default["sprout"]==ombre["sprout"]
            changed[default["headgear"]]=hat
            changed[default["sprout"]]=pin
            print(name,hats[name]["lowering"],hats[name]["rear_tuck"],flush=True)
    mouth=surface(ROOT/before["cases"]["flow-cap"]["parts"]["mouth"]["source"])
    groom_paths=inputs["builds"]["Masculine"]["grooms"]
    for style in GROOMS:
        source=groom_paths[style]
        candidate=out/f"groom-{style}.glb"
        grooms[style]=refine_groom(ROOT/source,candidate,mouth)
        changed[source]=candidate
    cases=before["cases"]
    bare=cases["flow-cap-bare-eyes"]
    for style in ("mustache","patch","goatee","long"):
        source=groom_paths[style]
        groom={"source":source,"sha256":sha(ROOT/source),"file":Path(source).name}
        cases["flow-"+style]={**bare,"features":{**bare["features"],"groom":style},
                            "parts":{**bare["parts"],"groom":groom}}
    cases_out={}
    for key,look in cases.items():
        parts={}
        for role,item in look["parts"].items():
            source=item["source"]
            old=(a.baseline/"assets"/item["file"])
            if role=="groom" and key in ("flow-mustache","flow-patch","flow-goatee","flow-long"):
                blob,_=gloss.revise((ROOT/source).read_bytes(),role,recipe,None)
                old=out/(gloss.digest(blob)+".glb")
                old.write_bytes(blob)
            else:
                assert sha(old)==item["sha256"]
            new=old
            if path:=changed.get(source):
                group="sprout" if role=="extra" and look["features"]["detail"]=="sprout" else role
                blob,_=gloss.revise(path.read_bytes(),group,recipe,None)
                new=out/(gloss.digest(blob)+".glb")
                new.write_bytes(blob)
            parts[role]={"old":str(old),"new":str(new),"old_sha256":sha(old),"new_sha256":sha(new)}
        cases_out[key]={**look,"parts":parts}
    # Each standalone replacement uses the same reviewed finish as its assembly.
    for source,file in changed.items():
        role="headgear" if file.name.startswith("beanie-") else "sprout" if file.name.startswith("sprout-") else "groom"
        data,_=gloss.revise(file.read_bytes(),role,recipe,None)
        file.write_bytes(data)
    for style,result in grooms.items():
        result["sha256"]=sha(out/f"groom-{style}.glb")
    for style,result in hats.items():
        result["hat_sha256"]=sha(out/f"beanie-{style}.glb")
        result["sprout_sha256"]=sha(out/f"sprout-{style}.glb")
    coverage={source:{"file":file.name,"sha256":sha(file)} for source,file in changed.items()}
    (output/"source.json").write_text(json.dumps({"base":316,"revision":317,"cases":cases_out,
        "replacement_assets":coverage,"beanies":hats,"grooms":grooms},indent=2)+"\n",newline="\n")
    print("Refined",len(hats),"beanie fits and",len(grooms),"mustache styles",flush=True)


if __name__=="__main__":
    main()
