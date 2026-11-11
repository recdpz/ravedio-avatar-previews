"""Read-only reference for the existing sprite profile. Not a 3D codec."""
TYPE_NAMES=('none','avatar','flag','socialMode')
TABLES={
 'build':['a','b'],
 'skin':['porcelain','golden','bronze','cocoa'],
 'hairColor':['midnight','chestnut','sand','ember','cloud','flamingo','voltage','ultraviolet'],
 'headgear':['none','cap','beanie','cowboy','bucket','bandana','animalEars','hoodie'],
 'gearColor':['onyx','crimson','tangerine','sunbeam','jungle','lagoon','cobalt','magenta'],
 'glasses':['none','round','shade','rect','wayfarer','aviator','cateye','sport'],
 'extra':['none','freckles','earrings','faceGems'],
 'face':['none','detail1','detail2','detail3'],
 'hair':['none','style1','style2','style3','style4','style5','style6','style7'],
}
HAIR_LABELS={
 'a':['Shaved/bald','Taper','Curls','Fringe','Buzz cut','Side part','Man bun','Rounded afro'],
 'b':['Shaved/bald','Bob','Long waves','High ponytail','Pixie','Lob','Box braids','Curls'],
}
FACE_LABELS={'a':['Clean','Stubble','Mustache','Full beard'],
             'b':['Soft','Lashes','Blush','Lashes + blush']}
DEFAULT={'build':0,'skin':1,'hair':2,'hairColor':0,'headgear':0,'gearColor':5,'glasses':0,'extra':0,'face':0}


def encode(values):
    s={**DEFAULT,**values}
    if set(s)!=set(DEFAULT):raise ValueError('Unknown legacy field')
    for field,table in TABLES.items():
        if type(s[field]) is not int or not 0<=s[field]<len(table):raise ValueError(field)
    return [0x40|(s['skin']<<4)|(s['hair']<<1)|(s['hairColor']>>2),
            ((s['hairColor']&3)<<6)|(s['headgear']<<3)|s['gearColor'],
            (s['glasses']<<5)|(s['build']<<4)|(s['extra']<<2)|s['face']]


def decode(data):
    if len(data)!=3 or any(type(v) is not int or not 0<=v<=255 for v in data):raise ValueError('Exactly three bytes required')
    a,b,c=data;kind=a>>6
    out={'format':'legacy-typed-profile3','profileBytes':list(data),'type':TYPE_NAMES[kind],
         'canonicalClear':data==[0,0,0],'catalogue335Mapping':None}
    if kind!=1:
        return {**out,'payload22':((a&63)<<16)|(b<<8)|c,'presentation':'initials-fallback'}
    values={'build':(c>>4)&1,'skin':(a>>4)&3,'hair':(a>>1)&7,
            'hairColor':((a&1)<<2)|(b>>6),'headgear':(b>>3)&7,'gearColor':b&7,
            'glasses':c>>5,'extra':(c>>2)&3,'face':c&3}
    names={key:TABLES[key][value] for key,value in values.items()}
    names['hairLabel']=HAIR_LABELS[names['build']][values['hair']]
    names['faceLabel']=FACE_LABELS[names['build']][values['face']]
    build=names['build'];face=values['face'];layers=[]
    def add(sprite,palette):layers.append({'sprite':sprite,'palette':palette})
    add('headSpriteB' if build=='b' else 'headSprite',f"skinPalettes[{values['skin']}]")
    if build=='b' and face:
        if face!=2:add('lashSprite','inkColor')
        if face!=1:add('blushSprite',f"blushColors[{values['skin']}]")
    extra=values['extra']
    if extra:add(('','freckleSprite','earringSprite','gemSprite')[extra],
                 ('',f"freckleColors[{values['skin']}]",'earringPalette','gemPalette')[extra])
    if values['hair']:
        key=f"{build}{values['hair']}"
        add('hairSprites.'+key,f"hairPalettes.{key}[{values['hairColor']}]")
    if build=='a' and face:add(f'facialSprites[{3-face}]',f"facialPalettes[{3-face}][{values['hairColor']}]")
    if values['glasses']:add(f"glassesSprites[{values['glasses']-1}]",f"glassesPalettes[{values['glasses']-1}]")
    if values['headgear']:add(f"hatSprites[{values['headgear']-1}]",f"gearPalettes[{values['gearColor']}]")
    return {**out,'values':values,'names':names,'legacySpriteLayers':layers,'presentation':'legacy-sprite'}
