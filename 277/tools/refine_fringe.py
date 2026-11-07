"""Sculpt an airy fringe with volume above the forehead and soft, tucked tips."""
import json
import math
import sys
from pathlib import Path

import numpy as np

REV = Path(__file__).resolve().parents[1]
ROOT = REV.parent
sys.path.insert(0,str(ROOT/"275/tools"))
from build_hair import (BANGS_COLOR, CENTER, HATS, RADIUS, bangs_body, cloth_for, ease,
                        export_hair, fit_crown, grid_mesh, surface, unit)


def fringe_hairline(azimuth, existing):
    front = 1-ease((np.abs(azimuth)-.46)/.28)
    # A shallow, asymmetric edge under the wisps keeps the forehead open.
    seats = np.array([-.56,-.34,-.10,.17,.43])
    seat = np.exp(-((azimuth[...,None]-seats)/.074)**2).max(axis=-1)
    edge = 2.109 + .012*np.sin(azimuth*7+.75) - .013*seat
    return existing + front*(edge-existing)


def low_crown(hat):
    points, fraction, shade = bangs_body(hat,hairline=fringe_hairline)
    radial = unit(points-CENTER)
    angle = np.arctan2(radial[:,:,0],radial[:,:,2])
    front = 1-ease((np.abs(angle)-.48)/.25)
    t = np.linspace(0,1,points.shape[0])[:,None]
    edge = ease((t-.47)/.53)
    points -= (.0165*front*edge)[...,None]*radial
    return points,fraction,shade


def airy_fringe(material, ombre, hat, cloth):
    # Curves specify root, outward bend, return bend, and tip across the
    # forehead, then root/tip height, half-width and the arch's height.
    locks = [
        (-.133,-.151,-.188,-.176,2.154,1.963,.015,.043),
        (-.115,-.131,-.149,-.147,2.158,2.004,.006,.034),
        (-.083,-.096,-.112,-.091,2.165,1.978,.013,.045),
        (-.063,-.062,-.059,-.047,2.169,2.011,.007,.033),
        (-.023,-.022,.024,.015,2.168,1.958,.014,.047),
        (-.001,.008,.022,.028,2.171,1.996,.006,.035),
        (.035,.050,.088,.074,2.162,1.975,.014,.044),
        (.072,.088,.121,.113,2.156,2.001,.007,.037),
        (.108,.131,.182,.159,2.151,1.962,.013,.042),
    ]
    t = np.linspace(0,1,59)
    ring_angle = np.linspace(0,math.tau,16,endpoint=False)
    for i,(root,a,b,tip,start,end,width,lift) in enumerate(locks):
        closed_hat = hat in {"cap","beanie","bucket","cowboy"}
        if closed_hat:
            end += .005
        y = start + (end-start)*t
        x = root*(1-t)**3 + 3*a*t*(1-t)**2 + 3*b*t*t*(1-t) + tip*t**3
        scalp_z = CENTER[2]+np.sqrt(np.maximum(0.,RADIUS**2-x*x-(y-CENTER[1])**2))
        arc = ease((t-.13)/.58)*(1-np.clip((t-.71)/.29,0,1)**1.55)
        depth = (.012*(1-t)+.005*t) + lift*arc*(.42 if closed_hat else 1)
        axis = np.stack((x,y,scalp_z+depth),axis=-1)
        tangent = unit(np.gradient(axis,axis=0))
        side = unit(np.cross(tangent,unit(axis-CENTER)))
        normal = unit(np.cross(side,tangent))
        twist = .14*np.sin(i*1.8+.3)*np.sin(np.pi*t)
        turned_side = side*np.cos(twist[:,None])+normal*np.sin(twist[:,None])
        turned_normal = unit(np.cross(turned_side,tangent))

        # Thin, flattened locks end with a curved cap and taper by different
        # amounts. Broad roots sit inside the crown.
        taper = (.85+.15*ease(t/.35))*(1-.58*ease((t-.40)/.58))
        rounded = np.sqrt(np.maximum(.012,1-np.clip((t-.968)/.032,0,1)**2))
        taper *= rounded
        ring = axis[:,None,:]+width*taper[:,None,None]*np.cos(ring_angle)[None,:,None]*turned_side[:,None,:]
        ring += (.0047*taper)[:,None,None]*np.sin(ring_angle)[None,:,None]*turned_normal[:,None,:]
        if cloth:
            ring = fit_crown(ring,cloth,hat)
        fraction = np.full(ring.shape[:2],.16)
        grid_mesh(f"Fringe / arched wisp {i+1:02d}",ring,fraction,np.ones_like(fraction),material,
                  ombre,BANGS_COLOR,loop=True,radial_normals=False)


def build_fringe(revision=REV, lob=low_crown, fringe=airy_fringe, export=export_hair):
    catalogue = json.loads((ROOT/"276/hair-fits.json").read_text(encoding="utf8"))
    feminine = catalogue["Feminine"]
    for fit in feminine["space-buns"]["fits"].values():
        for color,file in fit.items():
            fit[color] = "../276/"+file.removeprefix("./")
    fits = feminine["side-sweep"]["fits"]
    for hat in HATS:
        if hat == "ears":
            fits[hat] = fits["none"]
            continue
        path = cloth_for("side-sweep",hat)
        cloth = surface(path) if path else None
        for color in ("default","ombre"):
            result = export("side-sweep",hat,color=="ombre",cloth,output=revision/"assets",
                                 lob_shape=lob,fringe_shape=fringe)
            fits[hat][color] = "./assets/"+result.name
    (revision/"hair-fits.json").write_text(json.dumps(catalogue,indent=2)+"\n",encoding="utf8",newline="\n")


if __name__ == "__main__":
    build_fringe()
