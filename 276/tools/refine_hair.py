"""Refine the 275 hairstyles in the same avatar and headwear coordinates."""
import sys
from pathlib import Path

import numpy as np

REV = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(REV.parent/"275/tools"))
from build_hair import CENTER, bangs_body, build_catalogue, ease, release_back, unit


def refined_waves(points, hat):
    base = release_back(points,hat)
    if hat == "pashmina":
        return base  # The longer sections stay tucked into the existing hood fit.

    x,y,z = (base-CENTER).T
    angle = np.arctan2(x,-z)
    weight = ease((-.010-y)/.27)*ease((1.43-np.abs(angle))/.33)
    progress = ease((-.052-y)/.46)
    mid = np.array([-1.15,-.83,-.47,-.08,.31,.70,1.05])
    phase = np.array([.2,1.4,2.5,3.6,4.8,5.5,6.3])
    sweep = .112*np.sin(progress[:,None]*5.2+phase) + .041*np.sin(progress[:,None]*8.3+phase*.73)
    mid = mid + progress[:,None]*sweep
    boundaries = (mid[:,1:]+mid[:,:-1])*.5

    width = np.array([.125,.127,.141,.150,.139,.126,.123])
    crowns = np.exp(-((angle[:,None]-mid)/width)**2)
    seams = np.exp(-((angle[:,None]-boundaries)/.041)**2)
    amplitudes = .021 + .010*np.sin(progress[:,None]*5.8+phase)
    relief = weight*((crowns*amplitudes).sum(axis=1)-.010*seams.max(axis=1))
    hem = ease((-.377-y)/.13) * weight
    soft_notches = np.exp(-((angle[:,None]-boundaries)/.066)**2).max(axis=1)
    rise = hem*(.023*soft_notches + .008*np.sin(angle*8+.4))
    r = np.hypot(x,z) + relief
    return CENTER + np.stack((r*np.sin(angle),y+rise,-r*np.cos(angle)),axis=-1)


def soft_hairline(azimuth, previous):
    # The tips are lobes of the same surface as the crown. Each has its own
    # width and fall, with visible forehead in the spaces between them.
    center = np.array([-.525,-.398,-.281,-.153,-.044,.091,.215,.358,.499])
    length = np.array([.106,.077,.115,.073,.113,.079,.109,.090,.116])
    width = np.array([.051,.037,.047,.035,.046,.038,.048,.038,.051])
    weight = np.exp(-(np.abs(azimuth[...,None]-center)/width)**3.1)
    fall = (weight*length).max(axis=-1)
    curved = 2.091 + .006*np.sin(azimuth*9+.38) - fall
    middle = 1-ease((np.abs(azimuth)-.58)/.17)
    return previous + middle*(curved-previous)


def soft_lob(hat):
    outer = np.linspace(-np.pi,np.pi,193)[:-1]
    angles = np.concatenate((outer[outer<-.76],np.linspace(-.76,.76,193),outer[outer>.76]))
    points, fraction, shade = bangs_body(hat,hairline=soft_hairline,angles=angles)
    radial = unit(points-CENTER)
    azimuth = np.arctan2(radial[:,:,0],radial[:,:,2])
    front = 1-ease((np.abs(azimuth)-.51)/.23)
    y = points[:,:,1]
    drop = ease((2.122-y)/.158)*front
    bend = drop*(.105+.071*np.sin(azimuth*7+.66)) - .034*drop**3
    x,z = points[:,:,0].copy(),points[:,:,2]-CENTER[2]
    points[:,:,0] = x*np.cos(bend)+z*np.sin(bend)
    points[:,:,2] = CENTER[2]+z*np.cos(bend)-x*np.sin(bend)
    edge = ease((np.linspace(0,1,points.shape[0])-.73)/.27)[:,None]
    points -= (.008*front*edge)[...,None]*unit(points-CENTER)
    return points, fraction, shade


if __name__ == "__main__":
    (REV/"assets").mkdir(exist_ok=True)
    build_catalogue(REV,bun_shape=refined_waves,lob_shape=soft_lob,fringe_shape=None)
