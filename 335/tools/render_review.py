"""Render every bob headwear, palette and camera combination from the catalogue."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json
import math
import argparse

import bpy
import numpy as np
from mathutils import Vector

OUTPUT=Path('D:/Ravedio-Avatar-Work/native335')
SOURCE=Path('D:/Ravedio-Avatar-Work/native334/Ravedio334-waves.blend')
HATS=('none','cap','beanie','bucket','cowboy','ears','headband','pashmina')
COLORS=('default','black','auburn','blonde','platinum','pink','purple','ombre')
ANGLES={'front':(0,0),'threequarter':(-33,0),'profile':(-90,0),'rightprofile':(90,0),
        'rear':(180,0),'rearquarter':(-144,0),'above':(-33,36),'underneath':(-33,-24)}


def load(path):return json.loads(path.read_bytes())
def color_linear(value):
    rgb=np.array([int(value[i:i+2],16) for i in (1,3,5)])/255
    return np.where(rgb<=.04045,rgb/12.92,((rgb+.055)/1.055)**2.4)


def select(catalogue,row):
    _,hair,hat,top,bottom,eye,_,glasses,lens,extra,skin,finish=row
    fit=catalogue['fit_rows'][f'Feminine/{hair}/{hat}/{top}/{finish}']
    independent=catalogue['independent_roles']['Feminine']
    face=independent['faces'][eye]
    parts={role:fit[role] for role in ('hair','hairLengths','top','headgear')}
    parts.update(base=independent['bases'][bottom]['clothed'],bottom=independent['bottoms'][bottom],
                 eyes=face['eyes'],lashes=face['lashes'],mouth=face['mouth'])
    if extra=='sprout':parts['extra']=fit['sprout']
    elif extra=='hot':parts['extra']=independent['hot']
    if glasses!='none':
        fitted=independent['glasses'][glasses]
        parts.update(glasses=fitted['glasses'],lenses=fitted['lenses'][lens])
    return {'parts':{role:digest for role,digest in parts.items() if digest}}


def change_parts(scene,source,target):
    for role in sorted(source.keys()|target.keys()):
        if source.get(role)==target.get(role):continue
        for obj in list(scene.objects):
            if obj.type=='MESH' and obj.get('component269')==role:
                bpy.data.objects.remove(obj,do_unlink=True)
        if role in target:
            before=set(scene.objects)
            bpy.ops.import_scene.gltf(filepath=str(target[role]),import_shading='NORMALS')
            imported=[o for o in set(scene.objects)-before if o.type=='MESH']
            assert imported,(role,target[role])
            for obj in imported:obj['component269']=role


def setup(catalogue,hat,top='jersey',skin=2,extra='none',glasses='none',lens='clear'):
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    scene=bpy.context.scene
    row=select(catalogue,('F','bob',hat,top,'pants','bean','none',glasses,lens,extra,skin,'default'))
    old={o.get('component269'):'packed' for o in scene.objects if o.type=='MESH' and o.get('component269')}
    target={role:str(OUTPUT/catalogue['components'][digest]['file']) for role,digest in row['parts'].items()}
    change_parts(scene,old,target)
    palette=load(OUTPUT/'palette.json')
    for obj in scene.objects:
        if obj.type!='MESH':continue
        for material in obj.data.materials:
            kind=next((k for prefix,k in (('Skin','skin'),('Face / ink209','ink'),('Face / lip209','lip'))
                       if material.name.startswith(prefix)),None)
            if kind:
                shader=next(n for n in material.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
                shader.inputs['Base Color'].default_value=(*palette[kind][skin],1)
        if obj.get('component269')=='top':obj.visible_glossy=False
    prefs=bpy.context.preferences.addons['cycles'].preferences
    scene.cycles.device='CPU'
    for backend in ('CUDA','METAL','OPTIX','HIP','ONEAPI'):
        try:
            prefs.compute_device_type=backend;prefs.get_devices()
        except (TypeError,RuntimeError):
            continue
        adapters=[d for d in prefs.devices if d.type==backend]
        if not adapters:continue
        for d in prefs.devices:d.use=d in adapters
        scene.cycles.device='GPU'
        break
    scene.render.film_transparent=True
    scene.render.use_compositing=False
    scene.render.image_settings.file_format='PNG'
    scene.render.image_settings.color_mode='RGBA'
    bpy.context.preferences.filepaths.save_version=0
    return scene,row


def camera(scene,angle):
    yaw,pitch=map(math.radians,ANGLES[angle])
    target=Vector((0,0,1.72))
    scene.camera.data.ortho_scale=1.52
    scene.camera.location=target+8*Vector((math.sin(yaw)*math.cos(pitch),-math.cos(yaw)*math.cos(pitch),math.sin(pitch)))
    scene.camera.rotation_euler=(target-scene.camera.location).to_track_quat('-Z','Y').to_euler()


def render(catalogue,hat,colors,angles,quick=False,top='jersey',skin=2,extra='none',prefix='',glasses='none',lens='clear'):
    scene,row=setup(catalogue,hat,top,skin,extra,glasses,lens)
    scene.render.resolution_x=scene.render.resolution_y=360 if quick else 480
    scene.render.resolution_percentage=100
    scene.cycles.samples=16 if quick else 24
    default={m:m.node_tree.nodes.get('Principled BSDF') for obj in scene.objects if obj.type=='MESH'
             and obj.get('component269')=='hair' for m in obj.data.materials}
    default={m:next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED') for m in default}
    for color in colors:
        if color=='ombre':
            digest=catalogue['fit_rows'][f'Feminine/bob/{hat}/{top}/ombre']['hair']
            target=OUTPUT/catalogue['components'][digest]['file']
            change_parts(scene,{'hair':'default'},{'hair':str(target)})
        elif color!='default':
            value=next(value for key,_,value in catalogue['options']['colors']['hair'] if key==color)
            rgb=color_linear(value)
            for material,shader in default.items():shader.inputs['Base Color'].default_value=(*rgb,1)
        for angle in angles:
            camera(scene,angle)
            if not quick and hat=='none' and color=='default' and angle=='threequarter' and not prefix:
                bpy.ops.file.pack_all()
                bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT/'Ravedio335-Wavy-bob.blend'))
            scene.render.filepath=str(OUTPUT/'review'/f'{prefix}{hat}-{color}-{angle}.png')
            bpy.ops.render.render(write_still=True)
        print('Reviewed',prefix,hat,color,flush=True)


def main():
    global OUTPUT,SOURCE
    parser=argparse.ArgumentParser()
    parser.add_argument('--quick',action='store_true')
    parser.add_argument('--hats',nargs='+',choices=HATS)
    parser.add_argument('--wardrobe',action='store_true')
    parser.add_argument('--accessories-only',action='store_true')
    parser.add_argument('--work',type=Path,default=OUTPUT)
    parser.add_argument('--source',type=Path)
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    OUTPUT=args.work
    if args.source:SOURCE=args.source
    elif (OUTPUT/'sources/approved-B334.blend').is_file():SOURCE=OUTPUT/'sources/approved-B334.blend'
    (OUTPUT/'review').mkdir(exist_ok=True)
    catalogue=load(OUTPUT/'catalogue.json')
    hats=args.hats or HATS
    for hat in (() if args.accessories_only else hats):
        colors=('default','ombre') if args.quick else COLORS
        angles=('threequarter','profile','rearquarter') if args.quick else tuple(ANGLES)
        render(catalogue,hat,colors,angles,args.quick)
    if args.wardrobe:
        for top in catalogue['options']['builds']['Feminine']['tops']:
            for hat in ('none','pashmina'):
                render(catalogue,hat,('default',),('front','profile','rear','underneath'),
                       top=top,prefix=top+'-')
        render(catalogue,'none',COLORS,('threequarter','rearquarter'),skin=3,prefix='deep-')
        render(catalogue,'none',('default',),('threequarter','profile','above'),extra='sprout',prefix='sprout-')
    if args.accessories_only:
        for glasses in catalogue['independent_roles']['Feminine']['glasses']:
            lens='clear' if glasses in ('reading','rectangular') else 'dark'
            render(catalogue,'none',('default',),('threequarter','profile','rightprofile'),
                   glasses=glasses,lens=lens,prefix='glasses-'+glasses+'-')
        render(catalogue,'ears',('default',),('threequarter','profile','above'),extra='sprout',prefix='sprout-')


if __name__=='__main__':main()
