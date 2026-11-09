"""Author the front box-braid fall and a low exit from the pashmina."""
import json
from pathlib import Path
import sys

import numpy as np

REV = Path(__file__).resolve().parents[1]
ROOT = REV.parent
sys.path.insert(0,str(ROOT/"299/tools"))
from fit import CENTER, ease, geometry, islands, read_glb, warp_normals, write_glb


def braid_groups(doc, data):
    braid,cuff = geometry(doc,data)
    points,tips = (part[2]@part[4].T+part[5] for part in (braid,cuff))
    tip_groups = islands(tips,cuff[-1])
    labels = np.unique(tip_groups)
    centers = np.array([tips[tip_groups==label].mean(axis=0) for label in labels])
    woven = islands(points,braid[-1])
    groups = np.empty(len(points),dtype=int)
    matches = np.zeros(len(labels),dtype=int)
    for label in np.unique(woven):
        member = woven==label
        ply = points[member]
        end = ply[ply[:,1] < ply[:,1].min()+.05].mean(axis=0)
        nearest = np.argmin(np.linalg.norm((centers-end)*[1,.4,1],axis=1))
        groups[member] = labels[nearest]
        matches[nearest] += 1
    assert np.all(matches==4)
    return braid,cuff,points,tips,groups,tip_groups,labels


def smooth_profile(y, data, sample_y, spread):
    values = np.column_stack([np.interp(sample_y,y,axis) for axis in data.T])
    half = int(np.ceil(spread*3/(sample_y[1]-sample_y[0])))
    kernel = np.exp(-.5*(np.arange(-half,half+1)*(sample_y[1]-sample_y[0])/spread)**2)
    kernel /= kernel.sum()
    return np.column_stack([np.convolve(np.pad(axis,half,mode="edge"),kernel,"valid") for axis in values.T])


def old_center(points, y):
    bins = np.floor((points[:,1]-y[0])/.010).astype(int)
    samples = np.array([points[bins==i].mean(axis=0) for i in np.unique(bins)])
    return smooth_profile(samples[:,1],samples[:,[0,2]],y,.017)


def guides(y, rank, covered, angle, sign):
    if not covered:
        knots = [1.17,1.29,1.39,1.49,1.59,1.72,1.85,1.98]
        x = np.array([.179,.186,.197,.208,.219,.229,.232,.220])+.031*rank
        z = np.array([.272,.276,.273,.258,.266,.310,.317,.301])-.031*rank*np.array([.29,.23,.20,.54,.82,1,1,1])
        target = smooth_profile(np.array(knots),np.column_stack((x*sign,z)),y,.023)
    else:
        # Bring the front row inside the scarf from the crown onward.
        # Hold a rounded clearance around the head until the lower opening.
        theta = 1.265+.545*np.clip((angle-.61)/1.21,0,1)
        radius = np.sqrt(np.maximum(.405**2-(y-CENTER[1])**2,.10**2))
        radius += .006*(rank%2) + .004*ease((y-1.54)/.20)*ease((2.15-y)/.15)
        under = np.column_stack((sign*radius*np.sin(theta),CENTER[2]+radius*np.cos(theta)))
        if rank<3:
            # Round the lower side edge before advancing over the chest.
            knots = [1.16,1.25,1.33,1.39,1.44,1.49,1.54,1.60]
            x = np.array([.184,.189,.198,.214,.235,.263,.292,.332])+rank*np.array([.040,.040,.037,.033,.029,.026,.018,.012])
            z = np.array([.286,.289,.277,.233,.190,.145,.116,.114])-rank*np.array([.003,.002,.002,.004,.008,.011,.018,.029])
            exit_path = smooth_profile(np.array(knots),np.column_stack((x*sign,z)),y,.018)
            turn=(rank/2)**2*np.exp(-((y-1.486)/.046)**2)
            exit_path[:,0] -= sign*(.016*turn + .013*(rank/2)**2*np.exp(-((y-1.464)/.037)**2))
            exit_path[:,1] -= .014*turn
            blend = ease((1.63-y)/.099)[:,None]
            target = under*(1-blend)+exit_path*blend
        else:
            # Keep the side braids in the cape until they clear its lower
            # edge. Dropping them at the front would cross the neckline.
            lower = ease((1.64-y)/.28)
            lower_angle = theta+(.29-.013*(rank-3))*lower
            knots = [1.16,1.25,1.31,1.36,1.41,1.46,1.52,1.61]
            lower_radius = smooth_profile(np.array(knots),
                np.array([.306,.312,.306,.289,.279,.288,.303,.344])[:,None],y,.016)[:,0]
            lower_radius += .008*(rank%2)
            falling=np.column_stack((sign*lower_radius*np.sin(lower_angle),
                                     CENTER[2]+lower_radius*np.cos(lower_angle)))
            blend=ease((1.65-y)/.105)[:,None]
            target=under*(1-blend)+falling*blend
    return target

def process(source, target, covered, basis):
    model,data=read_glb(source)
    original_braid,original_cuff,_,_,groups,cuffs,labels=braid_groups(*read_glb(basis))
    braid,cuff=geometry(model,data)
    assert np.array_equal(braid[-1],original_braid[-1]) and np.array_equal(cuff[-1],original_cuff[-1])
    points,tips=(part[2]@part[4].T+part[5] for part in (braid,cuff))
    rails={}
    for label in labels:
        sample=points[(groups==label)&(abs(points[:,1]-1.88)<.025)]
        center=sample.mean(axis=0)
        rails[label]=(np.sign(center[0]),np.arctan2(abs(center[0]),center[2]+.015))
    changed=[]
    for side in (-1,1):
        ordered=sorted((label for label in labels if rails[label][0]==side),key=lambda l:rails[l][1])
        for rank,label in enumerate((label for label in ordered if rails[label][1]<1.82) if covered else ordered[:3]):
            y=np.linspace(1.12,2.21,220)
            original=old_center(points[groups==label],y)
            target_center=guides(y,rank,covered,rails[label][1],side)
            start,end=(2.185,.225) if covered else (1.853,.220)
            w=np.clip((start-y)/end,0,1)
            blend=w*w*(3-2*w)
            center=original+(target_center-original)*blend[:,None]
            relative=center-[0.,CENTER[2]]
            radius=np.linalg.norm(relative,axis=1)
            skin=np.sqrt(np.maximum(.404**2-(y-CENTER[1])**2,0))
            factor=np.maximum(1,skin/np.maximum(radius,.001))
            correction=(relative*(factor-1)[:,None])*blend[:,None]
            delta=center-original+correction

            def warp(p):
                shifted=p.copy()
                shifted[:,0]+=np.interp(p[:,1],y,delta[:,0])
                shifted[:,2]+=np.interp(p[:,1],y,delta[:,1])
                return shifted

            for part,p,labels_for_part in [(braid,points,groups),(cuff,tips,cuffs)]:
                _,bounds,position,normal,rotation,offset,_=part
                mask=(labels_for_part==label)&(p[:,1]<start)
                local=p[mask]
                position[mask]=(warp(local)-offset)@rotation
                normal[mask]=warp_normals(warp,local,normal[mask]@rotation.T)@rotation
                bounds.update(min=position.min(axis=0).tolist(),max=position.max(axis=0).tolist())
            changed.append(int(label))
    write_glb(target,model,data)
    return changed
