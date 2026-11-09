const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const out = process.env.CAPTURE_DIR;
const origin = process.env.PREVIEW_ORIGIN || 'http://127.0.0.1:9251';
const revisions = process.argv.slice(2).map(Number);
const angles = ['front', 'threequarter', 'profile', 'rightprofile', 'rear', 'rearquarter', 'top', 'underside'];
const styles = {
  Feminine: ['bob','ponytail','straight','curls','side-sweep','space-buns','twin-braids','box-braids'],
  Masculine: ['sidepart','taper','buzz','curly-top','afro','flow','locs','middle-part'],
};
const common = { headwear:'beanie', view:'face', hairColor:'default', glasses:'none', detail:'none', skin:3, headgearColor:'default', groom:'none' };

async function main() {
  fs.mkdirSync(out, {recursive:true});
  const browser = await chromium.launch({executablePath:process.env.CHROMIUM_PATH,
    args:['--use-angle=d3d11','--ignore-gpu-blocklist']});
  try {
    const page = await browser.newPage({viewport:{width:820,height:680}});
    const faults = [];
    page.on('pageerror', e => faults.push(e.message));
    page.on('response', r => {if (r.status() >= 400) faults.push(r.status()+' '+r.url());});
    const baseline = new Map();
    function compare(revision, key, parts, expectedChanges) {
      if (revision === 308) {
        baseline.set(key,parts);
        return;
      }
      const before = baseline.get(key);
      if (!before) return;
      const uri = value => value && new URL(value,origin+'/308/').pathname;
      const roles = new Set([...Object.keys(before),...Object.keys(parts)]);
      const changed = [...roles].filter(role => uri(before[role]) !== uri(parts[role])).sort();
      assert.deepEqual(changed, [...expectedChanges].sort(), key);
    }
    for (const revision of revisions) {
      await page.goto(origin+'/'+revision+'/?build=Feminine&hair=ponytail&headwear=beanie&mode=face');
      await page.waitForFunction(r => window['review'+r]?.ready(),revision);
      async function choose(selection) {
        const result = await page.evaluate(async ([rev, selection]) => {
          const review = window['review'+rev];
          await review.set(selection);
          if (!review.ready() || review.errors.length) throw Error(review.errors.join('\n'));
          return {render:review.rendered(), state:review.state()};
        }, [revision, selection]);
        for (const [key, value] of Object.entries(selection)) {
          if (key === 'angle') assert.equal(result.state.angle, value);
          else if (key === 'view') assert.equal(result.state.mode, value);
          else if (key === 'build') assert.equal(result.render.build, value);
          else assert.equal(result.render.features[key], value, key);
        }
        return result.render.components;
      }
      async function capture(key, size) {
        const png = await page.evaluate(([r,s]) => window['review'+r].capture(s),[revision,size]);
        fs.writeFileSync(path.join(out,revision+'-'+key+'.png'), Buffer.from(png.split(',')[1],'base64'));
      }
      for (const [build, hairs] of Object.entries(styles)) {
        for (const hair of hairs) {
          const top = build==='Feminine'?'jersey':'tank';
          const p = await choose({...common, build, hair, top});
          if (revision===309) assert(new URL(p.headgear).pathname.startsWith('/309/assets/'));
          const changes = ['headgear','eyes','mouth'];
          if (hair==='ponytail') changes.push('hairLengths');
          compare(revision,hair,p,changes);
          for (const angle of angles) {
            await page.locator('#angle').selectOption(angle);
            await capture([hair,angle].join('-'), 384);
          }
          if (revision===309) {
            const combo = await choose({...common, build, hair, top, hairColor:'ombre',
              headgearColor:'black', detail:'sprout', angle:'rearquarter'});
            assert(new URL(combo.extra).pathname.startsWith('/309/assets/'));
            assert.equal(combo.headgear, p.headgear);
            await capture(hair+'-sprout', 384);
          }
          console.log(revision+' '+hair);
        }
      }
      for (const hairColor of ['default','ombre']) {
        const pony = { ...common, build:'Feminine', hair:'ponytail', hairColor, top:'sweatshirt',
          angle:'rearquarter' };
        compare(revision,'bare-ponytail-'+hairColor,await choose({...pony,headwear:'none'}),['eyes','mouth']);
        const hoodie = await choose(pony);
        compare(revision,'hoodie-ponytail-'+hairColor,hoodie,['eyes','mouth','hairLengths','headgear']);
        await capture('hoodie-ponytail-'+hairColor,384);
      }
      for (const [build, hair, top] of [['Feminine','ponytail','jersey'],['Masculine','flow','tank']]) {
        for (const eyes of ['original','tapered','hooded','bean']) {
          for (const glasses of eyes==='original' ? ['none','reading','wayfarer'] : ['none']) {
            const lensTint = glasses==='reading' ? 'clear' : 'dark';
            const p = await choose({...common, build, hair, top, eyes, glasses, lensTint,
              headgearColor:'default', detail:'none', angle:'front', view:'chat'});
            if (revision===309) {
              assert(new URL(p.eyes).pathname.startsWith('/309/assets/'));
              assert(new URL(p.mouth).pathname.startsWith('/309/assets/'));
              if (glasses!=='none') {
                const lenses = await page.evaluate(() => review309.materials().filter(m => m.slot==='lenses'));
                assert(lenses.length && lenses.every(m => m.opacity === (lensTint==='clear' ? .075 : .74) && m.transmission===0));
              }
            }
            for (const size of [48,64]) await capture([hair,eyes,glasses,size].join('-'), size);
          }
        }
      }
    }
    assert.deepEqual(faults, []);
  } finally { await browser.close(); }
}

main().catch(error => { console.error(error); process.exitCode=1; });
