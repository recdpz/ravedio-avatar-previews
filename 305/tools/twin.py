"""Route both long Twin Braids while retaining their woven geometry and cuffs."""
from functools import lru_cache
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"304/tools"))
from braids import old_center, smooth_profile
from fit import CENTER, ease, geometry, read_glb, surface, warp_normals, write_glb


def path(y, source, side, covered):
    if covered:
        # Stay behind the hood at cheek height and turn toward the face
        # only as the braid reaches the lower front edge.
        knots=np.array([1.01,1.13,1.22,1.30,1.36,1.42,1.47,1.52,1.58,1.65,1.74,1.85])
        x=np.array([.256,.254,.250,.245,.241,.244,.264,.298,.331,.355,.380,.388])
        z=np.array([.237,.248,.252,.245,.222,.184,.140,.100,.064,.024,-.066,-.134])
        length_support=ease((1.36-y)/.21)[:,None]
        shift=(np.interp(1.16,y,source[:,1])-.249)
        target=smooth_profile(knots,np.column_stack((side*x,z)),y,.022)
        target[:,1]+=shift*length_support[:,0]
        turn=np.exp(-((y-1.490)/.050)**2)
        target[:,0]-=side*.022*turn
        target[:,1]-=.006*turn
        start,blend=1.785,.155
        clearance=.410
    else:
        # A single approach to the chest replaces the shallower dip
        # above the breast and the abrupt second push at the shoulder.
        knots=np.array([1.01,1.13,1.22,1.30,1.37,1.45,1.53,1.61,1.69,1.78,1.86])
        x=np.array([.264,.266,.273,.285,.302,.324,.347,.366,.378,.389,.386])
        z=np.array([.204,.207,.209,.203,.188,.158,.118,.054,-.025,-.105,-.133])
        length_support=ease((1.36-y)/.22)[:,None]
        shift=(np.interp(1.16,y,source[:,1])-.173)
        target=smooth_profile(knots,np.column_stack((side*x,z)),y,.033)
        target[:,1]+=shift*length_support[:,0]
        start,blend=1.754,.171
        clearance=.404

    weight=ease((start-y)/blend)[:,None]
    result=source+(target-source)*weight
    relative=result-[0.,CENTER[2]]
    current=np.linalg.norm(relative,axis=1)
    floor=np.sqrt(np.maximum(clearance**2-(y-CENTER[1])**2,0))
    return result+relative*(np.maximum(1,floor/np.maximum(current,.001))-1)[:,None]*weight,start


@lru_cache(maxsize=24)
def front_surface(path):
    return surface(path)


def garment_support(y, sections, support, limit):
    """Seat the whole braid over the garment with a broad, smooth profile."""
    curves=np.zeros(len(y))
    dz=y[1]-y[0]
    for points in sections:
        for x,h,z in points[points[:,1]<limit]:
            front=z
            for collider in support:
                _,_,_,dist=collider.ray_cast((x,h,.63),(0,0,-1),.63)
                if dist is not None:
                    front=max(front,.63-dist+.005)
            row=np.clip(round((h-y[0])/dz),0,len(y)-1)
            curves[row]=max(curves[row],front-z)
    spread=.26*np.abs(y[:,None]-y[None,:])
    guard=np.maximum(0,np.max(curves[None,:]-spread,axis=1))
    smoothed=smooth_profile(y,guard[:,None],y,.023)[:,0]
    return np.maximum(curves,smoothed+.005*ease(smoothed/.009))

def fit(source,target,covered,support_paths):
    model,buf=read_glb(source)
    parts=list(geometry(model,buf))
    braid=parts[0]
    center_source=braid[2]@braid[4].T+braid[5]
    supports=tuple(front_surface(p) for p in support_paths)
    y=np.linspace(1.00,1.985,230)
    for side in (-1,1):
        original=old_center(center_source[center_source[:,0]*side>0],y)
        fitted,start=path(y,original,side,covered)
        motion=fitted-original

        def warp(p):
            result=p.copy()
            result[:,0]+=np.interp(p[:,1],y,motion[:,0])
            result[:,2]+=np.interp(p[:,1],y,motion[:,1])
            return result

        sections=[]
        for _,_,points,_,rotation,offset,_ in parts:
            world=points@rotation.T+offset
            sections.append(warp(world[world[:,0]*side>0]))
        motion[:,1]+=garment_support(y,sections,supports,1.39)

        for _,bounds,points,normals,rotation,offset,_ in parts:
            p=points@rotation.T+offset
            use=(p[:,0]*side>0)&(p[:,1]<start)
            n=normals[use]@rotation.T
            points[use]=(warp(p[use])-offset)@rotation
            normals[use]=warp_normals(warp,p[use],n)@rotation
            bounds.update(min=points.min(axis=0).tolist(),max=points.max(axis=0).tolist())
    write_glb(target,model,buf)
