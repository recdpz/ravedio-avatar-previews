const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const origin = process.env.PREVIEW_ORIGIN || 'http://127.0.0.1:9251';
const out = process.env.CAPTURE_DIR;
if (!out) throw new Error('Set CAPTURE_DIR to a review directory');
fs.mkdirSync(out, { recursive: true });
const catalogue = JSON.parse(fs.readFileSync(path.join(__dirname, '../../263/catalogue263.json')));
const angles = ['front', 'profile', 'rightprofile', 'rear', 'rearquarter', 'top', 'threequarter', 'underside'];

async function select(page, revision, change) {
  return page.evaluate(async ({revision,change}) => {
    const review = window['review'+revision];
    await review.set(change);
    if (!review.ready() || review.errors.length) throw new Error(review.errors.join('\n'));
    const state = review.state();
    for (const [key,value] of Object.entries(change)) {
      const current = key==='view' ? state.mode : state.features[key] ?? state[key];
      if (current !== value) throw new Error(key + ' changed to ' + current);
    }
    return review.rendered().components;
  },{revision,change});
}

function canonical(parts, revision) {
  return Object.fromEntries(Object.entries(parts).map(([role,url]) =>
    [role, new URL(url, origin+'/'+revision+'/').pathname]));
}

async function capture(page, revision, name, size=512) {
  const img = await page.evaluate(({revision,size}) => window['review'+revision].capture(size), {revision,size});
  fs.writeFileSync(path.join(out,name+'.png'), Buffer.from(img.split(',')[1],'base64'));
}

async function main() {
  const browser = await chromium.launch({
    executablePath: process.env.CHROMIUM_PATH,
    headless: true, args: ['--use-angle=d3d11','--ignore-gpu-blocklist'],
  });
  try {
    const current = await browser.newPage({viewport:{width:1100,height:920}});
    const earlier = await browser.newPage({viewport:{width:1100,height:920}});
    const failures = [];
    for (const [page,revision] of [[current,273],[earlier,272]]) {
      page.on('pageerror', error => failures.push(String(error)));
      page.on('response', response => { if (response.status() >= 400) failures.push(response.url()); });
      await page.goto(origin+'/'+revision+'/');
      await page.waitForFunction(rev => window['review'+rev]?.ready(), revision);
    }
    const matches = [];
    for (const [build, choices] of Object.entries(catalogue.builds)) {
      for (const hair of Object.keys(choices.hair)) {
        const revised = build==='Feminine' && ['ponytail','space-buns'].includes(hair);
        const folder = revised ? '/273/assets/' : '/272/assets/';
        const common = {build,hair,top:'sweatshirt',bottom:'pants',view:'face',skin:1,groom:'none',
                        detail:'none',glasses:'none',headgearColor:'default'};
        for (const hairColor of ['default','ombre']) {
          const bare = canonical(await select(current,273,{...common,hairColor,headwear:'none'}),273);
          const covered = canonical(await select(current,273,{...common,hairColor,headwear:'headband'}),273);
          for (const role of Object.keys(bare)) {
            if (bare[role] !== covered[role]) throw new Error(build+' '+hair+' '+role+' changed under bandana');
          }
          if (!covered.headgear?.startsWith(folder)) throw new Error('Old bandana in new viewer');
        }
        await select(current,273,{...common,hairColor:'default',headwear:'headband'});
        for (const angle of angles) {
          await current.locator('#angle').selectOption(angle);
          await capture(current,273,[build,hair,angle].join('_'));
        }
        const sprout = await select(current,273,{detail:'sprout',angle:'threequarter'});
        if (!canonical(sprout,273).extra?.startsWith(folder)) throw new Error('Old sprout placement');
        await capture(current,273,[build,hair,'sprout'].join('_'),384);
        if (revised) {
          await select(earlier,272,{...common,hairColor:'default',headwear:'headband'});
          for (const angle of ['front','profile','rearquarter','top']) {
            await earlier.locator('#angle').selectOption(angle);
            await capture(earlier,272,[build,hair,angle,'before'].join('_'));
          }
        }
        matches.push({build,hair,angles,revised,defaultHairExact:true,ombreHairExact:true,braidLengthsExact:true,sprout:true});
      }
    }
    for (const [build,hair] of [['Feminine','ponytail'],['Masculine','taper']]) {
      for (const headwear of ['none','cap','pashmina']) {
        const config = {build,hair,headwear,detail:'sprout',hairColor:'ombre',top:'sweatshirt',bottom:'pants',
                        glasses:'reading',lensTint:'clear',eyes:'original',groom:'none',skin:1};
        const previous = canonical(await select(earlier,272,config),272);
        const updated = canonical(await select(current,273,config),273);
        if (JSON.stringify(previous) !== JSON.stringify(updated)) throw new Error(headwear+' dependency changed: '+JSON.stringify({previous,updated}));
      }
    }
    await current.setViewportSize({width:390,height:844});
    await select(current,273,{build:'Feminine',hair:'ponytail',headwear:'headband',detail:'sprout',hairColor:'default'});
    await current.locator('#show-cloth').uncheck();
    const hidden = await current.evaluate(() => review273.inspect().visible);
    if (hidden.headgear || hidden.extra || !hidden.hair) throw new Error('Cloth inspection did not preserve hair');
    await current.locator('#show-cloth').check();
    for (const color of ['white','red']) {
      await current.locator('#headgearColor').selectOption(color);
      await current.waitForFunction(c => review273.ready() && review273.rendered().features.headgearColor === c,color);
      await capture(current,273,'mobile-'+color,384);
    }
    if (failures.length) throw new Error(failures.join('\n'));
    const receipt = {revision:273,matches,totalAngles:matches.length*angles.length,
                     preservedOtherFits:6,mobileColorAndClothControls:true};
    fs.writeFileSync(path.join(out,'checks.json'),JSON.stringify(receipt,null,2)+'\n');
    console.log({looks:matches.length, views:receipt.totalAngles, preservedOtherFits:6});
  } finally {
    await browser.close();
  }
}

main().catch(error => { console.error(error); process.exitCode = 1; });
