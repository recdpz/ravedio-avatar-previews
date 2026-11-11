"""Build named-settings/schema/mapping evidence without creating a wire format."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib,shutil,subprocess
from zipfile import ZipFile,ZIP_DEFLATED

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import resolve_avatar as resolver
import legacy_profile3 as legacy

REPO=HERE.parents[1]
ART=Path('D:/Ravedio-Avatar-Work/native335')
OUT=Path('D:/Ravedio-Avatar-Work/handoff335/package')
WORKSPACE=Path('//wsl.localhost/Ubuntu/home/ronaldcasasola/mesh')

def load(path):return json.loads(path.read_bytes())
def save(path,value):path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf8')
def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def generate():
    OUT.mkdir(parents=True,exist_ok=True)
    c=load(ART/'catalogue.json')
    for name in ('README.md','legacy_profile3.py','resolve_avatar.py','material_recipes.mjs','material-rules.json','test_material_recipes.mjs'):
        shutil.copyfile(HERE/name,OUT/name)
    shutil.copyfile(REPO/'335/viewer.js',OUT/'viewer335.js')
    shutil.copyfile(REPO/'335/tools/render_review.py',OUT/'render_bob335.py')
    for name in ('catalogue.json','palette.json','studio.json','finish.json','bob-fits.json','fit-review.json','visual-review.json'):
        shutil.copyfile(ART/name,OUT/name)
    prior=Path('E:/Ravedio-Avatar/refinement169/profile-handoff.md')
    shutil.copyfile(prior,OUT/'PROPOSED-six-byte-handoff169.md')
    snapshots=OUT/'read-only-source-snapshots'
    mobile_commit='b7457bcd2ca98f8e2b907d6d4de7aa1f267c6cf4'
    firmware_commit='85f545b79198defce028a92873a3ebc2360ec5b4'
    evidence={}
    files={
        'avatar_spec.dart':'mobile/lib/models/avatar_spec.dart',
        'profile_update.dart':'mobile/lib/models/profile_update.dart',
        'RavedioUserAvatar.swift':'mobile/apps/ios/Modules/Sources/RavedioDesignSystem/RavedioUserAvatar.swift',
        'RavedioUserAvatar.kt':'mobile/apps/android/core/designsystem/src/main/java/com/ravedio/designsystem/RavedioUserAvatar.kt',
        'RavedioCore.h':'firmware/src/RavedioCore.h',
    }
    for name,relative in files.items():
        product,inside=relative.split('/',1)
        commit=mobile_commit if product=='mobile' else firmware_commit
        data=subprocess.check_output(['git','-c','safe.directory=*','-C',str(WORKSPACE/product),'show',commit+':'+inside])
        evidence[relative]={'sha256':hashlib.sha256(data).hexdigest(),'repository':'ravedio/'+product,
            'commit':commit,'path':inside,'source_url':f'https://github.com/ravedio/{product}/blob/{commit}/{inside}',
            'source_contents_in_public_art_handoff':False}
        stale=snapshots/name
        if stale.is_file():stale.unlink()
    if snapshots.is_dir() and not any(snapshots.iterdir()):snapshots.rmdir()
    fields=[('type',0,7,6),('skin',0,5,4),('hair',0,3,1),('hairColor-high',0,0,0),
        ('hairColor-low',1,7,6),('headgear',1,5,3),('gearColor',1,2,0),('glasses',2,7,5),
        ('build',2,4,4),('extra',2,3,2),('face',2,1,0)]
    proposal=[['type',0,7,6],['headwear',0,5,3],['headwearColor',0,2,0],
        ['build',1,7,7],['hair',1,6,3],['hairColor',1,2,0],
        ['skin',2,7,6],['top',2,5,3],['topColor',2,2,0],
        ['eyes',3,7,6],['faceDetails',3,5,3],['extra',3,2,0],
        ['glasses',4,7,5],['frameColor',4,4,3],['ageBracket',4,2,0],
        ['bottom',5,7,6],['bottomColor',5,5,3],['reserved',5,2,0]]
    profile={'current':{'id':'legacy-typed-profile3','status':'implemented-legacy-sprite-format',
        'wireBytes':3,'inBandVersionField':None,'localCloudReservedByte':{'index':3,'requiredValue':0,'transmitted':False},
        'absence':'An omitted update is distinct from an explicitly present zero clear; it is not encoded as a one-byte clear.',
        'fields':[{'name':name,'byte':byte,'msb':hi,'lsb':lo} for name,byte,hi,lo in fields],
        'hairColorIndexFormula':'((byte0 & 1) << 2) | (byte1 >> 6)',
        'types':{'0':'none; canonical clear is 00 00 00','1':'avatar; all payload bit values used',
                 '2':'flag reserved for future presentation; current native initials fallback',
                 '3':'social mode reserved for future presentation; current native initials fallback'},
        'unusedAvatarPayloadBits':0,'reservedAvatarEnumValues':[],
        'tables':legacy.TABLES,'contextualHairLabels':legacy.HAIR_LABELS,'contextualFaceLabels':legacy.FACE_LABELS,
        'defaults':legacy.DEFAULT,'defaultBytes':legacy.encode({}),
        'zeroAvatarPayload':'40 00 00 is a valid avatar, not clear',
        'catalogue335Mapping':None,'sourceEvidence':evidence},
        'sixByteProposal':{'status':'PROPOSED-NOT-FINALIZED-NOT-IMPLEMENTED','avatarBytes':6,
            'source':'PROPOSED-six-byte-handoff169.md','sourceSha256':sha(prior),
            'fields':[{'name':n,'byte':b,'msb':hi,'lsb':lo} for n,b,hi,lo in proposal],
            'reservedBits':'byte5 bits2..0 must be zero if this proposal is later adopted',
            'optionValueAssignments':'NOT FROZEN for current artwork; no approved full enum map',
            'inBandVersionField':None,'typesAndLengths':{'0':'proposed one-byte clear 00','1':'proposed six-byte avatar','2':'proposed two-byte country flag; country IDs unresolved','3':'reserved, payload and length unresolved'},
            'structuralVectorsOnly':['40 00 00 00 00 00','7F FF FF FF FF F8'],
            'doNot':'Do not enable this in a native/firmware codec or infer length heuristically.'},
        'fiveByteExplorer':{'status':'DESIGN-EXPLORER-NOT-WIRE-AUTHORITY','sourceSha256':sha(Path('C:/Users/Ronnie/.codex/visualizations/2026/09/13/01a09d1a-941a-7c51-823a-430e315cd3fb/profile-bit-budget.html')),
            'note':'Presets and saved slider state do not establish a reviewed layout or enum contract.'}}
    save(OUT/'profile-formats.json',profile)
    options={**c['options'],'skin':[{'id':i,'label':label} for i,label in enumerate(('Fair','Light warm','Tan','Deep'))],
        'nose':{'none':'No nose'},'mouth':{'line':'Regular smile'},'defaults':{b:resolver.defaults(b) for b in c['options']['builds']},
        'numericWireIds':'UNASSIGNED for this 3D artwork; IDs below are named asset selectors only'}
    save(OUT/'catalogue-options.json',options);save(OUT/'defaults.json',options['defaults'])
    props={'schemaVersion':{'type':'integer','const':1},'catalogueRevision':{'type':'integer','const':335},
        'build':{'type':'string','enum':list(c['options']['builds'])},'skin':{'type':'integer','enum':[0,1,2,3]},
        'nose':{'const':'none'},'mouth':{'const':'line'}}
    for field,role in resolver.COLOR_FIELDS.items():props[field]={'type':'string','enum':[row[0] for row in c['options']['colors'][role]]}
    for field,key in (('headwear','headwear'),('glasses','glasses'),('detail','details')):props[field]={'type':'string','enum':list(c['options'][key])}
    conditionals=[]
    for build,table in c['options']['builds'].items():
        per={field:{'type':'string','enum':list(table[key])} for field,key in (('hair','hair'),('eyes','eyes'),('groom','grooms'),('top','tops'),('bottom','bottoms'))}
        for field in per:props.setdefault(field,{'type':'string'})
        conditionals.append({'if':{'properties':{'build':{'const':build}},'required':['build']},'then':{'properties':per}})
    schema={'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'urn:ravedio:avatar-settings:1',
        'title':'Catalogue 335 named rendering settings; not a radio profile',
        'type':'object','additionalProperties':False,'required':sorted(resolver.FIELDS),'properties':props,'allOf':conditionals}
    save(OUT/'avatar-settings.schema.json',schema)
    save(OUT/'complete-mapping.json',{'revision':335,'wireIdsAssigned':False,'fitSelector':c['fit_selector'],
        'fitRows':c['fit_rows'],'independentRoles':c['independent_roles'],'groomMouths':c['groom_mouths'],
        'components':c['components'],'colorAliases':c['options']['color_aliases'],
        'restrictions':{'combination':'Fit row must exist; never substitute a generic hair/hat warp.',
            'lashes':'Automatic per face/build','nose':'none','mouth':'line','unknownNamedValues':'reject',
            'unknownFutureWireValues':'requires separate protocol decision; not assigned here'}})
    old=[]
    for title,data in (('canonical-clear',[0,0,0]),('constructor-default',[0x54,5,0]),
        ('legacy-feminine-bob-cap-rect-gems',[0x42,0x49,0x7d]),('zero-avatar-payload',[0x40,0,0]),
        ('maximum-avatar-payload',[0x7f,0xff,0xff]),('reserved-flag',[0x80,0,0]),('reserved-social',[0xc0,0,0])):
        old.append({'id':title,'hex':' '.join(f'{x:02X}' for x in data),'decoded':legacy.decode(data)})
    save(OUT/'legacy-examples.json',old)
    named=[]
    cases=[('approved-bob','Feminine',{}),('bob-cap-ombre','Feminine',{'headwear':'cap','hairColor':'ombre'}),
        ('bob-pashmina-buttonup','Feminine',{'headwear':'pashmina','top':'open'}),
        ('bob-bandana-reading-hot','Feminine',{'headwear':'headband','hairColor':'pink','glasses':'reading','lensTint':'clear','frameColor':'gold','detail':'hot','topColor':'blue'}),
        ('ponytail-beanie-sprout','Feminine',{'hair':'ponytail','headwear':'beanie','hairColor':'ombre','detail':'sprout'}),
        ('space-buns-cap','Feminine',{'hair':'space-buns','headwear':'cap'}),
        ('masculine-flow-cap','Masculine',{'hair':'flow','headwear':'cap','top':'sweatshirt','bottom':'pants','groom':'short','glasses':'wayfarer','detail':'hot','hairColor':'black'}),
        ('masculine-shirtless','Masculine',{'top':'shirtless','groom':'none'})]
    for id,build,changes in cases:
        s={**resolver.defaults(build),**changes}
        named.append({'id':id,'profileBytes':None,'input':s,'expected':resolver.resolve(s,c,ART)})
    save(OUT/'named-examples.json',named)
    provenance={'artworkCommit':subprocess.check_output(['git','rev-parse','f7a01d2'],cwd=REPO,text=True).strip(),
        'artworkRevision':335,'catalogueSha256':sha(ART/'catalogue.json'),
        'approval':load(REPO/'approvals/bob334-waves.json'),'integration':load(REPO/'335/integration-lock.json'),
        'mobileSourceCommit':mobile_commit,'firmwareSourceCommit':firmware_commit,
        'sourceEvidence':evidence,'archives':load(ART/'delivery.json'),
        'newUnpublishedArtwork':'335 source work is now pushed; no artwork after 335 has been substituted into this handoff.',
        'protocolChanges':False}
    save(OUT/'artwork-provenance.json',provenance)
    release='https://github.com/recdpz/ravedio-avatar-previews/releases/tag/avatar-art335-source'
    attachments={}
    for entry in load(ART/'delivery.json').values():
        if not isinstance(entry,dict):continue
        name=Path(entry['file']).name
        attachments[name]={**entry,'url':'https://github.com/recdpz/ravedio-avatar-previews/releases/download/avatar-art335-source/'+name}
    save(OUT/'release.json',{'release':release,'artworkCommit':provenance['artworkCommit'],'assets':attachments,
        'handoffName':'Ravedio335-mobile-selection-handoff.zip','handoffChecksumName':'Ravedio335-mobile-selection-handoff.zip.sha256'})
    print('Generated schema, all 1792 fit bindings, defaults, legacy vectors and eight named examples.')


def package():
    archive=OUT.parent/'Ravedio335-mobile-selection-handoff.zip'
    files={p.relative_to(OUT).as_posix():{'sha256':sha(p),'bytes':p.stat().st_size} for p in OUT.rglob('*') if p.is_file() and p.name!='manifest.json'}
    save(OUT/'manifest.json',{'schema':1,'artworkRevision':335,'wireFormatChange':False,'files':files})
    with ZipFile(archive,'w',ZIP_DEFLATED,compresslevel=6) as z:
        for p in OUT.rglob('*'):
            if p.is_file():z.write(p,p.relative_to(OUT).as_posix())
    with ZipFile(archive) as z:
        assert z.testzip() is None
        for name,entry in files.items():
            with z.open(name) as f:assert hashlib.file_digest(f,'sha256').hexdigest()==entry['sha256']
    archive.with_suffix('.zip.sha256').write_text(sha(archive)+'  '+archive.name+'\n',encoding='ascii')
    print('Verified handoff archive',archive.stat().st_size,sha(archive))


if __name__=='__main__':
    if '--package-only' not in sys.argv:generate()
    if '--package' in sys.argv or '--package-only' in sys.argv:package()
