
const fs = require('node:fs');
const path = require('node:path');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const destination = process.env.CAPTURE_DIR;
if (!destination) throw new Error('Set CAPTURE_DIR to a scratch directory');
fs.mkdirSync(destination, {recursive: true});
const base = process.env.PREVIEW_ORIGIN || 'http://127.0.0.1:9251';
const catalogue = JSON.parse(fs.readFileSync(path.join(__dirname, '../../263/catalogue263.json')));
const angles = ['front','profile','rightprofile','rear'];

async function take(page, name, size=300) {
  const data = await page.evaluate(size => review270.capture(size), size);
  fs.writeFileSync(path.join(destination, name + '.png'), Buffer.from(data.split(',')[1], 'base64'));
}

async function select(page, options) {
  await page.evaluate(async options => {
    await review270.set(options);
    if (!review270.ready() || review270.errors.length) throw new Error(review270.errors.join('\n'));
    const state = review270.state();
    for (const [key,value] of Object.entries(options)) {
      const actual = key === 'view' ? state.mode : key in state.features ? state.features[key] : state[key];
      if (actual !== value) throw new Error(key + ' expected ' + value + ' got ' + actual);
    }
    if (state.proportions.headScale !== 0.8 || state.proportions.heightPercent !== -8) throw new Error('Wrong fit');
  },options);
}

async function angle(page,value) {
  await page.locator('#angle').selectOption(value);
}

async function main() {
  const browser = await chromium.launch({
    executablePath: process.env.CHROMIUM_PATH,
    headless:true,args:['--use-angle=d3d11','--ignore-gpu-blocklist'],
  });
  try {
    const page = await browser.newPage({viewport:{width:900,height:900}});
    const errors = [];
    page.on('pageerror', error => errors.push(String(error)));
    page.on('response', response => { if(response.status() >= 400) errors.push(response.status()+' '+response.url()); });
    await page.goto(base+'/270/');
    await page.waitForFunction(() => window.review270?.ready());
    const views = [], scarf = [], palette = [];
    for (const [build, c] of Object.entries(catalogue.builds)) {
      const feminine = build === 'Feminine';
      const tops = Object.keys(c.tops);
      for (const hair of Object.keys(c.hair)) {
        for (const headwear of Object.keys(catalogue.headwear)) {
          const state = {
            build,hair,headwear,top:'sweatshirt',bottom:'pants',eyes:'original',skin:1,
            detail:'sprout',glasses:'none',hairColor:'default',groom:feminine?'none':'short',
            view:headwear==='pashmina'||hair.includes('braids')?'body':'face',
          };
          await select(page,state);
          const key = [build,hair,headwear].join('_');
          for (const camera of angles) {
            await angle(page,camera);
            await take(page,key+'_'+camera);
          }
          views.push(key);
        }
        for (const top of tops) {
          await select(page,{build,hair,headwear:'pashmina',top,detail:'none',view:'body',angle:'threequarter'});
          const key = [build,hair,top].join('_');
          await take(page,key+'_drape');
          await angle(page,'profile');
          await take(page,key+'_drape-side');
          scarf.push(key);
        }
        await select(page,{build,hair,headwear:'none',top:'sweatshirt',hairColor:'ombre',view:'chat',angle:'front'});
        await take(page,[build,hair,'ombre'].join('_'),64);
        palette.push(build+'_'+hair);
      }
      for (const glasses of Object.keys(catalogue.glasses)) {
        if (glasses==='none') continue;
        await select(page,{
          build,headwear:'cap',hair:feminine?'ponytail':'curly-top',glasses,
          lensTint:glasses==='reading'?'clear':'dark',top:'sweatshirt',hairColor:'default',
          detail:'hot',view:'face',angle:'profile',
        });
        await take(page,build+'_'+glasses+'_glasses-side',384);
        await angle(page,'front');
        await take(page,build+'_'+glasses+'_glasses-front',384);
      }
      console.log(build,'checked',views.length,'headwear combinations',scarf.length,'pashmina outfits');
    }
    const coveredColors = [];
    for (const hair of ['straight','curls','twin-braids']) {
      await select(page,{build:'Feminine',hair,headwear:'pashmina',top:'sweatshirt',hairColor:'default',
        glasses:'none',detail:'none',view:'face',angle:'threequarter'});
      const geometry = () => page.evaluate(() => {
        const {hair,hairLengths} = review270.inspect().geometry;
        return [Object.values(hair).sort(),Object.values(hairLengths || {}).sort()];
      });
      const standard = await geometry();
      await page.locator('#hairColor').selectOption('ombre');
      await page.waitForFunction(() => review270.ready() && review270.rendered().features.hairColor === 'ombre');
      if (JSON.stringify(standard) !== JSON.stringify(await geometry())) throw new Error(hair+' ombre changed pose');
      await take(page,'Feminine_'+hair+'_covered-ombre',400);
      coveredColors.push(hair);
    }
    await page.setViewportSize({width:390,height:844});
    for (const build of Object.keys(catalogue.builds)) {
      await page.locator('#build').selectOption(build);
      await page.waitForFunction(b => review270.ready() && review270.rendered().build === b,build);
      await page.locator('#top').selectOption('sweatshirt');
      await page.waitForFunction(() => review270.ready() && review270.rendered().features.top === 'sweatshirt');
      for (const bottom of ['shorts','pants']) {
        await page.locator('#bottom').selectOption(bottom);
        await page.waitForFunction(v => review270.ready() && review270.rendered().features.bottom === v,bottom);
      }
      if (!((await page.locator('#bottom').boundingBox()).width > 100)) throw new Error('Mobile controls');
    }
    if (errors.length) throw new Error(errors.join('\n'));
    fs.writeFileSync(path.join(destination,'checks.json'),JSON.stringify({views,scarf,palette,coveredColors},null,2));
    console.log({headwear:views.length,scarves:scarf.length,ombre:palette.length,glasses:14});
  } finally {
    await browser.close();
  }
}
main().catch(error => {console.error(error);process.exitCode=1});
