const fs = require('node:fs');
const path = require('node:path');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'playwright');

const origin = process.env.PREVIEW_ORIGIN || 'http://127.0.0.1:9251';
const out = process.env.CAPTURE_DIR;
if (!out) throw new Error('Set CAPTURE_DIR for the review images');
const angles = ['front','threequarter','profile','rightprofile','rearquarter','rear','top','underside'];
const revision = Number(process.env.REVIEW_REVISION || 275);
const baseline = revision-1;
const fits = require(path.join(__dirname,'../..',String(revision),'hair-fits.json')).Feminine;
fs.mkdirSync(out,{recursive:true});

async function select(page, revision, change) {
  return page.evaluate(async ({revision,change}) => {
    const review = window['review'+revision];
    await review.set(change);
    const actual = review.rendered();
    if (!review.ready() || review.errors.length) throw Error(review.errors.join('\n'));
    for (const [key,value] of Object.entries(change)) {
      const got = key === 'view' ? review.state().mode : key === 'build' ? actual.build : actual.features[key];
      if (got !== value) throw Error(key+' became '+got);
    }
    return actual.components;
  },{revision,change});
}

async function captures(page, revision, prefix, views, size=512) {
  for (const angle of views) {
    await page.locator('#angle').selectOption(angle);
    const uri = await page.evaluate(({revision,size}) => window['review'+revision].capture(size),{revision,size});
    fs.writeFileSync(path.join(out,prefix+'_'+angle+'.png'),Buffer.from(uri.split(',')[1],'base64'));
  }
}

async function run() {
  const browser = await chromium.launch({executablePath:process.env.CHROMIUM_PATH,headless:true,
    args:['--use-angle=d3d11','--ignore-gpu-blocklist']});
  try {
    const failures = [], records = [];
    const pages = {};
    for (const rev of [baseline,revision]) {
      const page = pages[rev] = await browser.newPage({viewport:{width:1150,height:920}});
      page.on('pageerror',e=>failures.push(String(e)));
      page.on('response',r=>{if(r.status()>=400 && !r.url().endsWith('favicon.ico'))failures.push(r.url())});
      await page.goto(origin+'/'+rev+'/');
      await page.waitForFunction(n=>window['review'+n]?.ready(),rev);
    }
    const previous = pages[baseline], current = pages[revision];
    for (const [hair,entry] of Object.entries(fits)) {
      const common = {build:'Feminine',hair,view:'face',top:'sweatshirt',detail:'none',skin:1,
        bottom:'pants',glasses:'none',groom:'none',headgearColor:'default'};
      if (await current.locator('#hair option[value="'+hair+'"]').textContent() !== entry.label) throw Error('Wrong label');
      await select(previous,baseline,{...common,headwear:'none',hairColor:'default'});
      await captures(previous,baseline,hair+'_before',['front','profile','rear']);
      for (const [headwear,fit] of Object.entries(entry.fits)) {
        for (const hairColor of ['ombre','default']) {
          const result = await select(current,revision,{...common,headwear,hairColor});
          const expected = new URL(fit[hairColor],origin+'/'+revision+'/').href;
          if (result.hair !== expected) throw Error('Wrong fitted hair: '+result.hair);
          if (headwear === 'headband' && !result.headgear.includes('/27')) throw Error('Lost fitted bandana');
          if (hairColor === 'ombre') await captures(current,revision,hair+'_'+headwear+'_ombre',['threequarter','rear']);
        }
        await captures(current,revision,hair+'_'+headwear,angles);
        records.push({hair,headwear,angles,colors:['default','ombre']});
      }
      await select(current,revision,{...common,headwear:'none',hairColor:'black',view:'chat',
        glasses:'reading',lensTint:'clear'});
      await captures(current,revision,hair+'_chat',['front','threequarter'],120);
      for (const top of ['open','tank','jersey']) {
        await select(current,revision,{...common,headwear:'pashmina',hairColor:'default',top,view:'body'});
        await captures(current,revision,hair+'_pashmina_'+top,['threequarter','profile','rear']);
      }
      await select(current,revision,{...common,headwear:'none',hairColor:'default',detail:'sprout'});
      await captures(current,revision,hair+'_sprout',['threequarter','profile']);
    }
    for (const [build,hair,headwear] of [['Feminine','ponytail','headband'],['Feminine','straight','none'],
                                      ['Masculine','taper','headband']]) {
      const config = {build,hair,headwear,hairColor:'ombre',detail:'sprout',top:'sweatshirt'};
      const a = await select(previous,baseline,config), b = await select(current,revision,config);
      if (JSON.stringify(a)!==JSON.stringify(b)) throw Error('Unrelated fit changed for '+hair);
    }
    await current.setViewportSize({width:390,height:844});
    await select(current,revision,{build:'Feminine',hair:'space-buns',headwear:'headband',detail:'none'});
    await current.locator('#hair').selectOption('side-sweep');
    await current.waitForFunction(n=>window['review'+n].ready() && window['review'+n].rendered().features.hair==='side-sweep',revision);
    await current.locator('#show-cloth').uncheck();
    if (await current.evaluate(n=>window['review'+n].inspect().visible.headgear,revision)) throw Error('Cloth toggle failed');
    await current.locator('#show-cloth').check();
    if (failures.length) throw Error(failures.join('\n'));
    fs.writeFileSync(path.join(out,'checks.json'),JSON.stringify({revision,records,
      defaultAngleCount:records.length*angles.length,ombreAngleCount:records.length*2,
      mobileSelectorAndClothToggle:true,unrelatedFitsCompared:3},null,2)+'\n');
    console.log('Checked '+records.length+' looks, all eight angles, two color fits, and mobile selection');
  } finally {
    await browser.close();
  }
}

run().catch(e=>{console.error(e);process.exitCode=1});
