"""Integrate the approved 334 B source with authored contact fits and ombre."""
import sys
sys.dont_write_bytecode=True
import hashlib
import json
import os
import shutil
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'296/tools'))
from drape import CENTER, warp_normals, surface, read_glb, write_glb
TO_BLENDER=np.array(((1,0,0),(0,0,1),(0,-1,0)))

BASE=Path('D:/Ravedio-Avatar-Work/native330')
APPROVED=Path('D:/Ravedio-Avatar-Work/native334')
OUTPUT=Path('D:/Ravedio-Avatar-Work/native335')
HATS=('none','cap','beanie','bucket','cowboy','ears','headband','pashmina')


def load(path):return json.loads(path.read_bytes())
def save(path,value):path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf8')
def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def ease(x):
    x=np.clip(x,0,1)
    return x*x*(3-2*x)
def normalized(x):return x/np.maximum(np.linalg.norm(x,axis=-1,keepdims=True),1e-9)


def translate_component(digest,dy,catalogue):
    source=BASE/catalogue['components'][digest]['file']
    doc,data=read_glb(source)
    for scene in doc['scenes']:
        for root in scene.get('nodes',[]):
            node=doc['nodes'][root]
            if 'matrix' in node:node['matrix'][13]+=dy
            else:
                node.setdefault('translation',[0,0,0])
                node['translation'][1]+=dy
    pending=OUTPUT/'translated.glb';write_glb(pending,doc,data)
    revised=sha(pending);destination=OUTPUT/'assets'/f'{revised}.glb'
    if destination.exists():pending.unlink()
    else:pending.replace(destination)
    catalogue['components'][revised]={'file':'assets/'+destination.name,'bytes':destination.stat().st_size}
    return revised


def contact_field(path):
    tree=surface(path)
    width,height=256,129
    yaw=np.arange(width)*2*np.pi/width-np.pi
    pitch=np.linspace(-np.pi/2,np.pi/2,height)
    field=np.full((height,width),.86)
    for row,v in enumerate(pitch):
        directions=np.column_stack((np.cos(v)*np.sin(yaw),np.full(width,np.sin(v)),np.cos(v)*np.cos(yaw)))
        for col,direction in enumerate(directions):
            _,_,_,distance=tree.ray_cast(Vector(CENTER),Vector(direction),.70)
            if distance is not None:
                field[row,col]=distance-.006
    # A short pressure transition around physical contact, not a global cap
    # warp that presses fringe where the fabric does not reach.
    for _ in range(4):
        field=np.minimum.reduce((field,np.roll(field,1,axis=1)+.007,
            np.roll(field,-1,axis=1)+.007,np.vstack((field[:1],field[:-1]))+.007,
            np.vstack((field[1:],field[-1:]))+.007))
    return field


def field_at(field,direction):
    height,width=field.shape
    u=(np.arctan2(direction[:,0],direction[:,2])+np.pi)*width/(2*np.pi)
    v=(np.arcsin(np.clip(direction[:,1],-1,1))+np.pi/2)*(height-1)/np.pi
    col=np.floor(u).astype(int)
    row=np.minimum(np.floor(v).astype(int),height-2)
    x,y=u-col,v-row
    a,b=col%width,(col+1)%width
    return (field[row,a]*(1-x)+field[row,b]*x)*(1-y)+(field[row+1,a]*(1-x)+field[row+1,b]*x)*y


def fit_warp(field,hat):
    def warp(points):
        relative=points-CENTER
        theta=np.arctan2(relative[:,0],relative[:,2])
        if hat=='pashmina':
            # A short bob folds toward the nape under the hood. Its front
            # curtain fringe remains free in the face opening.
            lower=ease((1.83-points[:,1])/.34)
            side=ease((np.abs(theta)-.90)/.65)
            theta+=np.sign(theta)*.10*lower*side
            radial=np.hypot(relative[:,0],relative[:,2])
            radial-=.020*lower*side
            moved=points.copy()
            moved[:,0]=radial*np.sin(theta)
            moved[:,1]+=.040*lower*side
            moved[:,2]=CENTER[2]+radial*np.cos(theta)
        else:
            moved=points
        relative=moved-CENTER
        radius=np.linalg.norm(relative,axis=1)
        direction=normalized(relative)
        limit=field_at(field,direction)
        pressure=.004*np.logaddexp(0,(radius-limit)/.004)
        target=np.maximum(radius-pressure,np.minimum(radius,.388))
        return CENTER+direction*target[:,None]
    return warp


def recolor_ombre(obj):
    mesh=obj.data
    points=np.array([v.co[:] for v in mesh.vertices])@TO_BLENDER.T
    theta=np.arctan2(points[:,0],points[:,2]-CENTER[2])
    progress=(1.985-points[:,1])/.49
    progress+=.038*np.sin(5*theta+.3)*ease(progress/.6)
    blend=ease(progress)
    root=np.array((.0998987332,.0512694605,.0331047699))
    # Warm caramel tips: the short curtain ends remain mostly brown, rather
    # than acquiring the same blond tip as a full-length side section.
    srgb=np.array((184,139,92))/255
    tips=np.where(srgb<=.04045,srgb/12.92,((srgb+.055)/1.055)**2.4)
    colors=root*(1-blend[:,None])+tips*blend[:,None]
    rgba=np.column_stack((colors,np.ones(len(colors))))
    attribute=mesh.color_attributes.new(name='Bob ombre',type='FLOAT_COLOR',domain='POINT')
    attribute.data.foreach_set('color',rgba.astype(np.float32).ravel())
    mesh.color_attributes.active_color_index=len(mesh.color_attributes)-1
    mesh.color_attributes.render_color_index=len(mesh.color_attributes)-1
    material=mesh.materials[0].copy()
    material.name='Hair / brown to caramel ombre'
    nodes,links=material.node_tree.nodes,material.node_tree.links
    shader=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
    color=nodes.new('ShaderNodeVertexColor');color.layer_name=attribute.name
    links.new(color.outputs['Color'],shader.inputs['Base Color'])
    mesh.materials[0]=material


def export(obj,path):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True);bpy.context.view_layer.objects.active=obj
    bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,
                             export_materials='EXPORT',export_extras=True)


def main():
    OUTPUT.mkdir(parents=True,exist_ok=True)
    assets=OUTPUT/'assets';assets.mkdir(exist_ok=True)
    catalogue=load(BASE/'catalogue.json')
    original=load(BASE/'catalogue.json')
    approval=load(ROOT/'approvals/bob334-waves.json')['approved_assets']['Feminine-bob']
    assert sha(APPROVED/'waves.glb')==approval['sha256']
    assert sha(APPROVED/'Ravedio334-waves.blend')==approval['source_sha256']
    ear_row=original['fit_rows']['Feminine/bob/ears/jersey/default']
    ear_headgear=translate_component(ear_row['headgear'],-.020,catalogue)
    ear_sprout=translate_component(ear_row['sprout'],-.020,catalogue)
    fits={};report={}
    for hat in HATS:
        bpy.ops.wm.open_mainfile(filepath=str(APPROVED/'Ravedio334-waves.blend'))
        obj=next(o for o in bpy.context.scene.objects if o.type=='MESH' and o.get('component269')=='hair')
        points=np.array([v.co[:] for v in obj.data.vertices])@TO_BLENDER.T
        normals=np.array([v.normal[:] for v in obj.data.vertices])@TO_BLENDER.T
        moved=points
        if hat!='none':
            row=catalogue['fit_rows'][f'Feminine/bob/{hat}/jersey/default']
            path=(OUTPUT/catalogue['components'][ear_headgear]['file']) if hat=='ears' else BASE/catalogue['components'][row['headgear']]['file']
            field=contact_field(path)
            np.save(OUTPUT/f'contact-{hat}.npy',field)
            warp=fit_warp(field,hat)
            moved=warp(points)
            shading=warp_normals(warp,points,normals)
            obj.data.vertices.foreach_set('co',(moved@TO_BLENDER).astype(np.float32).ravel())
            obj.data.update()
            obj.data.normals_split_custom_set_from_vertices((shading@TO_BLENDER).tolist())
        fits[hat]={}
        for finish in ('default','ombre'):
            if finish=='ombre':recolor_ombre(obj)
            pending=OUTPUT/f'{hat}-{finish}.glb'
            if hat=='none' and finish=='default':
                shutil.copyfile(APPROVED/'waves.glb',pending)
            else:export(obj,pending)
            digest=sha(pending);destination=assets/f'{digest}.glb'
            if destination.exists():pending.unlink()
            else:pending.replace(destination)
            catalogue['components'][digest]={'file':'assets/'+destination.name,'bytes':destination.stat().st_size}
            fits[hat][finish]=digest
        delta=np.linalg.norm(moved-points,axis=1)
        report[hat]={'vertices':len(points),'max_displacement':float(delta.max()),
                     'changed_fraction':float(np.mean(delta>1e-5))}
        print('Exported',hat,report[hat],flush=True)
    count=0
    context={}
    for key,row in catalogue['fit_rows'].items():
        if not key.startswith('Feminine/bob/'):continue
        _,_,hat,top,finish=key.split('/')
        row['hair']=fits[hat][finish]
        row['hairLengths']=None
        if hat=='ears':
            row['headgear']=ear_headgear
            row['sprout']=ear_sprout
        context.setdefault(hat,{}).setdefault(top,{})[finish]={
            'hair':'assets/'+fits[hat][finish]+'.glb',
            'headgear':catalogue['components'][row['headgear']]['file'] if row['headgear'] else None,
            'sprout':catalogue['components'][row['sprout']]['file']}
        count+=1
    assert count==128
    for key,row in original['fit_rows'].items():
        if not key.startswith('Feminine/bob/'):assert row==catalogue['fit_rows'][key]
    for entry in catalogue['components'].values():
        destination=OUTPUT/entry['file']
        if destination.exists():continue
        source=BASE/entry['file']
        try:os.link(source,destination)
        except OSError:shutil.copyfile(source,destination)
    for name in ('palette','studio','finish'):
        shutil.copyfile(BASE/catalogue[name],OUTPUT/catalogue[name])
    dyes=catalogue['shared_jersey_dyes_dir']
    shutil.copytree(BASE/dyes,OUTPUT/dyes,dirs_exist_ok=True)
    catalogue['revision']=335
    catalogue['options']['builds']['Feminine']['hair']['bob']='Wavy bob'
    overlay=load(BASE/'overlay.json')
    overlay['hairLabels']={'Feminine':{'bob':{'label':'Wavy bob','note':'Approved curtain fringe and a wavy, tucked bob. Authored headwear fits.'}}}
    save(OUTPUT/'catalogue.json',catalogue);save(OUTPUT/'overlay.json',overlay)
    save(OUTPUT/'bob-fits.json',{'revision':335,'style':'bob','build':'Feminine','fits':context})
    save(OUTPUT/'receipt.json',{'revision':335,'base_revision':330,'approved_revision':334,
        'approved_source_sha256':approval['source_sha256'],'approved_glb_sha256':approval['sha256'],
        'fit_rows':count,'fits':fits,'deformations':report})
    print('Integrated 128 bob rows; other styles and independent roles retained.',flush=True)


if __name__=='__main__':main()
