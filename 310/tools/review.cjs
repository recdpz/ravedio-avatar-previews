const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const out = process.env.CAPTURE_DIR;
const origin = process.env.PREVIEW_ORIGIN || 'http://127.0.0.1:9251';
const revisions = process.argv.slice(2).map(Number);
const angles = ['front','threequarter','profile','rightprofile','rear','rearquarter','top','underside'];
const styles = {
  Feminine:['bob','ponytail','straight','curls','side-sweep','space-buns','twin-braids','box-braids'],
  Masculine:['sidepart','taper','buzz','curly-top','afro','flow','locs','middle-part'],
};

async function main() {
  fs.mkdirSync(out,{recursive:true});
  const browser = await chromium.launch({executablePath:process.env.CHROMIUM_PATH,
    args:['--use-angle=d3d11','--ignore-gpu-blocklist']});
  try {
    const page = await browser.newPage({viewport:{width:820,height:680}});
    const faults = [];
    page.on('pageerror',e=>faults.push(e.message));
    page.on('response',r=>{if (r.status()>=400) faults.push(r.status()+' '+r.url());});
    await page.route('**/309/viewer.js',async route=>{
      const response = await route.fetch();
      const source = await response.text();
      // Closer diagnostic framing, using the production preview geometry.
      const js = source.replace("mode==='face'?1.5:2.7","mode==='face'?1.23:1.56")
        .replace("mode==='face'?1.88:1.28","mode==='face'?1.91:1.64");
      await route.fulfill({response,body:js});
    });
    for (const revision of revisions) {
      await page.goto(origin+'/'+revision+'/');
      await page.waitForFunction(r=>window['review'+r]?.ready(),revision);
      const choose = state => page.evaluate(async ([r,state])=>{
        const review=window['review'+r];
        await review.set({skin:1,groom:'none',detail:'none',glasses:'none',topColor:'default',
          headgearColor:'default',bottom:'pants',hairColor:'default',...state});
        if(!review.ready() || review.errors.length) throw Error(review.errors.join('\n'));
        const selected=review.rendered();
        for (const [key,value] of Object.entries(state)) {
          const actual=key==='view'?review.state().mode:key==='build'?selected.build:selected.features[key];
          if(actual!==value) throw Error(key+' '+actual+' != '+value);
        }
        return selected.components;
      },[revision,state]);
      async function capture(key,views) {
        for (const angle of views) {
          await page.locator('#angle').selectOption(angle);
          const png=await page.evaluate(r=>window['review'+r].capture(520),revision);
          fs.writeFileSync(path.join(out,[revision,key,angle].join('-')+'.png'),Buffer.from(png.split(',')[1],'base64'));
        }
      }
      const hats = new Set();
      for (const [build,hairs] of Object.entries(styles)) {
        for (const hair of hairs) {
          const state={build,hair,top:build==='Feminine'?'jersey':'tank',headwear:'beanie',view:'face'};
          const parts=await choose(state);
          hats.add(parts.headgear);
          await capture(hair,angles);
          if (revision===310) {
            const colored=await choose({...state,detail:'sprout',hairColor:'ombre',headgearColor:'white'});
            assert.equal(parts.headgear,colored.headgear);
            assert.match(colored.extra,/\/310\/assets\//);
            await capture(hair+'-white',['rearquarter','profile']);
          }
        }
      }
      assert.equal(hats.size,revision===310?16:1);
      console.log(revision+' beanie fits captured');
      const state={build:'Feminine',hair:'twin-braids',headwear:'none',view:'body'};
      for (const top of ['bandeau','triangle','strappy','tshirt','jersey','open','tank','sweatshirt']) {
        await choose({...state,top});
        await capture('braids-'+top,['front','profile','rightprofile','threequarter','rearquarter']);
      }
      for (const headwear of ['beanie','cap','bucket','cowboy','headband','ears','pashmina']) {
        await choose({...state,top:'open',headwear,hairColor:'ombre'});
        await capture('braids-'+headwear,['profile','threequarter']);
      }
      console.log(revision+' braid fits captured');
    }
    assert.deepEqual(faults,[]);
  } finally {await browser.close();}
}
main().catch(error=>{console.error(error);process.exitCode=1;});
