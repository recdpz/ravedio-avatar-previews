"""Fit a softly rolled, see-through fringe to the approved avatar."""
import math
import sys
from pathlib import Path

import bpy
import numpy as np

REV = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(REV.parent/"277/tools"))
from refine_fringe import build_fringe
from build_hair import (BANGS_COLOR, CENTER, RADIUS, bangs_body, ease, fit_crown,
                        grid_mesh, hair_material, hit, unit)
from build_bandanas import cloth_surface

# Each group has a root angle, fall angle, end height, and individual offsets.
# The broad gaps between groups keep the fringe readable at portrait scale.
SECTIONS = (
    (-.56,-.557,1.942,(-.028,-.010,.014)),
    (-.426,-.407,1.955,(-.031,-.008,.015,.035)),
    (-.286,-.253,1.971,(-.032,-.006,.017)),
    (-.183,-.151,1.992,(-.003,)),
    (-.094,-.077,1.963,(-.031,-.010,.010,.034)),
    (.068,.083,1.972,(-.030,-.008,.012,.033)),
    (.174,.199,1.989,(-.008,.011)),
    (.258,.275,1.965,(-.029,-.010,.015,.037)),
    (.416,.422,1.956,(-.036,-.012,.009,.030)),
    (.536,.559,1.944,(-.021,-.001,.019)),
)


def feathered_edge(azimuth, original):
    centers = np.array([row[0] for row in SECTIONS])
    lanes = np.exp(-((azimuth[...,None]-centers)/.042)**2).max(axis=-1)
    edge = 2.135 + .012*np.sin(azimuth*4+.78) + .003*np.sin(azimuth*16+.3) - .013*lanes
    front = 1-ease((np.abs(azimuth)-.57)/.22)
    return original + front*(edge-original)


def feathered_crown(hat):
    points, fraction, shade = bangs_body(hat,hairline=feathered_edge)
    horizontal = points[:,:,[0,2]]-CENTER[[0,2]]
    radius = np.linalg.norm(horizontal,axis=-1)
    a = np.arctan2(horizontal[:,:,0],horizontal[:,:,1])
    t = np.linspace(0,1,points.shape[0])[:,None]
    front = 1-ease((np.abs(a)-.54)/.27)
    dy = points[:,:,1]-CENTER[1]
    # Taper gradually in head-radius space so the front continues outward
    # as it descends. A late horizontal shrink would make a shelf here.
    scalp_radius = RADIUS+.001+.030*ease((points[:,:,1]-2.102)/.111)
    contour = np.sqrt(np.maximum(.000001,scalp_radius*scalp_radius-dy*dy))
    feather = front*ease((t-.18)/.26)
    radius += feather*(contour-radius)
    centers = np.array([row[0] for row in SECTIONS])
    ridge = np.exp(-((a[...,None]-centers)/.036)**2).max(axis=-1)
    radius += .0028*front*ridge*np.sin(np.pi*t)**2
    points[:,:,0] = radius*np.sin(a)
    points[:,:,2] = CENTER[2]+radius*np.cos(a)
    return points,fraction,shade


def bezier(t,a,b,c,d):
    rest = 1-t
    return a*rest**3 + 3*b*t*rest**2 + 3*c*t*t*rest + d*t**3


def rolled_fringe(_material, ombre, hat, cloth):
    t = np.linspace(0,1,47)
    az = np.linspace(0,math.tau,12,endpoint=False)
    material = hair_material(ombre,BANGS_COLOR,.37)
    short_hat = hat in {"cap","beanie","bucket","cowboy"}
    strands = []
    crown, _, _ = feathered_crown(hat)
    cover = cloth_surface(fit_crown(crown,cloth,hat),True)
    for i,(root,fall,end,offsets) in enumerate(SECTIONS):
        for j,offset in enumerate(offsets):
            seed = i*5+j
            root_y = 2.156+.010*np.cos(root*2+.3) + .006*np.sin(seed*2.1)
            tip_y = end+.009*np.sin(seed*2.04)+(.007 if short_hat else 0)
            tip_r = np.sqrt(RADIUS*RADIUS-(tip_y-CENTER[1])**2)+.005
            root_r = np.sqrt(RADIUS*RADIUS-(root_y-CENTER[1])**2)+.010
            # A shared cubic roll puts the broadest part of the bend in the
            # same place across the forehead. Only the cut and spread vary.
            y = bezier(t,root_y,root_y-.029,tip_y+.060,tip_y)
            r = bezier(t,root_r,.258,.449 if not short_hat else .398,tip_r)
            drift = .022*np.sin(i*1.45+.4)+.004*np.sin(seed*2.44)
            a = bezier(t,.93*root+.60*offset,root+.76*offset,
                       fall+1.06*offset+drift,fall+1.16*offset+.004*np.sin(seed*1.32))
            axis = np.stack((r*np.sin(a),y,CENTER[2]+r*np.cos(a)),axis=-1)
            # Sink the fine roots where they would graze the cap surface.
            # Past the transition the full arc is free of the crown.
            for index in range(23):
                direction = unit(axis[index]-CENTER)
                surface = hit(cover,CENTER,direction)
                if surface is None:
                    continue
                clearance = (axis[index]-surface)@direction
                root_inset = .005*(1-ease((clearance+.002)/.014))
                axis[index] -= root_inset*direction
            tangent = unit(np.gradient(axis,axis=0))
            side = unit(np.cross(tangent,unit(axis-CENTER)))
            normal = unit(np.cross(side,tangent))
            half_width = .0025+.0012*(.5+.5*np.cos(seed*2.73))
            taper = (1-.58*ease((t-.55)/.43))*np.sqrt(np.maximum(
                .03,1-np.clip((t-.976)/.024,0,1)**2))
            taper *= .32+.68*ease((t-.20)/.36)
            ring = axis[:,None,:]+(half_width*taper)[:,None,None]*np.cos(az)[None,:,None]*side[:,None,:]
            ring += (.0019*taper)[:,None,None]*np.sin(az)[None,:,None]*normal[:,None,:]
            if cloth is not None:
                ring = fit_crown(ring,cloth,hat)
            fraction = np.full(ring.shape[:2],.16)
            strands.append(grid_mesh("Fringe / fine strand",ring,fraction,np.ones_like(fraction),
                                     material,ombre,BANGS_COLOR,loop=True,radial_normals=False))

    # Batch the independently shaped wisps into one selectable hair mesh.
    bpy.context.view_layer.objects.active = strands[0]
    with bpy.context.temp_override(active_object=strands[0],selected_editable_objects=strands):
        bpy.ops.object.join()
    strands[0].name = "Fringe / fine strands"


if __name__ == "__main__":
    build_fringe(REV,lob=feathered_crown,fringe=rolled_fringe)
