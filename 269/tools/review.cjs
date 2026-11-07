
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const out = process.env.CAPTURE_DIR;
const origin = process.env.PREVIEW_ORIGIN || 'http://127.0.0.1:9251';
if (!out) throw new Error('Set CAPTURE_DIR to a scratch folder');
fs.mkdirSync(out, { recursive: true });

const builds = {
  Feminine: ['ponytail', 'straight', 'curls'],
  Masculine: ['taper', 'flow', 'middle-part'],
};
const angles = ['front','threequarter','profile','rightprofile','rearquarter','rear','top','underside'];

async function set(page, revision, state) {
  await page.evaluate(async ({revision, state}) => {
    const view = window['review' + revision];
    await view.set(state);
    if (!view.ready() || view.errors.length) throw new Error(view.errors.join('\n'));
    const actual = view.state();
    for (const [key, value] of Object.entries(state)) {
      if (actual[key] !== value) throw new Error(key + ' selected ' + actual[key] + ', expected ' + value);
    }
  }, {revision, state});
}

async function capture(page, revision, name, size, sceneIndex=1) {
  const png = await page.evaluate(({revision,size,sceneIndex}) =>
    window['review' + revision].capture(size)[sceneIndex].png, {revision,size,sceneIndex});
  fs.writeFileSync(path.join(out, name + '.png'), Buffer.from(png.split(',')[1], 'base64'));
}

async function main() {
  const browser = await chromium.launch({
    executablePath: process.env.CHROMIUM_PATH,
    headless: true,
    args: ['--use-angle=d3d11','--ignore-gpu-blocklist'],
  });
  try {
    const current = await browser.newPage({viewport:{width:390,height:844}});
    const reference = await browser.newPage({viewport:{width:390,height:844}});
    const failures = [];
    for (const [p, rev] of [[current,269],[reference,268]]) {
      p.on('pageerror', e => failures.push(String(e)));
      p.on('response', r => { if (r.status() >= 400) failures.push(r.status() + ' ' + r.url()); });
      await p.goto(origin + '/' + rev + '/?mode=body&angle=profile');
      await p.waitForFunction(rev => window['review' + rev]?.ready(), rev);
    }
    let visuals = 0, matrix = 0, small = 0, matches = 0;
    const pairs = [];
    for (const [build, styles] of Object.entries(builds)) {
      const masculine = build === 'Masculine';
      const shirt = masculine ? 'buttonup' : 'open';
      for (const hair of styles) for (const headwear of ['none','cap','pashmina']) {
        const state = {
          build,hair,headwear,top:'sweatshirt',bottom:'pants',eyes:'original',
          glasses:headwear==='cap' ? (masculine?'rectangular':'reading') : 'none',
          groom:masculine?'short':'none',mode:'body',skin:1,
        };
        const name = [build,hair,headwear].join('-');
        await set(current,269,state);
        await set(reference,268,{...state,headScale:'0.8',lift:-8,heightMode:'manual'});
        for (const angle of angles) {
          await set(current,269,{angle});
          await capture(current,269,name+'-'+angle,448);
          visuals++;
        }
        for (const angle of ['threequarter','profile']) {
          await set(current,269,{mode:'face',angle});
          await set(reference,268,{mode:'face',angle});
          await capture(current,269,name+'-'+angle+'-baked',512);
          await capture(reference,268,name+'-'+angle+'-selected',512);
          pairs.push(name+'-'+angle);
          matches++;
        }
        if (headwear==='pashmina') {
          for (const top of ['tank','tshirt','jersey',shirt]) {
            await set(current,269,{top,mode:'body',angle:'threequarter'});
            await capture(current,269,name+'-'+top+'-threequarter',448);
            await set(current,269,{angle:'profile'});
            await capture(current,269,name+'-'+top+'-profile',448);
            matrix++;
          }
          if (masculine) {
            await set(current,269,{top:shirt,mode:'body',angle:'threequarter'});
            await set(reference,268,{top:shirt,mode:'body',angle:'threequarter'});
            await capture(current,269,name+'-buttonup-after',840);
            await capture(reference,268,name+'-buttonup-before',840);
            await set(current,269,{angle:'rightprofile'});
            await capture(current,269,name+'-buttonup-side',840);
          }
        }
      }
      for (const skin of [0,1,2,3]) {
        await set(current,269,{
          build,hair:styles[0],top:'sweatshirt',headwear:'none',glasses:'none',groom:'none',
          mode:'chat',angle:'front',skin,
        });
        for (const size of [48,64]) {
          await capture(current,269,'portrait-'+build+'-'+skin+'-'+size,size);
          small++;
        }
      }
      // A real selector interaction exercises options rebuilt after an earlier build switch.
      await current.locator('#bottom').selectOption('shorts');
      await current.waitForFunction(() => review269.ready() && review269.state().bottom === 'shorts');
      await current.locator('#bottom').selectOption('pants');
      await current.waitForFunction(() => review269.ready() && review269.state().bottom === 'pants');
    }
    for (const headwear of ['none','pashmina']) {
      await set(current,269,{
        build:'Masculine',hair:'taper',groom:'long',top:'sweatshirt',headwear,
        mode:'face',glasses:'none',angle:'threequarter',
      });
      for (const angle of ['threequarter','profile','rightprofile','underside']) {
        await set(current,269,{angle});
        await capture(current,269,'long-beard-'+headwear+'-'+angle,640);
        visuals++;
      }
    }
    if (failures.length) throw new Error(failures.join('\n'));
    fs.writeFileSync(path.join(out,'browser.json'),JSON.stringify({visuals,matrix,small,matches,pairs},null,2));
    console.log({visuals,matrix,small,matches});
  } finally {
    await browser.close();
  }
}
main().catch(err => { console.error(err); process.exitCode = 1; });
