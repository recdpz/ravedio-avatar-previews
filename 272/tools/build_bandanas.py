"""Fit wider 272 wraps and regular triangular scarves over the approved hair."""
import json
import math
import sys
from pathlib import Path

import bpy
import numpy as np

REV = Path(__file__).resolve().parents[1]
ROOT = REV.parent
OUT = REV / "assets"
sys.path.insert(0, str(ROOT / "271/tools"))
from build_bandanas import (
    CAT, CENTER, cloth_surface, ease, envelope, female_wrap, hit, mesh_grid, new_sprout,
    ordinary, pull_behind, sha, surface, texture,
)


def folded_band(tree, style, clearance):
    """Wrap a wider folded strip with a small drop towards the knot."""
    u = np.linspace(-np.pi, np.pi, 256, endpoint=False)
    v = np.linspace(0, 1, 35)
    direction = np.column_stack((np.sin(u), np.zeros_like(u), np.cos(u)))
    front_height = {"buzz":1.981, "taper":2.054, "curly-top":2.044, "afro":2.016}.get(style, 2.009)
    rear = ((1 - np.cos(u)) / 2)**2
    middle = front_height - .094*rear + .004*np.sin(u+.3) + .002*np.sin(3*u+.8)
    width = .120 - .021*rear**6 + .004*np.cos(u*2+.9)
    heights = middle[None,:] + (v[:,None]-.5)*width[None,:]
    support = np.empty_like(heights)
    for j,k in np.ndindex(heights.shape):
        center = CENTER.copy()
        center[1] = heights[j,k]
        d = direction[k]
        hair = hit(tree, center+d, -d)
        skin = math.sqrt(.384**2 - (center[1]-CENTER[1])**2)
        support[j,k] = max(skin, (hair-center)@d if hair is not None else skin)
    radius = envelope(support, True) + clearance
    # A little fullness at the folded edges, with subtle tension waves across the cotton.
    radius += .0013*np.sin(u*5+.7)[None,:] + .0024*np.sin(v[:,None]*np.pi*1.4)**2
    points = CENTER + direction[None,:,:]*radius[:,:,None]
    points[:,:,1] = heights
    uv = np.stack(np.meshgrid(np.arange(len(u))/len(u), v), axis=-1)
    return points, uv, True


def folded_kerchief(tree, style, clearance):
    """Fold the crown point forward, with a continuous low wrap under the updo."""
    u = np.linspace(-np.pi,np.pi,256,endpoint=False)
    v = np.linspace(0,1,31)
    # Keep the ponytail on the left. Move the knot to the right, on the same cloth.
    theta = u - (.20 if style == "ponytail" else 0)
    direction = np.column_stack((np.sin(theta),np.zeros_like(u),np.cos(theta)))
    angle_from_front = np.arccos(np.clip(np.cos(theta),-1,1))
    front = ease(1-angle_from_front/1.47)
    rear = ((1-np.cos(theta))/2)**2
    lower = 1.943 + .028*np.cos(theta) - .031*rear
    # Lift the leading hem off the tips of the face-framing locks.
    tuck = .036*ease((np.cos(theta)-.18)/.65)
    lower += tuck
    width = .067 - .025*rear**4 + .108*front**1.12 - tuck
    heights = lower[None,:] + v[:,None]*width[None,:]
    support = np.empty_like(heights)
    for j,k in np.ndindex(heights.shape):
        base = CENTER.copy()
        base[1] = heights[j,k]
        d = direction[k]
        found = hit(tree,base+d,-d)
        skin = math.sqrt(.384**2 - (base[1]-CENTER[1])**2)
        support[j,k] = max(skin, (found-base)@d if found is not None else skin)
    radius = envelope(support,True) + clearance
    radius += .0019*np.sin(np.pi*v[:,None])*(.6+.4*np.cos(theta)[None,:]**2)
    points = CENTER + direction[None,:,:]*radius[:,:,None]
    points[:,:,1] = heights
    uv = np.stack(np.meshgrid(np.arange(len(u))/len(u), v), axis=-1)
    return points, uv, True


def triangular_scarf(tree, style, clearance):
    # Loose hair and braids retain the full triangular scarf. Scale the
    # surface radially only when more clearance is needed around the hair.
    points, uv, loop = female_wrap(tree,style)
    rays = points-CENTER
    points = points + rays/np.linalg.norm(rays,axis=-1,keepdims=True)*clearance
    return points, uv, loop


def positioned(points, tree, clearance):
    for j,k in np.ndindex(points.shape[:2]):
        points[j,k] = pull_behind(tree, points[j,k], clearance)
    return points


def knit_knot(tree, points, anchor, mat, is_band):
    """An overlapping square knot, with short asymmetric cloth ends and a gathered seat."""
    t,s = np.meshgrid(np.linspace(0,1,36),np.linspace(-1,1,15),indexing="ij")
    rear = points[len(points)//2,0] if is_band else points[-1,points.shape[1]//2]
    for sign in (-1,1):
        if is_band:
            # Start each fold on the actual rear ring, several vertices left/right.
            k = 5 if sign<0 else points.shape[1]-5
            start = points[len(points)//2,k]
        else:
            k = points.shape[1]//2 + sign*45
            start = points[-1,k]
        end = anchor + np.array([-sign*.011,-.007,-.024])
        line = start*(1-t[:,:,None]) + end*t[:,:,None]
        width = (.034 if is_band else .023)*(1-t) + .012*t
        gather = line.copy()
        gather[:,:,1] += s*width + .004*np.sin(np.pi*t)
        gather[:,:,2] -= .007*np.sin(np.pi*t)*(1-s*s)
        gather = positioned(gather, tree, .0025)
        uv = np.stack((.30 + t*.075, (s+1)*.5),axis=-1)
        mesh_grid("Bandana / gathered fold "+str(sign),gather,uv,mat,thickness=.003)

        # At the knot the cloth is narrow. It opens into a short hemmed end.
        length = (.113 if sign<0 else .144) if is_band else (.106 if sign<0 else .132)
        flare = .024 + .009*np.sin(np.pi*t) - .010*(1-t)**4 - .005*t
        end_x = sign*(.013 + (.045 if is_band else .040)*t + .009*np.sin(np.pi*t))
        tail = anchor + np.stack((
            end_x + s*flare,
            -.021 - length*t + .013*np.sin(np.pi*t) + sign*.014*s*t**4,
            -.026 - .017*t - .009*np.sin(np.pi*t) - .005*(1-s*s)*np.sin(np.pi*t),
        ),axis=-1)
        tail = positioned(tail, tree, .006)
        uv = np.stack((.44 + .15*t,(s+1)*.5),axis=-1)
        mesh_grid("Bandana / hemmed tail "+str(sign),tail,uv,mat,thickness=.003)

    y,x = np.meshgrid(np.linspace(-1,1,15),np.linspace(-1,1,25),indexing="ij")
    front = anchor + np.stack((
        .032*x*(1-.18*y*y) + .004*y,
        .021*y*(1-.13*x*x) - .016,
        -.028 - .012*(1-x*x)*(1-y*y),
    ),axis=-1)
    front = positioned(front, tree, .006)
    uv = np.stack((.37 + .075*(x+1)*.5, (y+1)*.5),axis=-1)
    mesh_grid("Bandana / rounded knot fold",front,uv,mat,thickness=.0037)


def build_fit(build, style):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    key = build + "-" + style
    bare = CAT["builds"][build]["hair"][style]["path"]
    file = ordinary(bare)
    hair = surface(file)
    pony = None
    if key == "Feminine-ponytail":
        is_tail = lambda name: "rounded tail220" in name or "tie220" in name
        pony = surface(file, is_tail)
        hair = surface(file, lambda name: not is_tail(name))
    masculine = build == "Masculine"
    folded = not masculine and style in {"ponytail", "space-buns"}
    wrap = folded_band if masculine else folded_kerchief if folded else triangular_scarf
    for clearance in [0.0,.0018,.004,.0065]:
        points, uv, loop = wrap(hair,style,clearance)
        shell = cloth_surface(points,loop)
        overlaps = len(shell.overlap(hair))
        pony_pairs = len(shell.overlap(pony)) if pony is not None else 0
        if not overlaps and not pony_pairs:
            break
    assert overlaps == 0 and pony_pairs == 0, (key,overlaps,pony_pairs)
    mat = texture("bandana-print.png" if loop else "scarf-print.png")
    anchor = points[len(points)//2,0] if loop else points[-1,points.shape[1]//2]
    mesh_grid("Bandana / folded wrap" if loop else "Bandana / triangular crown scarf",points,uv,mat,loop=loop)
    knit_knot(hair,points,anchor,mat,loop)
    dst = OUT / (key+"-bandana.glb")
    bpy.ops.export_scene.gltf(filepath=str(dst),export_format="GLB",export_apply=True,
                              export_materials="EXPORT",export_image_format="AUTO")
    woven = surface(dst, lambda n: "wrap" in n or "scarf" in n)
    tied = surface(dst, lambda n: ("fold" in n and "wrap" not in n) or "tail" in n)
    joins = len(woven.overlap(tied))
    pony_pairs = len(surface(dst).overlap(pony)) if pony is not None else 0
    assert joins > 0 and pony_pairs == 0, (key,joins,pony_pairs)
    sprout = OUT / (key+"-sprout.glb")
    shift = new_sprout(ordinary(CAT["sprouts"][key+"--headband"]["path"]),shell,hair,sprout)
    print("FIT272",key,"clearance",clearance,"wrap/knot contact",joins,"ponytail overlaps",pony_pairs,flush=True)
    return {
        "hair":bare,"hair_sha256":sha(file),
        "construction":"folded kerchief" if folded else "folded forehead wrap" if masculine else "triangular crown scarf",
        "headgear":"./assets/"+dst.name,"headgear_sha256":sha(dst),
        "sprout":"./assets/"+sprout.name,"sprout_sha256":sha(sprout),
        "outer_wrap_hair_overlap_pairs":overlaps,"ponytail_overlap_pairs":pony_pairs,
        "wrap_tie_contact_pairs":joins,"sprout_height_adjustment":shift,
    }


if __name__ == "__main__":
    fits = {}
    for build, family in CAT["builds"].items():
        for style in family["hair"]:
            fits[build+"-"+style] = build_fit(build,style)
    (REV/"bandana-fits.json").write_text(json.dumps(fits,indent=2)+"\n",encoding="utf8",newline="\n")
