const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');

const origin = process.env.PREVIEW_ORIGIN || 'http://127.0.0.1:9251';
const out = process.env.CAPTURE_DIR;
const revision = Number(process.env.ART_REVISION || 291);
const fits = require('../../' + revision + '/hair-fits.json').Feminine['side-sweep'].fits;
const angles = ['front', 'threequarter', 'profile', 'rightprofile', 'rearquarter', 'rear', 'top', 'underside'];
const colors = ['default', 'black', 'darkbrown', 'auburn', 'blonde', 'platinum', 'pink', 'purple', 'ombre'];
const tops = ['bandeau', 'triangle', 'strappy', 'tshirt', 'jersey', 'open', 'tank', 'sweatshirt'];

async function select(page, rev, config) {
  return page.evaluate(async ({ rev, config }) => {
    const review = window['review' + rev];
    await review.set(config);
    const result = review.rendered();
    if (!review.ready() || review.errors.length) throw Error(review.errors.join('\n'));
    for (const [key, value] of Object.entries(config)) {
      const got = key === 'build' ? result.build : key === 'view' ? review.state().mode : result.features[key];
      if (got !== value) throw Error(key + ' became ' + got);
    }
    return result.components;
  }, { rev, config });
}

async function capture(page, name, angle, size = 512) {
  await page.locator('#angle').selectOption(angle);
  const uri = await page.evaluate(([rev, pixels]) => window['review' + rev].capture(pixels), [revision, size]);
  fs.writeFileSync(path.join(out, name + '-' + angle + '.png'), Buffer.from(uri.split(',')[1], 'base64'));
}

async function run() {
  if (!out) throw Error('Set CAPTURE_DIR for the review images');
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch({
    executablePath: process.env.CHROMIUM_PATH,
    headless: true,
    args: ['--use-angle=d3d11', '--ignore-gpu-blocklist'],
  });
  const failures = [];
  try {
    const page = await browser.newPage({ viewport: { width: 1150, height: 920 } });
    page.on('pageerror', e => failures.push(String(e)));
    page.on('response', r => { if (r.status() >= 400 && !r.url().endsWith('favicon.ico')) failures.push(r.url()); });
    const query = 'build=Feminine&hair=side-sweep&headwear=none&top=sweatshirt&bottom=pants&detail=none&glasses=none&skin=1&mode=face';
    await page.goto(origin + '/' + revision + '/?' + query);
    await page.waitForFunction(rev => window['review' + rev]?.ready(), revision);
    if (await page.locator('#hair option[value="side-sweep"]').textContent() !== 'Long Bangs') {
      throw Error('The selector is missing Long Bangs');
    }
    const common = {
      build: 'Feminine', hair: 'side-sweep', view: 'face', top: 'sweatshirt',
      bottom: 'pants', detail: 'none', glasses: 'none', skin: 1,
    };
    for (const [headwear, pair] of Object.entries(fits)) {
      for (const hairColor of ['default', 'ombre']) {
        const parts = await select(page, revision, { ...common, headwear, hairColor });
        const expected = new URL(pair[hairColor], origin + '/' + revision + '/').href;
        if (parts.hair !== expected) throw Error('Wrong asset for ' + headwear + ' ' + hairColor);
        const views = hairColor === 'default' ? angles : ['threequarter', 'rear'];
        for (const angle of views) await capture(page, headwear + '-' + hairColor, angle);
      }
    }
    const palettes = new Set();
    for (const hairColor of colors) {
      await select(page, revision, { ...common, headwear: 'none', hairColor, view: 'face' });
      const tint = await page.evaluate(rev => window['review' + rev].materials().find(m => m.slot === 'hair'), revision);
      if (hairColor !== 'default') palettes.add(JSON.stringify(tint.color));
      await capture(page, 'color-' + hairColor, 'threequarter');
      await select(page, revision, { ...common, headwear: 'none', hairColor, view: 'chat' });
      await capture(page, 'chat-' + hairColor, 'front', 120);
    }
    if (palettes.size !== colors.length - 1) throw Error('Duplicate hair tints in the selector');
    for (const top of tops) {
      await select(page, revision, { ...common, headwear: 'pashmina', hairColor: 'default', top, view: 'body' });
      for (const angle of ['threequarter', 'profile', 'rear']) await capture(page, 'scarf-' + top, angle);
    }
    for (const headwear of ['none', 'headband', 'pashmina']) {
      await select(page, revision, {
        ...common, headwear, hairColor: 'default', detail: 'sprout', glasses: 'reading', lensTint: 'clear',
      });
      await capture(page, 'detail-' + headwear, 'threequarter');
      await capture(page, 'detail-' + headwear, 'profile');
    }

    const before = await browser.newPage({ viewport: { width: 1150, height: 920 } });
    await before.goto(origin + '/280/');
    await before.waitForFunction(() => window.review280?.ready());
    const unrelated = [
      { build: 'Feminine', hair: 'space-buns', headwear: 'headband', hairColor: 'ombre' },
      { build: 'Feminine', hair: 'straight', headwear: 'none', hairColor: 'black' },
      { build: 'Masculine', hair: 'taper', headwear: 'headband', hairColor: 'black' },
    ];
    for (const config of unrelated) {
      const selection = { ...common, ...config };
      const a = await select(before, 280, selection);
      const b = await select(page, revision, selection);
      if (JSON.stringify(a) !== JSON.stringify(b)) throw Error('An unrelated asset changed for ' + config.hair);
    }
    await page.setViewportSize({ width: 390, height: 844 });
    await select(page, revision, { ...common, hair: 'ponytail', headwear: 'headband' });
    await page.locator('#hair').selectOption('side-sweep');
    await page.waitForFunction(rev => window['review' + rev].ready() && window['review' + rev].rendered().features.hair === 'side-sweep', revision);
    await page.locator('#show-cloth').uncheck();
    if (await page.evaluate(rev => window['review' + rev].inspect().visible.headgear, revision)) throw Error('Cloth toggle failed');
    await page.locator('#show-cloth').check();
    if (failures.length) throw Error(failures.join('\n'));
    fs.writeFileSync(path.join(out, 'browser.json'), JSON.stringify({
      revision, headwear: Object.keys(fits), defaultAngles: angles.length,
      ombreAngles: 2, colors, chatPortraitSize: 120, pashminaTops: tops,
      mobileSelectorAndClothToggle: true, unrelatedFitsCompared: unrelated.length,
    }, null, 2) + '\n');
    console.log('Checked 8 headwear states, 9 color states, all pashmina tops, and the mobile selector');
  } finally {
    await browser.close();
  }
}

run().catch(e => { console.error(e); process.exitCode = 1; });
