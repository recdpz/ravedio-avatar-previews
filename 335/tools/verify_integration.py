"""Verify the bob replacement, palette encoding and per-outfit contact fits."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parent))
from integrate_bob import BASE,OUTPUT,APPROVED,HATS,CENTER,load,sha,save,surface
from drape import accessor,node_transforms,read_glb


def geometry(path):
    doc,data=read_glb(path)
    points=[]
    for node,rotation,offset in node_transforms(doc):
        if 'mesh' not in node:continue
        for primitive in doc['meshes'][node['mesh']]['primitives']:
            p=accessor(doc,data,primitive['attributes']['POSITION'],3)
            points.append(p@rotation.T+offset)
    return doc,data,np.concatenate(points)


def main():
    before=load(BASE/'catalogue.json');after=load(OUTPUT/'catalogue.json')
    receipt=load(OUTPUT/'receipt.json');context=load(OUTPUT/'bob-fits.json')
    assert after['revision']==335
    for key in ('coordinates','independent_roles','groom_mouths','fit_selector'):
        assert before[key]==after[key],key
    for key,row in before['fit_rows'].items():
        if not key.startswith('Feminine/bob/'):
            assert row==after['fit_rows'][key],key
    for role in ('palette','studio','finish'):
        assert sha(BASE/before[role])==sha(OUTPUT/after[role])
    bare=receipt['fits']['none']['default']
    assert bare==receipt['approved_glb_sha256']==sha(APPROVED/'waves.glb')
    assert sha(APPROVED/'Ravedio334-waves.blend')==receipt['approved_source_sha256']
    records={};point_cache={}
    new=set()
    for hat in HATS:
        for finish in ('default','ombre'):
            digest=receipt['fits'][hat][finish];new.add(digest)
            path=OUTPUT/after['components'][digest]['file']
            assert sha(path)==digest
            doc,data,points=geometry(path)
            assert np.isfinite(points).all()
            assert not any(ext in doc.get('extensionsUsed',[]) for ext in ('KHR_draco_mesh_compression','EXT_meshopt_compression','KHR_mesh_quantization'))
            assert len(doc['materials'])==1
            material=doc['materials'][0]
            assert 'normalTexture' in material
            assert 'metallicRoughnessTexture' in material['pbrMetallicRoughness']
            assert all('bufferView' in image for image in doc['images'])
            primitives=[p for mesh in doc['meshes'] for p in mesh['primitives']]
            for p in primitives:
                uv=accessor(doc,data,p['attributes']['TEXCOORD_0'],2)
                normal=accessor(doc,data,p['attributes']['NORMAL'],3)
                assert np.isfinite(uv).all() and np.isfinite(normal).all()
                assert np.max(np.abs(np.linalg.norm(normal,axis=1)-1))<.002
                assert ('COLOR_0' in p['attributes'])==(finish=='ombre')
                if finish=='ombre':
                    count=doc['accessors'][p['attributes']['COLOR_0']]['type']
                    colors=accessor(doc,data,p['attributes']['COLOR_0'],4 if count=='VEC4' else 3)
                    assert np.isfinite(colors).all() and colors.min()>=0 and colors.max()<=1
            records[hat+'/'+finish]={'vertices':len(points),'bytes':path.stat().st_size,
                'triangles':sum(doc['accessors'][p['indices']]['count']//3 for p in primitives),
                'materials':len(doc['materials']),'embedded_textures':len(doc['images'])}
            point_cache[hat,finish]=points
        a,b=(point_cache[hat,f] for f in ('default','ombre'))
        assert a.shape==b.shape,(hat,a.shape,b.shape)
        assert np.max(np.abs(a-b))<1e-6,'Ombre changed geometry: '+hat
    count=0;contact={};trees={};garments={};hair_trees={};clothing={}
    for key,row in after['fit_rows'].items():
        if not key.startswith('Feminine/bob/'):continue
        _,_,hat,top,finish=key.split('/')
        fit=context['fits'][hat][top][finish]
        for role in ('hair','headgear','sprout'):
            expected=after['components'][row[role]]['file'] if row[role] else None
            assert fit[role]==expected,(key,role)
        assert row['hairLengths'] is None
        for role in ('top',):assert row[role]==before['fit_rows'][key][role]
        if hat!='ears':assert row['headgear']==before['fit_rows'][key]['headgear']
        if hat!='none' and finish=='default':
            digest=row['headgear']
            if digest not in trees:trees[digest]=surface(OUTPUT/after['components'][digest]['file'])
            cache_key=hat+'/'+digest
            if cache_key not in contact:
                points=point_cache[hat,finish]
                points=points[np.linalg.norm(points-CENTER,axis=1)>.385][::103]
                depths=[]
                for p in points:
                    relative=p-CENTER;r=np.linalg.norm(relative)
                    _,_,_,distance=trees[digest].ray_cast(CENTER,relative/r,.70)
                    if distance is not None and distance>.385:depths.append(r-distance)
                values=np.array(depths)
                contact[cache_key]={'sampled_contact_rays':len(values),
                    'max_behind_cloth':float(values.max()) if len(values) else 0,
                    'rays_more_than_10mm_through_cloth':int(np.sum(values>.010))}
        if hat in ('none','pashmina') and finish=='default':
            hair=row['hair'];top_digest=row['top']
            if hair not in hair_trees:hair_trees[hair]=surface(OUTPUT/after['components'][hair]['file'])
            if top_digest not in garments:garments[top_digest]=surface(OUTPUT/after['components'][top_digest]['file'])
            clothing[hat+'/'+top]=len(hair_trees[hair].overlap(garments[top_digest]))
        count+=1
    assert count==128
    assert all(count==0 for count in clothing.values()),clothing
    for digest,entry in after['components'].items():assert (OUTPUT/entry['file']).is_file(),digest
    report={'rows':count,'uncovered_source_exact':True,'other_styles_unchanged':True,
        'palette_unchanged':True,'shared_coordinates_preserved':True,
        'ordinary_glbs':records,'contact_samples':contact,'hair_top_triangle_contacts':clothing}
    save(OUTPUT/'fit-review.json',report)
    print('Verified 128 bob rows, 16 ordinary hair exports, palette, UVs, ombre geometry and catalogue isolation.')
    for key,value in contact.items():
        assert value['rays_more_than_10mm_through_cloth']==0,('Review contact',key,value)
    print('Hair/top contacts',clothing)


if __name__=='__main__':main()
