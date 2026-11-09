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
    const hats = ['none','cap','beanie','bucket','cowboy','headband','ears','pashmina'];
    const paths = new Map();
    for (const r of [303,304]) {
      await open(r);
      for (const headwear of hats) {
        for (const hairColor of ['default','ombre']) {
          const config = {...ponytail,headwear,hairColor};
          const current = await choose(config);
          const key = headwear+'-'+hairColor;
          if (r===303) paths.set(key,current);
          else {
            const old = paths.get(key);
            if (hairColor==='ombre') {
              assert(current.hair.endsWith('/304/assets/ponytail-'+headwear+'-ombre.glb'));
              assert.deepEqual({...current,hair:old.hair},old);
            } else assert.deepEqual(current,old);
          }
          if (hairColor==='ombre') await capture(headwear,['front','profile','rear','rearquarter','top']);
        }
      }
    }
    console.log("Ponytail palette and eight headwear fits verified");
  } finally { await browser.close(); }
}

run().catch(error => {console.error(error);process.exitCode=1});
