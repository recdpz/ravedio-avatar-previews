"""Keep the established feature selector and add bob-specific resolved fits."""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'335'
viewer=(ROOT/'309/viewer.js').read_text(encoding='utf8')
needle='const controlKey = '
assert viewer.count(needle)==1
viewer=viewer.replace(needle,
    'const bobContextUrl=new URL("./files/bob-fits.json",import.meta.url);\n'
    'const bobContext=await(await fetch(bobContextUrl)).json();\n'+needle)
needle='  return parts;\n}\nfunction component'
assert viewer.count(needle)==1
viewer=viewer.replace(needle,'''
  if(model==='Feminine'&&state.hair==='bob'){
    const finish=state.hairColor==='ombre'?'ombre':'default';
    const fit=bobContext.fits[state.headwear]?.[state.top]?.[finish];
    if(!fit)throw new Error('Missing integrated bob fit: '+state.headwear+'/'+state.top+'/'+finish);
    parts.hair=new URL(fit.hair,bobContextUrl).href;
    delete parts.hairLengths;
    if(fit.headgear)parts.headgear=new URL(fit.headgear,bobContextUrl).href;
    else delete parts.headgear;
    if(state.detail==='sprout')parts.extra=new URL(fit.sprout,bobContextUrl).href;
  }
  return parts;
}
function component''')
viewer=viewer.replace("hair:b==='Feminine'?'ponytail':'taper'","hair:b==='Feminine'?'bob':'taper'")
viewer=viewer.replace("eyes:'original'","eyes:b==='Feminine'?'bean':'original'")
viewer=viewer.replace("top:b==='Feminine'?'open':'tank'","top:b==='Feminine'?'jersey':'tank'")
viewer=viewer.replace("bottom:b==='Feminine'?'skirt':'shorts'","bottom:b==='Feminine'?'pants':'shorts'")
viewer=viewer.replace("skin:overlay ? 3 : 1","skin:b==='Feminine'?2:(overlay?3:1)")
viewer=viewer.replace("angle='threequarter',mode='body'","angle='threequarter',mode='face'")
(OUT/'viewer.js').write_text(viewer,encoding='utf8')

html=(ROOT/'330/index.html').read_text(encoding='utf8')
html=html.replace('data-art-revision="330"','data-art-revision="335"')
html=html.replace('Ravedio · 330','Ravedio · 335').replace('AVATAR REVIEW · 330','AVATAR REVIEW · 335')
html=html.replace('<h1>Feminine Bob</h1>','<h1>Wavy bob · Integrated</h1>')
html=html.replace('Jaw-length bob with a stronger face-framing sweep and stacked layers at the nape. <a href="./files/comparison.jpg">Compare with 329</a>.',
    'Approved B, with fitted headwear and brown-to-caramel ombré. The uncovered source is unchanged from 334. <a href="../334/?style=waves">Approved reference</a>.')
html=html.replace('Ravedio330-Bob.blend','Ravedio335-Wavy-bob.blend')
html=html.replace('delivery/Ravedio330-bob-source.zip','delivery/Ravedio335-wavy-bob-source.zip')
html=html.replace('>Catalog source update</a>','>Bob update from 330</a><a href="./files/delivery/Ravedio335-full-source-catalogue.zip">Full source catalogue</a>')
html=html.replace('<a href="./files/headwear.jpg">Headwear fits</a>','<a href="./files/headwear.jpg">Headwear fits</a><a href="./files/colors.jpg">Hair colors</a><a href="./files/ombre.jpg">Ombré fits</a>')
html=html.replace('src="../309/viewer.js"','src="./viewer.js"')
html=html.replace('id="face" aria-pressed="false"','id="face" aria-pressed="true"')
html=html.replace('id="body" aria-pressed="true"','id="body" aria-pressed="false"')
gallery='''<section class="group" style="margin-top:24px"><h2>Studio render checks</h2>
<p class="small">Blender renders of the exported components: Tan skin, Rounded bean eyes and Jersey. These controls are independent of the rotatable model above.</p>
<div class="fields"><label>Headwear<select id="source-hat"></select></label><label>Hair color<select id="source-color"></select></label><label>View<select id="source-angle"></select></label></div>
<a id="source-link" href="files/review/none-default-threequarter.png" style="display:block;max-width:560px;margin:16px auto"><img id="source-image" src="files/review/none-default-threequarter.png" width="480" height="480" alt="Exported wavy bob studio render" style="display:block;width:100%;height:auto;background:#F1F4FA;border-radius:12px"></a>
</section>'''
html=html.replace('</div><nav>', '</div>'+gallery+'<nav>')
html=html.replace('</main><script type="importmap">','</main><script type="module" src="./studio.js"></script><script type="importmap">')
(OUT/'index.html').write_text(html,encoding='utf8')
