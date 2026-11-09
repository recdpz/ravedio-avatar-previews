const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const origin = process.env.PREVIEW_ORIGIN || 'http://127.0.0.1:9251';
const out = process.env.CAPTURE_DIR;
const revisions = process.argv.slice(2).map(Number);

async function main() {
  fs.mkdirSync(out,{recursive:true});
  const browser = await chromium.launch({executablePath:process.env.CHROMIUM_PATH,
    args:['--use-angle=d3d11','--ignore-gpu-blocklist']});
  try {
    const page = await browser.newPage({viewport:{width:860,height:700}});
    const errors = [];
    page.on('pageerror',e=>errors.push(e.message));
    page.on('response',r=>{if(r.status()>=400) errors.push(r.status()+' '+r.url());});
    await page.route('**/309/viewer.js',async route=>{
      const response = await route.fetch();
      const source = await response.text();
      const js = source.replace("mode==='face'?1.5:2.7","mode==='face'?1.38:2.7")
        .replace("mode==='face'?1.88:1.28","mode==='face'?1.91:1.28");
      await route.fulfill({response,body:js});
    });
    for(const revision of revisions) {
      await page.goto(origin+'/'+revision+'/?build=Feminine&hair=ponytail&headwear=beanie&mode=face');
      await page.waitForFunction(r=>window['review'+r]?.ready(),revision);
      const choose = state => page.evaluate(async ([r,s])=>{
        const review=window['review'+r];
        await review.set(s);
        if(!review.ready() || review.errors.length) throw Error(review.errors.join('\n'));
        const value=review.rendered();
        for (const k of ['headwear','hairColor','top','detail','bottom']) {
          if (value.features[k]!==s[k]) throw Error('Selection mismatch '+k);
        }
        return Object.fromEntries(Object.entries(value.components).map(([k,v])=>[k,new URL(v,document.baseURI).pathname.slice(1)]));
      },[revision,state]);
      const receipts = {}, wardrobe = {};
      const angles=['front','threequarter','profile','rightprofile','rearquarter','rear','top','underside'];
      for(const headwear of ['none','beanie','cap','headband','bucket','cowboy','ears','pashmina']) {
        for(const hairColor of ['default','ombre']) {
          const state={build:'Feminine',hair:'ponytail',headwear,hairColor,headgearColor:'default',top:'jersey',
            bottom:'skirt',glasses:'none',detail:'none',skin:3,view:'face'};
          const parts=await choose(state);
          receipts[headwear+'/'+hairColor]=parts;
          for(const angle of angles) {
            await page.locator('#angle').selectOption(angle);
            const png=await page.evaluate(r=>window['review'+r].capture(620),revision);
            fs.writeFileSync(path.join(out,[revision,headwear,hairColor,angle].join('-')+'.png'),
              Buffer.from(png.split(',')[1],'base64'));
          }
          for (const top of ['bandeau','triangle','strappy','tshirt','jersey','open','tank','sweatshirt']) {
            const setup={...state,top,bottom:'pants',detail:'sprout',view:'body'};
            const choice=await choose(setup);
            wardrobe[[headwear,hairColor,top].join('/')]=choice;
            if (top==='sweatshirt' && hairColor==='default') {
              await page.locator('#angle').selectOption('rear');
              const png=await page.evaluate(r=>window['review'+r].capture(520),revision);
              fs.writeFileSync(path.join(out,[revision,headwear,'hoodie-sprout','rear'].join('-')+'.png'),
                Buffer.from(png.split(',')[1],'base64'));
            }
          }
        }
      }
      fs.writeFileSync(path.join(out,'wardrobe-'+revision+'.json'),JSON.stringify(wardrobe,null,2)+'\n');
      fs.writeFileSync(path.join(out,'parts-'+revision+'.json'),JSON.stringify(receipts,null,2)+'\n');
      console.log(revision+' ponytail fits checked');
    }
    assert.deepEqual(errors,[]);
  } finally {await browser.close();}
}
main().catch(error=>{console.error(error);process.exitCode=1;});
