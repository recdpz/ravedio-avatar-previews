"""Carry the woven braids down the side before they settle over the top."""
from functools import lru_cache
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"307/tools"))
from braidfit import BRAID_SIZE, HEIGHTS, RING_COUNT, SIDES, TIE_SIZE, WEAVE_SIZE, shading, tangent
from twin import garment_support, smooth_profile
from fit import ease, geometry, read_glb, surface, tree, turn_along_path, write_glb

# Heights ascend from the tips to the cheek. The braid follows a nearly
# vertical fall alongside the head, then advances over the chest in one turn.
KNOTS = [1.06,1.15,1.24,1.31,1.37,1.43,1.49,1.55,1.62,1.70,1.77]
ACROSS = [.235,.243,.253,.266,.286,.313,.342,.369,.388,.399,.392]
FORWARD = [.198,.208,.225,.210,.176,.120,.063,.017,-.020,-.061,-.102]


def guide(center,side):
    y = center[:,1]
    curve = center.copy()
    profile = smooth_profile(np.asarray(KNOTS),np.column_stack((side*np.asarray(ACROSS),FORWARD)),
                             HEIGHTS,.027)
    blend = ease((1.80-y)/.153)
    for i,axis in enumerate((0,2)):
        curve[:,axis] += blend*(np.interp(y,HEIGHTS,profile[:,i])-center[:,axis])
    return curve


def carry(weave,band,center,rail):
    old_axis,new_axis = tangent(center),tangent(rail)
    sections = weave[:WEAVE_SIZE].reshape(3,RING_COUNT,SIDES,3)
    relative = (sections-center[None,:,None,:]).reshape(-1,3)
    a,b = [np.tile(np.repeat(axis,SIDES,axis=0),(3,1)) for axis in (old_axis,new_axis)]
    moved = turn_along_path(relative,a,b).reshape(sections.shape)+rail[None,:,None,:]

    def tip(points):
        local = points-center[-1]
        return rail[-1]+turn_along_path(local,np.broadcast_to(old_axis[-1],local.shape),
                                       np.broadcast_to(new_axis[-1],local.shape))

    return np.concatenate((moved.reshape(-1,3),tip(weave[WEAVE_SIZE:]))),tip(band)


@lru_cache(maxsize=32)
def collider(path):
    return surface(path)


def contact(mesh, other):
    return len({i for i,_ in mesh.overlap(other)})


def fit(source,target,base,top):
    doc,data = read_glb(source)
    parts = list(geometry(doc,data))
    originals = [p@r.T+offset for _,_,p,_,r,offset,_ in parts]
    assert [len(p) for p in originals]==[2*BRAID_SIZE,2*TIE_SIZE],source
    support = [collider(base),collider(top)]
    lower = [face[points[face,1].min(axis=1)<1.53]
             for points,(*_,face) in zip(originals,parts,strict=True)]
    for strength in (1.,.80,.63,.45,.28,.12):
        for widen in (0.,.014,.027):
            result = [points.copy() for points in originals]
            for i,side in enumerate((-1,1)):
                wb = slice(i*BRAID_SIZE,(i+1)*BRAID_SIZE)
                tb = slice(i*TIE_SIZE,(i+1)*TIE_SIZE)
                weave,band = originals[0][wb],originals[1][tb]
                center = weave[:WEAVE_SIZE].reshape(3,RING_COUNT,SIDES,3).mean(axis=(0,2))
                desired = guide(center,side)
                rail = center+(desired-center)*strength
                rail[:,0] += side*widen*np.exp(-((rail[:,1]-1.445)/.109)**2)
                trial = carry(weave,band,center,rail)
                push = garment_support(HEIGHTS,trial,support,1.49)
                y = rail[:,1]
                support_blend = ease((1.548-y)/.070)
                rail[:,2] += np.interp(y,HEIGHTS,push)*support_blend
                moved,tie = carry(weave,band,center,rail)
                weight = ease((1.78-center[:,1])/.06)
                blend = np.r_[np.tile(np.repeat(weight,SIDES),3),np.ones(BRAID_SIZE-WEAVE_SIZE)]
                result[0][wb] = weave+(moved-weave)*blend[:,None]
                result[1][tb] = tie
            for points,faces,(_,_,_,_,_,_,full) in zip(result,lower,parts,strict=True):
                if contact(tree(points,faces),support[0]) or contact(tree(points,full),support[1]):
                    break
            else:
                for part,old,new in zip(parts,originals,result,strict=True):
                    _,bounds,pos,normal,rot,offset,faces = part
                    touched = np.linalg.norm(new-old,axis=1)>1e-8
                    weight = ease((1.78-old[:,1])/.15)
                    normals = shading(new,faces,normal@rot.T,weight)
                    pos[touched] = (new[touched]-offset)@rot
                    normal[touched] = normals[touched]@rot
                    bounds.update(min=pos.min(0).tolist(),max=pos.max(0).tolist())
                write_glb(target,doc,data)
                return {"strength":strength,"shoulderEase":widen}
    raise ValueError(f"No braid route clears {top.name} with {source.name}")
