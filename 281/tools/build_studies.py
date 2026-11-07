"""Author two silhouette studies in the avatar's shared coordinates."""
import json
import sys
from pathlib import Path

import bpy
import numpy as np

REV = Path(__file__).resolve().parents[1]
ROOT = REV.parent
sys.path.insert(0,str(ROOT/"275/tools"))
from build_hair import (BANGS_COLOR, CENTER, RADIUS, bangs_body, ease,
                        grid_mesh, hair_material, shell, unit)

PART = -.13


def soft_edge(a, original, style):
    part = np.abs(a-PART)
    shoulder = ease((np.abs(a)-.54)/.91)
    weight = 1-ease((np.abs(a)-.72)/.30)
    if style == "air":
        # A shallow, softly broken arc frames the brow. The highest cuts are
        # small open gaps among broad shallow sections of the same surface.
        end = 1.974-.031*ease((part-.33)/.47)+.014*np.sin(a*2.9+.28)
        cuts = [(-.542,.041,.043),(-.292,.065,.074),(-.047,.036,.048),
                (.160,.065,.066),(.431,.054,.055),(.608,.039,.030)]
        for center,width,height in cuts:
            side = np.where(a<center,1.13,.80)
            end += height*np.exp(-((a-center)/(width*side))**2)
        end += .003*np.sin(28*a+1.1)
    else:
        # Longer corners wrap around the cheeks. A couple of shorter pieces
        # soften the open center without covering it.
        end = 2.117-.262*ease((part-.023)/.88)
        end += .008*np.sin(9*a+.8)*ease(part/.24)
    return original + weight*(end+.706*shoulder-original)


def air_radius(y):
    # Hermite segments give a rounded crest and return in profile. The hem
    # meets the forehead closely while its peak projects a little farther.
    heights = np.array([1.865,1.920,1.958,1.990,2.032,2.081,2.138,2.184,2.217])
    radius = np.array([.384,.373,.357,.364,.351,.313,.245,.153,.009])
    slope = np.array([-.16,-.32,.02,0.,-.52,-1.00,-1.63,-2.55,-5.2])
    index = np.clip(np.searchsorted(heights,y)-1,0,len(heights)-2)
    span = heights[index+1]-heights[index]
    t = np.clip((y-heights[index])/span,0,1)
    return ((2*t**3-3*t*t+1)*radius[index] + (t**3-2*t*t+t)*span*slope[index]
            +(-2*t**3+3*t*t)*radius[index+1] + (t**3-t*t)*span*slope[index+1])


def study_surface(style):
    a = np.linspace(-np.pi,np.pi,257)[:-1]
    points,progress,shade = bangs_body("none",angles=a,hairline=lambda angle,old:soft_edge(angle,old,style))
    y = points[:,:,1]
    old_angle = np.arctan2(points[:,:,0],points[:,:,2]-CENTER[2])
    old_r = np.hypot(points[:,:,0],points[:,:,2]-CENTER[2])
    front = (1-ease((np.abs(old_angle)-.61)/.40))*ease((2.213-y)/.077)
    stroke = ease((2.165-y)/.22)
    theta = old_angle.copy()
    if style == "air":
        # Sweep the shallow lock texture at an angle while preserving the
        # gently arched silhouette and open spaces in the front edge.
        theta += .090*front*stroke*(.54+.46*np.cos(old_angle*4.5+.4))
        core = air_radius(y)
        skin = np.sqrt(np.maximum(0.,.384**2-(y-CENTER[1])**2))
        core = np.maximum(core,skin+.006)
        direction = theta-.052*np.sin(theta*4+.5)*stroke
        grain = (.0020*np.cos(30*direction+stroke*2)**4 + .0036*np.sin(13*direction+stroke))
    else:
        # Guide the forehead layers away from the off-center opening, with
        # extra drift in the longer face-framing pieces.
        spread = np.tanh((old_angle-PART)/.20)
        theta += front*spread*stroke*(.155+.047*np.sin(old_angle*2+.4))
        radius = .408-.017*ease((2.015-y)/.160)
        core = np.sqrt(np.maximum(.000001,radius**2-(y-CENTER[1])**2))
        core += .017*np.exp(-((y-2.006)/.100)**2)*ease((np.abs(old_angle-PART)-.07)/.32)
        direction = theta-.16*spread*stroke
        grain = (.0015*np.cos(31*direction+stroke*2)**4 + .0045*np.sin(11*direction+stroke*2))
        part = np.exp(-((old_angle-PART-.10*ease((y-2.12)/.09))/.062)**2)
        core -= .005*part*ease((2.213-y)/.083)
    rho = old_r+front*(core+grain-old_r)
    points[:,:,0] = rho*np.sin(theta)
    points[:,:,2] = CENTER[2]+rho*np.cos(theta)
    return points,progress,shade


def swept_pieces(material):
    pieces = [
        ((-.067,-.096,-.215,-.265),2.165,1.856,.031),
        ((-.050,-.085,-.197,-.224),2.160,1.933,.017),
        ((-.035,-.070,-.109,-.127),2.148,2.012,.0065),
        ((-.018,.040,.229,.270),2.160,1.853,.033),
        ((-.006,.038,.183,.210),2.156,1.932,.016),
        ((.002,.030,.087,.110),2.149,2.014,.0065),
    ]
    t = np.linspace(0,1,42)
    az = np.linspace(0,2*np.pi,14,endpoint=False)
    s = 1-t
    for i,((a,b,c,d),start,end,width) in enumerate(pieces):
        x = a*s**3+3*b*s*s*t+3*c*s*t*t+d*t**3
        y = start+(end-start)*t
        r = np.sqrt(np.maximum(.000001,RADIUS**2-(y-CENTER[1])**2))
        lift = .005+.030*np.sin(np.pi*t)**1.25
        r += lift
        axis = np.column_stack((x,y,CENTER[2]+np.sqrt(np.maximum(.000001,r*r-x*x))))
        tangent = unit(np.gradient(axis,axis=0))
        side = unit(np.cross(tangent,unit(axis-CENTER)))
        normal = unit(np.cross(side,tangent))
        taper = (.78+.22*ease(t/.26))*(1-.82*ease((t-.58)/.42))
        ring = axis[:,None,:] + (width*taper)[:,None,None]*np.cos(az)[None,:,None]*side[:,None,:]
        ring += (.0034*taper)[:,None,None]*np.sin(az)[None,:,None]*normal[:,None,:]
        ones = np.ones(ring.shape[:2])
        grid_mesh("Hair / feathered accent "+str(i+1),ring,ones,ones,material,False,BANGS_COLOR,
                  loop=True,radial_normals=False)


def export_study(style):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    points,progress,shade = study_surface(style)
    material = hair_material(False,BANGS_COLOR,.37)
    shell("Hair / "+style+" fringe study",points,progress,shade,material,False,BANGS_COLOR,loop=True)
    if style == 'curtain':
        swept_pieces(material)
    path = REV/"assets"/(style+".glb")
    bpy.ops.export_scene.gltf(filepath=str(path),export_format="GLB",export_apply=True,
                              export_materials="EXPORT",export_image_format="AUTO")
    manifest = {"Feminine":{"side-sweep":{"label":"Fringe study","note":"Bare-head silhouette study",
                "fits":{"none":{"default":"./assets/"+path.name,"ombre":"./assets/"+path.name}}}}}
    (REV/(style+".json")).write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf8",newline="\n")


if __name__ == "__main__":
    for style in ("air","curtain"):
        export_study(style)
