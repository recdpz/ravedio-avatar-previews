"""Fresh-GLB assembly review, concealed-hair fits and packed source fixtures."""
import sys
from pathlib import Path
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue235')
import common235 as c
c.P=Path(__file__).parent
from common235 import *
OLD=R/'238';D=R/'239';cat=json.loads((OLD/'catalogue238.json').read_text())
ANGLES=['front','threequarter','profile','rightprofile','rear','top','underside']

def setup(build,top):
    bpy.ops.wm.open_mainfile(filepath=str(P/'sources'/f'{build}-{top}-pashmina239.blend'))
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

def hair_review():
    current=json.loads((D/'catalogue239.json').read_text());records={}
    for build in ['Feminine','Masculine']:
        top='open' if build=='Feminine' else 'tank'
        for style in current['builds'][build]['hair']:
            key=build+'-'+style;hair=current['fits'][key]['pashmina']['hair'];headgear=current['pashminaTops'][build][top]
            s,paths=assemble(build,top,hair,headgear,current,D)
            render(s,key+'-pashmina239',['profile','rear'],'review2',192,True)
            records[key]=dict(path=hair,geometry='Exact retained236 covered-hair export',front_locks_preserved=True,uncovered_hair_unchanged=True)
            u.dump(P/'hair239.json',records)
    print('HAIR239 sixteen retained covered hairstyles reviewed',flush=True)

def assemblies():
    current=json.loads((D/'catalogue239.json').read_text());fits=json.loads((P/'fits239.json').read_text());records={}
    for build,tops in fits.items():
        style='ponytail' if build=='Feminine' else 'taper';default='open' if build=='Feminine' else 'tank'
        for top,item in tops.items():
            hair=current['fits'][build+'-'+style]['pashmina']['hair'];headgear=current['pashminaTops'][build][top]
            s,paths=assemble(build,top,hair,headgear,current,D)
            frozen={k:v for k,v in u.object_geometry(s).items() if s.objects[k].get('component159')!='headgear'}
            render(s,build+'-'+top+'-export239',ANGLES,'review2',256,True)
            assert all(u.object_geometry(s).get(k)==v for k,v in frozen.items())
            records[build+'-'+top]=dict(final_glbs_reopened=True,angles=ANGLES,protected_exact=True,inputs=paths)
            if top==default:
                u.camera(s,'front',512,True);u.bake(s);bpy.ops.file.pack_all();path=P/'sources'/f'{build}-pashmina-assembly239.blend'
                bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene
                settings=u.requirements(s);render(s,build+'-pashmina239',ANGLES,'fixtures',512,True);portraits={}
                for size in [120,512]:
                    render(s,build+'-pashmina239-portrait'+str(size),['front'],'fixtures',size,False);portraits[str(size)]=u.settings(s)
                assert portraits['120']['camera']['matrix_world']==portraits['512']['camera']['matrix_world']
                assert portraits['120']['camera']['ortho_scale']==portraits['512']['camera']['ortho_scale']
                rec=dict(source=str(path),packed=True,body_reference=settings,portrait_settings=portraits,top=top,hair=style,skin_index=1,headgear='pashmina',shared_coordinates=True)
                fixture_path=P/'fixtures239.json';fixtures=json.loads(fixture_path.read_text()) if fixture_path.exists() else {};fixtures[build]=rec;u.dump(fixture_path,fixtures)
                # Readability references change only the skin tone, with fixed
                # geometry, studio, camera and framing. Restore before leaving.
                for tone in range(4):
                    u.tone(s,tone);render(s,build+'-skin'+str(tone)+'-portrait239',['front'],'review2',128,False)
                u.tone(s,1)
                # Actual final-export close-ups; replace only headgear for
                # exactly matched238 comparisons, keeping every other mesh.
                previous=json.loads((OLD/'catalogue238.json').read_text())
                for revision in [239,238]:
                    if revision==238:
                        for ob in list(s.objects):
                            if ob.get('component159')=='headgear':u.delete(ob)
                        imported((OLD/previous['pashminaTops'][build][top]).resolve(),'headgear')
                    for angle in ['front','threequarter','profile','rightprofile','underside']:
                        u.camera(s,angle,640,True);s.camera.data.ortho_scale=.86;s.camera.location.z+=.20;s.cycles.samples=32
                        floor=s.objects.get('Studio floor');old_hidden=floor.hide_render if floor else False
                        try:
                            if floor and angle=='underside':floor.hide_render=True
                            s.render.filepath=str(P/'review2'/f'{build}-neck{revision}-{angle}.png');bpy.ops.render.render(write_still=True)
                        finally:
                            if floor:floor.hide_render=old_hidden
            u.dump(P/'proof239.json',records)
    print('EXPORT239 fourteen top fits, seven angles; two packed/reopened assemblies',flush=True)

if __name__=='__main__':
    if '--hair-review' in sys.argv:hair_review()
    else:assemblies()
