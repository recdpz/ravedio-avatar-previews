"""Record the actual visual review, including unresolved artistic limitations."""
from pathlib import Path
import json,shutil
P=Path(__file__).parent/'revision227';D=P.parent.parent/'floating138/mobile-preview/227'
proof=json.loads((P/'export-proof.json').read_text())
notes={
 'Feminine-curls':'Coverage and attachment corrected, but this reads as broad sculpted waves rather than a sufficiently distinct curly style. Further artistic revision required before catalogue acceptance.',
 'Masculine-locs':'Ends and root coverage repaired. Locks are still too regular and parallel, especially from the side and crown. Further artistic revision required before catalogue acceptance.',
 'Masculine-flow':'Surface intersection/checkerboard removed. The silhouette remains close to the feminine short bob; needs a more distinct masculine flow direction before catalogue acceptance.',
 'Feminine-bucket':'Fit reviewed. Crown and brim still look rather rigid; fabric character needs further refinement before catalogue acceptance.',
 'Feminine-cowboy':'Fit reviewed. Crown reads as a simplified dress-hat form; cowboy crease and brim character need further refinement before catalogue acceptance.',
 'Feminine-pashmina':'Continuous coverage and hair clipping repaired. The silhouette still reads more like a hood/cape than soft folded fabric. Further fold refinement required before catalogue acceptance.',
 'Masculine-afro':'No exposed support skirt or crown penetration in the reviewed fits. Dense curl geometry is an art source, not a mobile derivative; close-up curl regularity remains an artistic refinement opportunity.',
 'Masculine-curly-top':'Actual head-following taper and curl coverage repaired. Dense curl geometry needs a visually compared mobile derivative; no performance approval.',
 'Feminine-kaleidoscope':'Displayed as Faceted frames. This is a frame silhouette only, not kaleidoscope optics.',
 'Feminine-gems':'Visible at larger sizes; individual gem details are not reliably legible at32px.',
 'Feminine-sprout':'Silhouette readable; the thin stem/detail is subtle at32px.'
}
blocked={'Feminine-curls','Masculine-locs','Masculine-flow','Feminine-bucket','Feminine-cowboy','Feminine-pashmina'}
assets={k:{'disposition':'further artistic revision required' if k in blocked else 'reviewable candidate; owner acceptance pending','note':notes.get(k,'No obvious attachment, coverage or export break found in the reviewed views. This is not owner acceptance or exhaustive combination qualification.')} for k in proof}
review={'passes':['Source construction views, followed by geometry and fit corrections','Reopened ordinary GLB: front, three-quarter, both profiles, rear, top, underside and body','Four skin tones at128px; derived32/48/64px readability sheets'],
 'scope':'25 individual looks. No base body, face, wardrobe or selected224 ponytail/cap replacement.',
 'small_portrait_findings':'Eyes and main hair silhouettes remain readable. Gem/sprout details diminish at32px. Existing224 masculine stubble becomes faint at small sizes and was not changed in this slice.',
 'assets':assets,'production_approved':False}
(P/'visual-dispositions.json').write_text(json.dumps(review,indent=2)+'\n')
fits=json.loads((P/'fit-proof.json').read_text());out={}
for key,r in fits.items():
 out[key]={}
 for hat,item in r['combinations'].items():
  caveats=[]
  if key in blocked:caveats.append(assets[key]['note'])
  hkey='Feminine-'+hat
  if hkey in blocked:caveats.append(assets[hkey]['note'])
  out[key][hat]={'reviewed_views':['front','profile','rear','top'],'disposition':'fit reviewed; artwork revisions remain' if caveats else 'fit reviewed; owner acceptance pending','caveats':caveats,'rendered_hair_sha256':item['rendered_hair_sha256']}
(P/'fit-dispositions.json').write_text(json.dumps({'combinations':77,'review':'Actual exported hair reimported and viewed with headwear. Crown penetrations, abrupt covered-crown shelves and pashmina clipping were corrected and rendered again.','excluded':'Retained224 ponytail/taper with every new headwear, every outfit/accessory cross-product, native apps and phone performance are not covered.','assets':out},indent=2)+'\n')
for name in ['looks227.json','fits227.json']:
 data=json.loads((D/name).read_text())
 for key,item in data.items():
  base=key.split('--')[0];messages=[]
  if base in notes:messages.append(notes[base])
  if '--' in key and 'Feminine-'+key.split('--')[1] in blocked:messages.append(notes['Feminine-'+key.split('--')[1]])
  if messages:item['note']+=' Review: '+' '.join(messages)
 (D/name).write_text(json.dumps(data,indent=2)+'\n')
for i in range(3):shutil.copy2(P/f'small-{i}.png',D/f'small-{i}.png')
print('Recorded25 component and77 fit dispositions, with unresolved artwork explicitly held back.')
