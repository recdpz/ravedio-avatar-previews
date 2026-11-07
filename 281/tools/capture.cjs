const fs = require('node:fs');
const path = require('node:path');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'playwright');

const origin = process.env.PREVIEW_ORIGIN || 'http://127.0.0.1:9251';
const destination = path.join(__dirname,'../views');
const looks = ['baseline','air','curtain'];
const views = [
  ['front','face',512], ['threequarter','face',512], ['profile','face',512],
  ['rightprofile','face',512], ['top','face',512],
  ['front','chat',120], ['profile','chat',120],
];

async function main() {
  const browser = await chromium.launch({executablePath:process.env.CHROMIUM_PATH,headless:true,
    args:['--use-angle=d3d11','--ignore-gpu-blocklist']});
  const failed = [];
  try {
    fs.mkdirSync(destination,{recursive:true});
    for (const look of looks) {
      const baseline = look === 'baseline';
      const revision = baseline ? 280 : 281;
      const page = await browser.newPage({viewport:{width:1100,height:940}});
      page.on('pageerror',e=>failed.push(String(e)));
      page.on('response',r=>{if(r.status()>=400 && !r.url().endsWith('favicon.ico'))failed.push(r.url())});
      const query = new URLSearchParams({study:look,build:'Feminine',hair:'side-sweep',
        headwear:'none',hairColor:'default',skin:'1',top:'sweatshirt',bottom:'pants',
        detail:'none',glasses:'none',mode:'face',angle:'front'});
      await page.goto(origin+(baseline ? '/280/' : '/281/render.html')+'?'+query);
      await page.waitForFunction(rev=>window['review'+rev]?.ready(),revision);
      const actual = await page.evaluate(n=>window['review'+n].rendered().components.hair,revision);
      const expected = baseline ? '/280/assets/side-sweep-none.glb' : '/281/assets/'+look+'.glb';
      if (new URL(actual).pathname !== expected) throw Error('Wrong geometry for '+look+': '+actual);
      for (const [angle,mode,size] of views) {
        await page.locator('#'+mode).click();
        await page.locator('#angle').selectOption(angle);
        const data = await page.evaluate(({revision,size}) => window['review'+revision].capture(size),{revision,size});
        fs.writeFileSync(path.join(destination,[look,mode,angle].join('-')+'.png'),
          Buffer.from(data.split(',')[1],'base64'));
      }
      await page.close();
    }
    if (failed.length) throw Error(failed.join('\n'));
    console.log('Captured 3 matched looks at 512 px and 120 px');
  } finally {
    await browser.close();
  }
}

main().catch(e=>{console.error(e);process.exitCode=1});
