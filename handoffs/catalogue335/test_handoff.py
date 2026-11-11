"""Mapping and codec evidence checks; no production codec is modified."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,copy

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import legacy_profile3 as legacy
import resolve_avatar as reference

ART=Path('D:/Ravedio-Avatar-Work/native335')
PACKAGE=Path('D:/Ravedio-Avatar-Work/handoff335/package')


def main():
    c=reference.load(ART);count=0
    for key,row in c['fit_rows'].items():
        build,hair,hat,top,finish=key.split('/')
        s=reference.defaults(build)
        s.update(hair=hair,headwear=hat,top=top,hairColor='ombre' if finish=='ombre' else 'default')
        actual=reference.resolve(s,c,ART)
        assert actual['fitSelector']==key
        parts={p['role']:p['sha256'] for p in actual['parts']}
        for role in ('hair','hairLengths','headgear','top'):
            assert parts.get(role)==row[role],(key,role)
        assert actual['profileBytes'] is None
        count+=1
    independent=0
    for build,options in c['options']['builds'].items():
        for field,table in (('hair','hair'),('eyes','eyes'),('groom','grooms'),('top','tops'),('bottom','bottoms')):
            for value in options[table]:
                s=reference.defaults(build);s[field]=value
                result=reference.resolve(s,c,ART)
                for part in result['parts']:assert (ART/part['file']).is_file()
                if field=='groom' and value in c['groom_mouths']:
                    assert next(p['sha256'] for p in result['parts'] if p['role']=='mouth')==c['groom_mouths'][value]
                independent+=1
        for glasses in c['options']['glasses']:
            for tint in ('clear','dark'):
                s=reference.defaults(build);s.update(glasses=glasses,lensTint=tint)
                reference.resolve(s,c,ART);independent+=1
        for field,role in reference.COLOR_FIELDS.items():
            for value,*_ in c['options']['colors'][role]:
                s=reference.defaults(build);s[field]=value
                reference.resolve(s,c,ART);independent+=1
        for detail in c['options']['details']:
            s=reference.defaults(build);s['detail']=detail
            reference.resolve(s,c,ART);independent+=1
    negative=0
    for changes in ({'hair':'bald'},{'eyes':'round'},{'detail':'faceGems'},{'top':'shirtless'},
                    {'groom':'long'},{'skin':True},{'schemaVersion':2},{'catalogueRevision':334},{'unassignedWireId':0}):
        s=reference.defaults('Feminine');s.update(changes)
        try:reference.resolve(s,c,ART)
        except (ValueError,TypeError):negative+=1
        else:raise AssertionError('Invalid selection accepted: '+str(changes))
    golden=[({},[0x54,0x05,0x00]),
        ({'build':1,'skin':0,'hair':1,'hairColor':1,'headgear':1,'gearColor':1,'glasses':3,'extra':3,'face':1},[0x42,0x49,0x7d]),
        ({field:len(table)-1 for field,table in legacy.TABLES.items()},[0x7f,0xff,0xff])]
    for values,expected in golden:
        assert legacy.encode(values)==expected
        assert legacy.decode(expected)['values']=={**legacy.DEFAULT,**values}
    for field,table in legacy.TABLES.items():
        for value in range(len(table)):
            expected={**legacy.DEFAULT,field:value}
            assert legacy.decode(legacy.encode(expected))['values']==expected
    assert legacy.decode([0,0,0])['canonicalClear']
    assert not legacy.decode([0x40,0,0])['canonicalClear']
    assert legacy.decode([0x40,0,0])['type']=='avatar'
    for bad in ([0,0],[0,0,0,0],[256,0,0]):
        try:legacy.decode(bad)
        except ValueError:pass
        else:raise AssertionError('Invalid legacy length/value accepted')
    for case in json.loads((PACKAGE/'named-examples.json').read_bytes()):
        assert reference.resolve(case['input'],c,ART)==case['expected']
    try:
        import jsonschema
    except ImportError:
        jsonschema=None
    if jsonschema:
        schema=json.loads((PACKAGE/'avatar-settings.schema.json').read_bytes())
        jsonschema.Draft202012Validator.check_schema(schema)
        for case in json.loads((PACKAGE/'named-examples.json').read_bytes()):
            jsonschema.validate(case['input'],schema)
        invalid=reference.defaults('Feminine');invalid['groom']='long'
        assert list(jsonschema.Draft202012Validator(schema).iter_errors(invalid))
    output={'fit_rows_checked':count,'independent_option_cases':independent,'invalid_named_cases_rejected':negative,
        'legacy_golden_vectors':len(golden),'named_worked_examples':8,'production_code_changed':False,
        'swift_kotlin_built_here':False}
    output['json_schema_2020_12_checked']=bool(jsonschema)
    (PACKAGE/'validation.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps(output))


if __name__=='__main__':main()
