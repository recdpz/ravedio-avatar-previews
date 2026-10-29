"""Fresh-GLB assembly review, concealed-hair fits and packed source fixtures."""
import sys
from pathlib import Path
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue235')
import common235 as c
c.P=Path(__file__).parent
from common235 import *
OLD=R/'235';D=R/'236';cat=json.loads((OLD/'catalogue235.json').read_text())
ANGLES=['front','threequarter','profile','rightprofile','rear','top','underside']

def setup(build,top):
    bpy.ops.wm.open_mainfile(filepath=str(P/'sources'/f'{build}-{top}-pashmina236.blend'))
    s=bpy.context.scene
    for o in list(s.objects):
        if o.type in ['MESH','CURVE'] and o.name!='Studio floor':u.delete(o)
    return s

def assemble(build,top,hair,headgear,table,root):
    s=setup(build,top);b=table['builds'][build]
    paths={'base':b.get('shirtlessBase') if top=='shirtless' else b['base'],'top':b['tops'][top]['path'],'bottom':b['bottoms']['skirt' if build=='Feminine' else 'shorts']['path'],'mouth':b['mouths']['line']['path'],'eyes':b['eyes']['original']['path'],'hair':hair,'headgear':headgear}
    if build=='Feminine':paths['eyelashes']=b['lashes']['original']['path']
    else:paths['groom']=b['grooms']['stubble']['path']
    for group,path in paths.items():
        if path:imported((root/path).resolve(),group)
    u.tone(s,1);return s,paths

def hair_fits():
    fits=json.loads((P/'fits236.json').read_text());records={}
    for build in ['Feminine','Masculine']:
        top='open' if build=='Feminine' else 'tank';headgear=(P/fits[build][top]['component']).as_posix()
        for style in cat['builds'][build]['hair']:
            key=build+'-'+style;src=cat['fits'][key]['pashmina']['hair']
            s,_=assemble(build,top,src,headgear,cat,OLD)
            # The export groups same-material panels into one addressable node;
            # inspect the node/material role, not the source mesh's old name.
            hood=next(o for o in s.objects if o.type=='MESH' and o.get('component159')=='headgear' and 'continuous woven pashmina' in o.name)
            cloth=tree([hood]);changed=0
            for o in s.objects:
                if o.type!='MESH' or o.get('component159')!='hair':continue
                inv=o.matrix_world.inverted()
                for v in o.data.vertices:
                    p=o.matrix_world@v.co
                    if not (1.40<p.z<1.64) or (p.y<-.30 and p.z<2.1):continue
                    direction=(p-a.C).normalized();hit,normal,_,distance=cloth.ray_cast(a.C,direction,1.5)
                    if hit is not None and (p-a.C).length>distance-.024:
                        v.co=inv@(a.C+direction*max(.1,distance-.024));changed+=1
            path=None
            if changed:
                u.bake(s);path='components/'+key+'-covered-hair236.glb';ex.export(s,P/path,'hair')
                remove(['hair']);imported(P/path,'hair')
            render(s,key+'-pashmina236',['profile','rear'],'review2',192,True)
            records[key]=dict(path=path,changed_concealed_vertices=changed,original=src,uncovered_hair_unchanged=True,front_locks_preserved=True)
            u.dump(P/'hair236.json',records)
    print('HAIR236 checked16 covered styles',flush=True)

def assemblies():
    current=json.loads((D/'catalogue236.json').read_text());fits=json.loads((P/'fits236.json').read_text());records={}
    for build,tops in fits.items():
        style='ponytail' if build=='Feminine' else 'taper';default='open' if build=='Feminine' else 'tank'
        for top,item in tops.items():
            hair=current['fits'][build+'-'+style]['pashmina']['hair'];headgear=current['pashminaTops'][build][top]
            s,paths=assemble(build,top,hair,headgear,current,D)
            frozen={k:v for k,v in u.object_geometry(s).items() if s.objects[k].get('component159')!='headgear'}
            render(s,build+'-'+top+'-export236',ANGLES,'review2',256,True)
            assert all(u.object_geometry(s).get(k)==v for k,v in frozen.items())
            records[build+'-'+top]=dict(final_glbs_reopened=True,angles=ANGLES,protected_exact=True,inputs=paths)
            if top==default:
                u.camera(s,'front',512,True);u.bake(s);bpy.ops.file.pack_all();path=P/'sources'/f'{build}-pashmina-assembly236.blend'
                bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene
                settings=u.requirements(s);render(s,build+'-pashmina236',ANGLES,'fixtures',512,True);portraits={}
                for size in [120,512]:
                    render(s,build+'-pashmina236-portrait'+str(size),['front'],'fixtures',size,False);portraits[str(size)]=u.settings(s)
                assert portraits['120']['camera']['matrix_world']==portraits['512']['camera']['matrix_world']
                assert portraits['120']['camera']['ortho_scale']==portraits['512']['camera']['ortho_scale']
                rec=dict(source=str(path),packed=True,body_reference=settings,portrait_settings=portraits,top=top,hair=style,skin_index=1,headgear='pashmina',shared_coordinates=True)
                fixture_path=P/'fixtures236.json';fixtures=json.loads(fixture_path.read_text()) if fixture_path.exists() else {};fixtures[build]=rec;u.dump(fixture_path,fixtures)
                # Readability references change only the skin tone, with fixed
                # geometry, studio, camera and framing. Restore before leaving.
                for tone in range(4):
                    u.tone(s,tone);render(s,build+'-skin'+str(tone)+'-portrait236',['front'],'review2',128,False)
                u.tone(s,1)
            u.dump(P/'proof236.json',records)
    print('EXPORT236 fourteen top fits, seven angles; two packed/reopened assemblies',flush=True)

if __name__=='__main__':
    if '--hair' in sys.argv:hair_fits()
    else:assemblies()
