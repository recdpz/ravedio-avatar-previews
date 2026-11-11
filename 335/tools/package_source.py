"""Package both the complete source catalogue and an exact-base bob update."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import hashlib,json,shutil
from zipfile import ZipFile,ZIP_DEFLATED

ROOT=Path(__file__).resolve().parents[2]
OUT=Path('D:/Ravedio-Avatar-Work/native335')
BASE=Path('D:/Ravedio-Avatar-Work/native330')
APPROVED=Path('D:/Ravedio-Avatar-Work/native334')

def load(path):return json.loads(path.read_bytes())
def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(path,value):path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf8')


def make_archive(name,files,manifest_name,metadata):
    delivery=OUT/'delivery';delivery.mkdir(exist_ok=True)
    records={file:{'sha256':sha(OUT/file),'bytes':(OUT/file).stat().st_size} for file in sorted(set(files))}
    manifest={**metadata,'files':records}
    save(OUT/manifest_name,manifest)
    path=delivery/name
    with ZipFile(path,'w',ZIP_DEFLATED,compresslevel=3) as archive:
        for file in records:archive.write(OUT/file,file)
        archive.write(OUT/manifest_name,manifest_name)
    with ZipFile(path) as archive:
        assert archive.testzip() is None
        assert set(archive.namelist())==set(records)|{manifest_name}
        for file,record in records.items():
            with archive.open(file) as f:assert hashlib.file_digest(f,'sha256').hexdigest()==record['sha256']
    path.with_suffix('.zip.sha256').write_text(sha(path)+'  '+path.name+'\n',encoding='ascii')
    print('Verified archive',path.name,path.stat().st_size,flush=True)
    return {'file':'delivery/'+path.name,'bytes':path.stat().st_size,'sha256':sha(path)}


def main():
    catalogue=load(OUT/'catalogue.json');base=load(BASE/'catalogue.json')
    sources=OUT/'sources';sources.mkdir(exist_ok=True)
    shutil.copyfile(APPROVED/'Ravedio334-waves.blend',sources/'approved-B334.blend')
    shutil.copyfile(ROOT/'approvals/bob334-waves.json',OUT/'approval.json')
    shutil.copyfile(ROOT/'335/README.md',OUT/'README.md')
    scripts=OUT/'tools';scripts.mkdir(exist_ok=True)
    shutil.copyfile(ROOT/'335/tools/render_review.py',scripts/'render_review.py')
    common=['catalogue.json','overlay.json','bob-fits.json','receipt.json','fit-review.json',
            'palette.json','studio.json','finish.json','approval.json','README.md',
            'Ravedio335-Wavy-bob.blend','sources/approved-B334.blend','tools/render_review.py',
            'angles.jpg','headwear.jpg','ombre.jpg','colors.jpg']
    common += ['browser-review.json','gallery-review.json','visual-review.json']
    for file in common:assert (OUT/file).is_file(),file
    all_assets=[entry['file'] for entry in catalogue['components'].values()]
    dyes=[p.relative_to(OUT).as_posix() for p in (OUT/catalogue['shared_jersey_dyes_dir']).rglob('*') if p.is_file()]
    full=make_archive('Ravedio335-full-source-catalogue.zip',common+all_assets+dyes,
        'manifest335.json',{'schema':1,'revision':335,'kind':'complete-source-catalogue',
        'component_count':len(all_assets),'approved_bob_revision':334,'profile_wire_change':False})
    updated=[entry['file'] for digest,entry in catalogue['components'].items() if digest not in base['components']]
    delta=make_archive('Ravedio335-wavy-bob-source.zip',common+updated,
        'delta-manifest335.json',{'schema':1,'revision':335,'kind':'source-delta',
        'base_revision':330,'base_catalogue_sha256':sha(BASE/'catalogue.json'),
        'apply':'Overlay these files onto an extracted exact revision 330 source catalogue; preserve the base assets and jersey-dyes directory.'})
    save(OUT/'delivery.json',{'revision':335,'full':full,'delta':delta})


if __name__=='__main__':main()
