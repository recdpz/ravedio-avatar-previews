const fs = require('node:fs');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const origin = process.env.PREVIEW_ORIGIN || 'http://127.0.0.1:9251';
const [revision, output] = process.argv.slice(2);

async function main() {
  const browser = await chromium.launch({executablePath:process.env.CHROMIUM_PATH,
    args:['--use-angle=d3d11','--ignore-gpu-blocklist']});
  try {
    const page = await browser.newPage({viewport:{width:820,height:680}});
    await page.goto(origin+'/'+revision+'/');
    await page.waitForFunction(r => window['review'+r]?.ready(), revision);
    const selections = await page.evaluate(async revision => {
      const review = window['review'+revision];
      const keys = id => [...document.getElementById(id).options].filter(o=>!o.disabled).map(o=>o.value);
      async function choose(selection) {
        await review.set({view:'face',skin:1,bottom:'pants',groom:'none',glasses:'none',
          detail:'none',headgearColor:'default',topColor:'default',...selection});
        if (!review.ready() || review.errors.length) throw Error(review.errors.join('\n'));
        const {features, components} = review.rendered();
        for (const [field,value] of Object.entries(selection)) {
          if (field==='build' ? review.rendered().build!==value : features[field]!==value) throw Error(field);
        }
        return Object.fromEntries(Object.entries(components).map(([k,v])=>[k,new URL(v,document.baseURI).pathname.slice(1)]));
      }
      const hats = {}, twins = {};
      for (const build of ['Feminine','Masculine']) {
        const top = build==='Feminine' ? 'jersey' : 'tank';
        await choose({build,headwear:'none',top});
        for (const hair of keys('hair')) {
          hats[build+'/'+hair] = {};
          for (const hairColor of ['default','ombre']) {
            const p = await choose({build,hair,top,hairColor,headwear:'beanie',detail:'sprout'});
            hats[build+'/'+hair][hairColor] = Object.fromEntries(
              ['base','hair','hairLengths','headgear','extra'].filter(k=>p[k]).map(k=>[k,p[k]]));
          }
        }
      }
      const build = 'Feminine', hair = 'twin-braids';
      await choose({build,hair,headwear:'none',top:'open'});
      const tops = keys('top'), headwears = keys('headwear');
      for (const headwear of headwears) for (const top of tops) for (const hairColor of ['default','ombre']) {
        const p = await choose({build,hair,headwear,top,hairColor});
        twins[[headwear,top,hairColor].join('/')] = Object.fromEntries(
          ['base','top','headgear','hair','hairLengths'].filter(k=>p[k]).map(k=>[k,p[k]]));
      }
      return {hats,twins};
    },revision);
    fs.writeFileSync(output,JSON.stringify(selections,null,2)+'\n');
    console.log(Object.keys(selections.hats).length+' beanie fits and '+Object.keys(selections.twins).length+' braid assemblies');
  } finally {await browser.close();}
}
main().catch(error=>{console.error(error);process.exitCode=1;});
