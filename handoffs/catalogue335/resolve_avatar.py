"""Strict catalogue-335 asset selection from named settings, with no wire codec.

python resolve_avatar.py CATALOGUE_DIRECTORY SETTINGS.json
"""
from pathlib import Path
import hashlib,json,sys

COMMON={'schemaVersion':1,'catalogueRevision':335,'skin':2,'hairColor':'default','headwear':'none',
        'headgearColor':'default','eyes':'bean','nose':'none','mouth':'line','groom':'none',
        'glasses':'none','frameColor':'black','lensTint':'dark','detail':'none',
        'top':'jersey','topColor':'default','bottom':'pants','bottomColor':'default'}
FIELDS=set(COMMON)|{'build','hair'}
COLOR_FIELDS={'hairColor':'hair','headgearColor':'headgear','topColor':'top','bottomColor':'bottom',
              'frameColor':'frames','lensTint':'lenses'}


def defaults(build='Feminine'):
    if build not in ('Feminine','Masculine'):raise ValueError('Unknown build')
    value={**COMMON,'build':build,'hair':'bob'}
    if build=='Masculine':value.update(hair='taper',skin=3,eyes='original',groom='stubble',top='tank',bottom='shorts')
    return value


def load(root):return json.loads((Path(root)/'catalogue.json').read_bytes())
def linear(hex_color):
    srgb=[int(hex_color[i:i+2],16)/255 for i in (1,3,5)]
    return [x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in srgb]


def validate(s,c):
    if set(s)!=FIELDS:raise ValueError('Settings fields mismatch: '+str(sorted(set(s)^FIELDS)))
    if type(s['schemaVersion']) is not int or s['schemaVersion']!=1:raise ValueError('Unsupported settings schema')
    if type(s['catalogueRevision']) is not int or s['catalogueRevision']!=335 or c['revision']!=335:raise ValueError('Catalogue revision mismatch')
    if s['build'] not in c['options']['builds']:raise ValueError('Unknown build')
    options=c['options']['builds'][s['build']]
    for key,table in (('hair','hair'),('eyes','eyes'),('groom','grooms'),('top','tops'),('bottom','bottoms')):
        if s[key] not in options[table]:raise ValueError('Unsupported '+key)
    for key,table in (('headwear','headwear'),('glasses','glasses'),('detail','details')):
        if s[key] not in c['options'][table]:raise ValueError('Unsupported '+key)
    if type(s['skin']) is not int or not 0<=s['skin']<4:raise ValueError('Invalid skin')
    if s['nose']!='none' or s['mouth']!='line':raise ValueError('Only no nose and regular smile are supported')
    for field,role in COLOR_FIELDS.items():
        if s[field] not in {row[0] for row in c['options']['colors'][role]}:raise ValueError('Unsupported '+field)
    return s


def material_bindings(s,c,root):
    palettes=json.loads((Path(root)/c['palette']).read_bytes())
    aliases=c['options']['color_aliases'];build=s['build']
    def pigment(field,role):
        key=s[field]
        authored=aliases[role][build]
        if role!='hair':authored=authored[s[{'headgear':'headwear','top':'top','bottom':'bottom'}[role]]]
        if key=='default' or (role=='hair' and key==authored):return {'mode':'preserve-authored','authoredAlias':authored}
        if key=='ombre':return {'mode':'preserve-baked-ombre','groom':'preserve-authored-root-pigment'}
        value=next(row[2] for row in c['options']['colors'][role] if row[0]==key)
        return {'mode':'recolor','srgb':value,'linearRGB':linear(value)}
    hair=pigment('hairColor','hair');top=pigment('topColor','top')
    hat=pigment('headgearColor','headgear');bottom=pigment('bottomColor','bottom')
    textures={}
    if s['top']=='jersey' and top['mode']=='recolor':
        color=s['topColor'];directory=c['shared_jersey_dyes_dir']
        textures={'pattern':f'{directory}/jersey-{color}-pattern.png',
            'atlas':c['feminine_jersey_dyes'][color] if build=='Feminine' else f'{directory}/jersey-{color}-atlas.png'}
        if build=='Masculine' and sum(w*x for w,x in zip((.2126,.7152,.0722),top['linearRGB']))>.35:
            textures.update(front=f'{directory}/jersey-front-dark.png',back=f'{directory}/jersey-back-dark.png')
    frame=next(row[2] for row in c['options']['colors']['frames'] if row[0]==s['frameColor'])
    return {'policy':'preserve-authored-PBR-and-textures-except-explicit-overrides',
        'skinPigments':{key:value[s['skin']] for key,value in palettes.items() if key in ('skin','ink','stubble','lip')},
        'hair':hair,'facialHairTintMultiplier':.82,'headgear':hat,'top':top,'bottom':bottom,
        'jerseyTextures':textures,'frames':{'srgb':frame,'linearRGB':linear(frame),
            'metallic':.72 if s['frameColor'] in ('silver','gold') else .08,
            'pattern':'tortoise64' if s['frameColor']=='tortoise' else None},
        'lenses':{'part':s['lensTint'],'transmission':0,'ior':1,'thickness':0,'transparent':True,
                  'depthWrite':False,'side':'front','renderOrder':5,'opacityAndSurface':'preserve-selected-GLB'},
        'materialRuleReference':'material-rules.json','environmentMapIntensity':.7}


def resolve(s,c,root):
    validate(s,c)
    finish='ombre' if s['hairColor']=='ombre' else 'default'
    key='/'.join((s['build'],s['hair'],s['headwear'],s['top'],finish))
    if key not in c['fit_rows']:raise ValueError('Unsupported combination: '+key)
    fitted=c['fit_rows'][key];ind=c['independent_roles'][s['build']];face=ind['faces'][s['eyes']]
    parts={role:fitted[role] for role in ('hair','hairLengths','top','headgear')}
    parts.update(base=ind['bases'][s['bottom']]['shirtless' if s['top']=='shirtless' else 'clothed'],
        bottom=ind['bottoms'][s['bottom']],eyes=face['eyes'],lashes=face['lashes'],groom=ind['grooms'][s['groom']],
        mouth=c['groom_mouths'].get(s['groom'],face['mouth']))
    if s['glasses']!='none':
        glass=ind['glasses'][s['glasses']]
        parts.update(glasses=glass['glasses'],lenses=glass['lenses'][s['lensTint']])
    if s['detail']=='sprout':parts['extra']=fitted['sprout']
    elif s['detail']=='hot':parts['extra']=ind['hot']
    inactive=[]
    if s['headwear']=='none':inactive.append('headgearColor')
    if s['glasses']=='none':inactive.extend(('frameColor','lensTint'))
    if s['top']=='shirtless':inactive.append('topColor')
    bindings=material_bindings(s,c,root)
    for path in bindings['jerseyTextures'].values():
        if not (Path(root)/path).is_file():raise ValueError('Missing dye texture: '+path)
    effective={k:v for k,v in s.items() if k not in inactive}
    if effective['hairColor']=='darkbrown':effective['hairColor']='default'
    order=('base','bottom','top','hair','hairLengths','groom','mouth','eyes','lashes','headgear','glasses','lenses','extra')
    descriptors=[]
    for role in order:
        digest=parts.get(role)
        if not digest:continue
        entry=c['components'][digest]
        descriptors.append({'role':role,'sha256':digest,**entry})
    return {'settings':s,'profileBytes':None,'wireEncoding':'not-finalized-for-catalogue335',
        'fitSelector':key,'parts':descriptors,'materialBindings':bindings,'inactiveFields':inactive,
        'renderCacheKey':hashlib.sha256(json.dumps(effective,sort_keys=True,separators=(',',':')).encode()).hexdigest()}


if __name__=='__main__':
    if len(sys.argv)==2 and sys.argv[1]=='--defaults':print(json.dumps({b:defaults(b) for b in ('Feminine','Masculine')},indent=2))
    elif len(sys.argv)==3:
        root=Path(sys.argv[1]);s=json.loads(Path(sys.argv[2]).read_bytes())
        print(json.dumps(resolve(s,load(root),root),indent=2))
    else:raise SystemExit('Usage: resolve_avatar.py CATALOGUE_DIR SETTINGS.json | --defaults')
