import sys
sys.path.insert(0,'E:/Ravedio-Avatar/catalogue235')
from common235 import *
import headwear235 as hats,accessories235 as acc
from mathutils import Matrix
HATS=['none','cap','beanie','bucket','cowboy','headband','ears','pashmina']
def hair_path(build,style):
 p=P/'components'/f'{build}-{style}-hair.glb'
 return p if p.exists() else (R/'234'/CAT['builds'][build]['hair'][style]['path']).resolve()
def covered(build,style,hat):
 changed=0
 if build=='Feminine' and style=='ponytail':
  tail=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.get('component159')=='hair' and ('tail220' in o.name or 'tie220' in o.name)]
  tie=next(o for o in tail if 'tie220' in o.name);center=sum((tie.matrix_world@v.co for v in tie.data.vertices),Vector())/len(tie.data.vertices)
  if hat=='pashmina':
   for o in tail:u.delete(o)
   a.sphere('Hair / tucked gathered pony235',(0,.30,1.87),(.095,.075,.095),a.M['hair'],'hair')
  else:
   # A deliberately tied low pony for closed hats. The approved free/high pony
   # is preserved for uncovered hair and its exact selected rear-hole cap fit.
   for o in tail:u.delete(o)
   from hair235 import lock
   for k in range(5):
    dx=(k-2)*.018;pts=[(dx*.45,.418,1.985),(dx,.488,1.990),(dx+.012,.550,1.930),(dx-.020,.575,1.80),(dx+.019,.552,1.65),(dx+.012,.505,1.59+.012*k)]
    lock('Hair / closed-hat low pony235 '+str(k),pts,[.016,.028,.030,.029,.019,.003],[.010,.021,.022,.020,.013,.003],k*.7,n=64,tip=.12)
   a.tube('Hair / low gathered elastic235',[(.041*math.sin(q),.432,1.985+.033*math.cos(q)) for q in np.linspace(0,2*math.pi,57)],.006,.005,a.M['band'],n=57,sides=10,taper=False,group='hair')
 for o in bpy.context.scene.objects:
  if o.type!='MESH' or o.get('component159')!='hair' or any(x in o.name.lower() for x in ['tail220','tie220','adjustable front','tucked gathered','low pony235','low gathered elastic']):continue
  inv=o.matrix_world.inverted()
  for v in o.data.vertices:
   p=o.matrix_world@v.co
   if p.z<1.80:continue
   dv=p-a.C;unit=Vector((dv.x/a.R.x,dv.y/a.R.y,dv.z/a.R.z)).normalized();th=math.acos(max(-1,min(1,unit.z)));ph=math.atan2(unit.x,-unit.y);seated=h.head_surface(th,ph,.010 if hat=='pashmina' else .014);weight=smooth((p.z-1.80)/.20)
   if dv.length>(seated-a.C).length:v.co=inv@p.lerp(seated,weight);changed+=1
 return changed
def conceal_rear_crown():
 build=bpy.context.scene.get('build235','Feminine');source=P/'sources'/f'{build}-pashmina-knot235.blend'
 with bpy.data.libraries.load(str(source),link=False) as(src,dst):dst.objects=[n for n in src.objects if 'soft crown and rear cape235' in n]
 obs=[o for o in dst.objects if o is not None];assert obs,'Missing frozen hood support';cloth=tree(obs)
 for o in obs:u.delete(o)
 changed=0
 for o in bpy.context.scene.objects:
  if o.type!='MESH' or o.get('component159')!='hair':continue
  inverse=o.matrix_world.inverted()
  for v in o.data.vertices:
   p=o.matrix_world@v.co
   if p.z<=1.40 or (p.y<-.30 and p.z<2.1):continue
   direction=(p-a.C).normalized();hit,normal,_,distance=cloth.ray_cast(a.C,direction,1.5)
   if hit is not None and (p-a.C).length>distance-.026:v.co=inverse@(a.C+direction*max(.1,distance-.026));changed+=1
 return changed
def press_bandana_roots():
 # Whole curls must be authored in a held-back arrangement. Point projection
 # cuts them apart and creates the owner-rejected mushroom/gap deformation.
 s=bpy.context.scene;style=s.get('hairStyle235','');build=s.get('build235','')
 if build=='Feminine':
  if style=='space-buns':remove(['hair']);imported((R/'234'/CAT['fits']['Feminine-space-buns']['cap']['hair']).resolve(),'hair')
  covered(build,style,'bucket')
 elif build=='Masculine' and style in ['afro','curly-top']:
  import hair235
  remove(['hair'])
  if style=='afro':hair235.coiled_puffs(True)
  else:hair235.curly(False,True)
 return 0
def main():
 only=next((x.split('=',1)[1].split(',') for x in sys.argv if x.startswith('--only=')),None);hat_filter=next((x.split('=',1)[1].split(',') for x in sys.argv if x.startswith('--hats=')),None);partial=only or hat_filter
 records=json.loads((P/'fits235.json').read_text()) if partial else {};sprouts=json.loads((P/'sprouts235.json').read_text()) if partial else {};haircache={};hatcache={};proof=json.loads((P/'fit-proof235.json').read_text()) if partial else []
 for build in ['Feminine','Masculine']:
  styles=list(CAT['builds'][build]['hair'])+(['middle-part'] if build=='Masculine' else [])
  for style in styles:
   if only and build+'-'+style not in only:continue
   key=build+'-'+style;records.setdefault(key,{})
   for hat in HATS:
    if hat_filter and hat not in hat_filter:continue
    s=load(build);s['build235']=build;s['hairStyle235']=style;protected=protect(s);remove(['hair']);exact=build=='Feminine' and style=='ponytail' and hat=='cap';classkey=key+('-pashmina' if hat=='pashmina' else '-closed')
    iscovered=hat in ['cap','beanie','bucket','cowboy','pashmina']
    if exact:
     fit=CAT['fits'][key]['cap'];hp=(R/'234'/fit['hair']).resolve();imported(hp,'hair');hats.build(hat,build);entry=dict(fit)
    else:
     src=hair_path(build,style)
     if iscovered and classkey in haircache:src=P/haircache[classkey]
     elif iscovered and build=='Feminine' and style=='space-buns':src=(R/'234'/CAT['fits'][key]['cap']['hair']).resolve()
     imported(src,'hair')
     if iscovered and classkey not in haircache:
      count=covered(build,style,hat);u.bake(s);path=P/'components'/f'{classkey}-hair.glb';ex.export(s,path,'hair');haircache[classkey]='components/'+path.name
     hats.build(hat,build)
     band_hair=None
     if hat=='headband':
      press_bandana_roots();u.bake(s);band_hair='components/'+key+'-bandana-hair.glb';ex.export(s,P/band_hair,'hair')
     if hat=='pashmina':
      conceal_rear_crown();u.bake(s);ex.export(s,P/haircache[classkey],'hair')
     headkey=key+'-bandana' if hat=='headband' else build+'-'+hat
     if hat=='pashmina':hatcache[headkey]='components/'+build+'-pashmina-headgear.glb'
     if hat!='none' and headkey not in hatcache:
      u.bake(s);path=P/'components'/f'{headkey}-headgear.glb';ex.export(s,path,'headgear');hatcache[headkey]='components/'+path.name
     hp=band_hair if hat=='headband' else haircache[classkey] if iscovered else ('components/'+src.name if src.parent==P/'components' else CAT['builds'][build]['hair'][style]['path']);entry=dict(hair=hp,headgear=hatcache.get(headkey))
    if hat!='none':records[key][hat]=entry
    anchor=acc.sprout();u.bake(s);spath=P/'components'/f'{key}--{hat}-sprout.glb';ex.export(s,spath,'extra');sprouts[key+'--'+hat]={'path':'components/'+spath.name,**anchor}
    check(s,protected)
    # Reopen final component exports for all fits before reviewing actual materials.
    if hat!='none':
     remove(['hair','headgear']);
     for group,path in entry.items():imported((P/path if path.startswith('components/') else R/'234'/path).resolve(),group)
    else:remove(['hair']);imported(hair_path(build,style),'hair')
    remove(['extra']);imported(spath,'extra')
    render(s,key+'--'+hat,['front','threequarter','profile','rightprofile','rear','top','underside'],'review2',192,body=hat=='pashmina')
    if build=='Feminine' and style=='ponytail' and hat in ['beanie','pashmina']:
     bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(P/'sources'/f'{key}--{hat}-assembly.blend'),compress=True)
    proof=[x for x in proof if (x['build'],x['hair'],x['hat'])!=(build,style,hat)];proof.append(dict(build=build,hair=style,hat=hat,protected_exact=True,reopened=True,source_hair=str(hair_path(build,style)),recipe='selected224 exact' if exact else 'Feminine triangular crown scarf/low gather; masculine folded band/held-back curls where needed' if hat=='headband' else 'free lengths retained except concealed tuck; covered crown; low gathered or tucked pony' if iscovered else 'uncovered hair; fitted hat',sprout=anchor))
    u.dump(P/'fits235.json',records);u.dump(P/'sprouts235.json',sprouts);u.dump(P/'fit-proof235.json',proof);print('FIT235',key,hat,flush=True)
if __name__=='__main__':main()
