"""Build a softly parted fringe from coherent groups that feather at the ends."""
import sys
from functools import partial
from pathlib import Path

import numpy as np

REV = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"279/tools"))
from layer_fringe import ANGLE_GRID, CENTER, RADIUS, bangs_body, build_fringe, cubic, ease
from layer_fringe import export_layered, fit_crown, unit

# Angle, root width, mean hem height, sweep, and offsets for the fine ends.
# The wider side groups continue the fringe toward the temple.
GROUPS = (
    (-.665,.138,1.923,-.043,((-.010,-.008),(.009,.003),(.022,.007))),
    (-.467,.168,1.949,-.057,((-.009,-.007),(.011,0.),(-.002,.007))),
    (-.267,.157,1.974,-.048,((-.008,-.004),(.008,.005))),
    (-.051,.166,1.974,.074,((.011,-.009),(-.004,0.),(.003,.007))),
    (.148,.195,1.964,.071,((.014,-.009),(-.006,0.),(.003,.009))),
    (.363,.183,1.945,.060,((.016,-.008),(-.008,0.),(.004,.008))),
    (.573,.143,1.927,.039,((.015,-.006),(-.005,0.),(.004,.005))),
)
PART = -.155
CLOSED_HATS = {"cap","beanie","bucket","cowboy"}


def rim(angle, original, hat):
    front = 1-ease((np.abs(angle)-.75)/.25)
    separation = .014*np.exp(-((angle-PART)/.116)**2)
    flow = 2.131 + separation + .006*np.sin(angle*8+.6)
    flow -= .054*ease((np.abs(angle)-.32)/.50)
    shoulder = ease((np.abs(angle)-.54)/.91)
    # The borrowed side drape starts descending at the temples. Compensate
    # there so a single fringe group spans a gently sloped root, not a ledge.
    flow += (.593 if hat=="pashmina" else .706)*shoulder
    return original + front*(flow-original)


def front_crown(hat):
    sections = [np.linspace(angle-width*.5,angle+width*.5,19) for angle,width,_,_,_ in GROUPS]
    limit = .94
    angles = np.unique(np.concatenate((ANGLE_GRID[np.abs(ANGLE_GRID)>limit],
                                       np.linspace(-limit,limit,71),*sections)))
    points,progress,shade = bangs_body(hat,hairline=lambda a,o:rim(a,o,hat),angles=angles)
    y = points[:,:,1]
    dz = points[:,:,2]-CENTER[2]
    a = np.arctan2(points[:,:,0],dz)
    rho = np.hypot(points[:,:,0],dz)
    front = 1-ease((np.abs(a)-.66)/.28)
    mask = front*ease((2.212-y)/.065)

    # Run the crown grain down from a shallow, off-center part. It gradually
    # turns in the same direction as each side of the fringe.
    length = ease((2.185-y)/.105)
    part_line = PART+.115*ease((y-2.121)/.090)
    guide = a - .14*np.tanh((a-part_line)/.27)*length
    seam = np.exp(-((a-part_line)/.061)**2)*np.sin(np.pi*ease((y-2.112)/.096))**2
    radius = .412 - .012*ease((2.201-y)/.111) - .0058*seam
    surface = np.sqrt(np.maximum(.000001,radius**2-(y-CENTER[1])**2))
    surface += (.0026*np.cos(17*guide+.4)**4+.0017*np.sin(13*guide+2*length))*ease((2.213-y)/.095)
    rho += mask*(surface-rho)
    points[:,:,0] = rho*np.sin(a)
    points[:,:,2] = CENTER[2]+rho*np.cos(a)
    rows = np.r_[0:len(points):2,len(points)-1]
    windows = [np.flatnonzero((angles>=section[0])&(angles<=section[-1])) for section in sections]
    return points[rows],progress[rows],shade[rows],windows


def layers(anchor, higher, end, sweep, hat):
    mid = len(anchor)//2
    root = anchor[mid]
    step = unit(root-higher[mid])
    root_r = np.linalg.norm((root-CENTER)[[0,2]])
    root_a = np.arctan2(root[0],root[2]-CENTER[2])
    covered = hat in CLOSED_HATS
    if covered:
        end += .012
    tip_r = np.sqrt(RADIUS**2-(end-CENTER[1])**2)+.005
    t = np.linspace(0,1,49)
    y = root[1]+(end-root[1])*t

    # Crest in the upper-middle length, then an unhurried return to the
    # skin. Use the actual crown tangent at the root of each group.
    temple = ease((abs(root_a)-.42)/.27)
    crest = .61
    reach = (.005 if covered else .014) - .007*temple
    crest_r = max(root_r+.009,tip_r+reach)
    slope = ((step[0]*np.sin(root_a)+step[2]*np.cos(root_a))/max(.12,-step[1]))
    lead = min(crest_r-.004,root_r+.33*crest*(root[1]-end)*max(.25,slope))
    before = cubic(np.minimum(t/crest,1),root_r,lead,crest_r,crest_r)
    after = cubic(np.maximum((t-crest)/(1-crest),0),crest_r,crest_r,tip_r+.35*reach,tip_r)
    r = np.where(t<=crest,before,after)
    skin = np.sqrt(np.maximum(0.,RADIUS**2-(y-CENTER[1])**2))
    r = np.maximum(r,skin+.004)
    tip_x = tip_r*np.sin(root_a+sweep)
    x = cubic(t,root[0],root[0]+.043*step[0],tip_x-.009*np.sign(sweep),tip_x)
    axis = np.column_stack((x,y,CENTER[2]+np.sqrt(np.maximum(.000001,r*r-x*x))))
    tangent = unit(np.gradient(axis,axis=0))
    radial = unit(axis-CENTER)
    side = unit(np.cross(tangent,radial))
    side *= np.sign((anchor[-1]-anchor[0])@side[0])
    normal = unit(np.cross(side,tangent))
    normal *= np.sign(normal[0]@(root-CENTER))

    u = np.linspace(-1,1,len(anchor))
    taper = 1-.51*ease(t)
    width = .5*abs((anchor[-1]-anchor[0])@side[0])*taper
    form = axis[:,None,:]+(width[:,None]*u[None,:])[:,:,None]*side[:,None,:]
    grooves = (1-u*u)*(.0028+.0014*np.cos(u*10.3+.55))
    form += (np.sin(np.pi*t)**1.2)[:,None,None]*grooves[None,:,None]*normal[:,None,:]
    exact = axis[:,None,:] + (anchor-root)[None,:,:]*taper[:,None,None]
    mix = ease(t/.36)[:,None,None]
    result = exact*(1-mix)+form*mix
    result[0] = anchor
    return result


def fine_end(strip, dy, dx):
    t = np.linspace(0,1,len(strip))
    center = strip.mean(axis=1)
    shift = ease(t)
    old_y = center[:,1]-CENTER[1]
    new_y = old_y+.63*dy*shift
    # Maintain the distance to the curved forehead as each tip fans out.
    head_r = np.sqrt(np.maximum(0.,RADIUS**2-old_y*old_y))
    tip_r = np.sqrt(np.maximum(0.,RADIUS**2-new_y*new_y))
    rho = np.linalg.norm((center-CENTER)[:,[0,2]],axis=1)+tip_r-head_r
    x = center[:,0]+.63*dx*shift
    z = CENTER[2]+np.sqrt(np.maximum(.000001,rho*rho-x*x))
    axis = np.column_stack((x,new_y+CENTER[1],z))
    taper = 1-.55*ease((t-.14)/.86)
    result = axis[:,None,:]+(strip-center[:,None,:])*taper[:,None,None]
    u = np.linspace(-1,1,strip.shape[1])
    rounded_end = 1-np.sqrt(np.maximum(0.,1-u*u))
    result[:,:,1] += .0038*ease((t-.77)/.23)[:,None]*rounded_end[None,:]
    result[0] = strip[0]
    return result


def mesh_geometry(hat, cloth):
    points,progress,shade,windows = front_crown(hat)
    rows,cols,_ = points.shape
    fitted = fit_crown(points,cloth,hat)
    vertices = fitted.reshape(-1,3).tolist()
    faces = [(j*cols+i,(j+1)*cols+i,(j+1)*cols+(i+1)%cols,j*cols+(i+1)%cols)
             for j in range(rows-1) for i in range(cols)]
    faces.append(tuple(range(cols)))
    color_length = progress.ravel().tolist()
    color_shade = shade.ravel().tolist()
    thickness = [1.]*len(vertices)

    def grow(strip, previous, first_weight, last_weight, tint):
        strip = fit_crown(strip,cloth,hat)
        for index,row in enumerate(strip[1:],1):
            start = len(vertices)
            vertices.extend(row.tolist())
            current = list(range(start,start+len(row)))
            faces.extend((previous[k],current[k],current[k+1],previous[k+1]) for k in range(len(row)-1))
            color_length.extend([.16]*len(row))
            color_shade.extend(tint)
            weight = first_weight+(last_weight-first_weight)*ease(index/(len(strip)-1))
            thickness.extend([float(weight)]*len(row))
            previous = current
        return np.array(previous)

    for index,(ids,(_,_,end,sweep,ends)) in enumerate(zip(windows,GROUPS,strict=True)):
        strip = layers(points[-1,ids],points[-2,ids],end,sweep,hat)
        split = [33,31,34,31,30,34,33][index]
        root = (rows-1)*cols+ids
        tones = shade[-1,ids].tolist()
        parent = grow(strip[:split+1],root,1.,.50,tones)
        # Small gaps at different heights open the loose groups into fine tips.
        for segment,(dy,dx) in zip(np.array_split(np.arange(len(ids)),len(ends)),ends,strict=True):
            child = fine_end(strip[split:,segment],dy,dx)
            grow(child,parent[segment],.50,.19,[tones[i] for i in segment])
    return vertices,faces,np.array(color_length),np.array(color_shade),thickness


if __name__ == "__main__":
    build_fringe(REV,export=partial(export_layered,mesh_shape=mesh_geometry))
