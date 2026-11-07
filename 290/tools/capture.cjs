const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');

const origin = process.env.PREVIEW_ORIGIN || 'http://127.0.0.1:9251';
const views = [
  ['front', 'face', 512], ['threequarter', 'face', 512], ['profile', 'face', 512],
  ['rightprofile', 'face', 512], ['top', 'face', 512], ['rearquarter', 'face', 512],
  ['rear', 'face', 512], ['underside', 'face', 512],
  ['front', 'chat', 120], ['profile', 'chat', 120],
];

async function main() {
  const study = 'long';
  const revision = '290';

  const output = process.env.CAPTURE_OUTPUT || path.join(__dirname, '../views');
  const browser = await chromium.launch({
    executablePath: process.env.CHROMIUM_PATH,
    headless: true,
    args: ['--use-angle=d3d11', '--ignore-gpu-blocklist'],
  });
  const errors = [];
  try {
    fs.mkdirSync(output, { recursive: true });
    const page = await browser.newPage({ viewport: { width: 1100, height: 940 } });
    page.on('pageerror', error => errors.push(String(error)));
    page.on('response', response => {
      if (response.status() >= 400 && !response.url().endsWith('favicon.ico')) {
        errors.push(response.url());
      }
    });
    const query = new URLSearchParams({
      build: 'Feminine', hair: 'side-sweep', headwear: 'none',
      hairColor: 'default', skin: '1', top: process.env.CAPTURE_TOP || 'sweatshirt', bottom: 'pants', detail: 'none',
      glasses: 'none', mode: 'face', angle: 'front',
    });
    await page.goto(origin + '/' + revision + '/render.html?' + query);
    await page.waitForFunction(rev => window['review' + rev]?.ready(), revision);
    const hair = await page.evaluate(rev => window['review' + rev].rendered().components.hair, revision);
    if (new URL(hair).pathname !== '/' + revision + '/assets/' + study + '.glb') {
      throw Error('Wrong hair asset ' + hair);
    }
    for (const [angle, mode, size] of views) {
      await page.locator('#' + mode).click();
      await page.locator('#angle').selectOption(angle);
      const image = await page.evaluate(
        ({ revision, size }) => window['review' + revision].capture(size), { revision, size });
      fs.writeFileSync(path.join(output, study + '-' + mode + '-' + angle + '.png'),
        Buffer.from(image.split(',')[1], 'base64'));
    }
    if (errors.length) throw Error(errors.join('\n'));
    console.log('Captured ' + views.length + ' matched views for ' + study);
  } finally {
    await browser.close();
  }
}

main().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
