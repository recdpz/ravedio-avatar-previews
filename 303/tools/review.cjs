const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const origin = process.env.PREVIEW_ORIGIN || 'http://127.0.0.1:9251';
const out = process.env.CAPTURE_DIR;
const angles = ['front','threequarter','profile','rightprofile','rear','rearquarter','top','underside'];
const ponytail = {build:'Feminine',hair:'ponytail',headwear:'headband',top:'open',bottom:'pants',
  hairColor:'default',headgearColor:'default',detail:'none',glasses:'none',view:'face'};

async function run() {
  if (!out) throw Error('Set CAPTURE_DIR');
  fs.mkdirSync(out, {recursive:true});
  const browser = await chromium.launch({executablePath:process.env.CHROMIUM_PATH,
    args:['--use-angle=d3d11','--ignore-gpu-blocklist']});
  try {
    const page = await browser.newPage({viewport:{width:1120,height:900}});
    let revision;
    async function open(next) {
      revision = next;
      await page.goto(origin+'/'+revision+'/');
      await page.waitForFunction(r => window['review'+r]?.ready(),revision);
    }
    async function choose(state) {
      const result = await page.evaluate(async ([r,config]) => {
        const review = window['review'+r];
        await review.set(config);
        if (!review.ready() || review.errors.length) throw Error(review.errors.join('\n'));
        return {render:review.rendered(), view:review.state().mode};
      },[revision,state]);
      for (const [key,value] of Object.entries(state)) {
        assert.equal(key === 'view' ? result.view : key === 'build' ? result.render.build : result.render.features[key],value,key);
      }
      return Object.fromEntries(Object.entries(result.render.components).map(([role,uri]) =>
        [role,new URL(uri,origin+'/'+revision+'/').pathname]));
    }
    async function capture(label,views=angles) {
      for (const angle of views) {
        await page.locator('#angle').selectOption(angle);
        const img = await page.evaluate(r => window['review'+r].capture(680),revision);
        fs.writeFileSync(path.join(out,[revision,label,angle].join('-')+'.png'),
          Buffer.from(img.split(',')[1],'base64'));
      }
    }
    const unaffected = ['none','cap','beanie','bucket','cowboy','ears','pashmina'];
    const styles = {
      Feminine:['bob','straight','curls','side-sweep','space-buns','twin-braids','box-braids'],
      Masculine:['taper','buzz','curly-top','afro','flow','locs','sidepart','middle-part'],
    };
    const baseline = new Map();
    for (const r of [302,303]) {
      await open(r);
      for (const hairColor of ['default','darkbrown','ombre']) {
        const state = {...ponytail,hairColor};
        for (const headwear of unaffected) {
          const current = await choose({...state,headwear});
          const key = hairColor+'-'+headwear;
          if (r===302) baseline.set(key,current);
          else assert.deepEqual(current,baseline.get(key));
        }
        const current = await choose(state);
        if (r===303) {
          assert(current.headgear.endsWith('/303/assets/ponytail-bandana.glb'));
          assert(current.hair.endsWith('/302/assets/ponytail-'+(hairColor==='ombre'?'ombre':'default')+'.glb'));
        }
        const key = 'fitted-'+hairColor;
        if (r===302) baseline.set(key,current);
        else assert.deepEqual({...current,headgear:baseline.get(key).headgear},baseline.get(key));
        if (hairColor !== 'darkbrown') await capture(hairColor);
      }
      await choose({...ponytail,headgearColor:'khaki'});
      await capture('khaki',['rear','rearquarter','profile','rightprofile']);
      for (const [build,hairs] of Object.entries(styles)) {
        for (const hair of hairs) {
          const state = {...ponytail,build,hair,top:build==='Feminine'?'open':'tank',detail:'sprout'};
          const current = await choose(state);
          if (r===302) baseline.set(build+'-'+hair,current);
          else assert.deepEqual(current,baseline.get(build+'-'+hair));
        }
      }
    }
    const sprout = await choose({...ponytail,detail:'sprout',headgearColor:'white'});
    assert(sprout.extra.endsWith('/302/assets/ponytail-sprout.glb'));
    await capture('sprout',['threequarter','rearquarter']);
    await page.locator('#show-cloth').uncheck();
    const visible = await page.evaluate(() => review303.inspect().visible);
    assert(!visible.headgear && !visible.extra && visible.hair);
    await page.locator('#show-cloth').check();
    console.log('36 unchanged fits and fitted Ponytail across colors, eight views, and cloth toggle verified');
  } finally { await browser.close(); }
}

run().catch(error => {console.error(error);process.exitCode=1});
