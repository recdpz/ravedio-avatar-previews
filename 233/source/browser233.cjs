const fs=require('fs'),assert=require('assert');
const{chromium}=require('C:/Users/Ronnie/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const P='E:/Ravedio-Avatar/refinement233',url=process.argv.find(x=>/^https?:/.test(x))||'http://127.0.0.1:9228/233/';
(async()=>{
 const browser=await chromium.launch({executablePath:'C:/Users/Ronnie/AppData/Local/ms-playwright/chromium_headless_shell-1228/chrome-headless-shell-win64/chrome-headless-shell.exe',args:['--enable-webgl','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const errors=[],http=[],checks=[];
 try{
  const page=await browser.newPage({viewport:{width:430,height:950}});
  page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.status()>=400)http.push([r.status(),r.url()])});
  await page.goto(url);
  async function ready(){for(let i=0;i<180;i++){assert.deepEqual(errors,[]);if(await page.evaluate(()=>!!window.review233?.ready()))return;await page.waitForTimeout(300)}throw Error('Preview did not become ready')}
  await ready();
  for(const build of ['Feminine','Masculine']){
   await page.locator('#build').selectOption(build);await ready();await page.locator('#angle').selectOption('front');
   const baseline=await page.evaluate(()=>window.review233.inspect().geometry);
   for(const key of ['tapered','bean']){
    await page.locator('[data-eye="'+key+'"]').click();await ready();
    assert.equal(await page.locator('#eyes').inputValue(),key);assert.equal(await page.locator('#before232').isDisabled(),false);
    const current=await page.evaluate(()=>window.review233.inspect().geometry),state=await page.evaluate(()=>window.review233.state());
    await page.locator('#before232').check();await ready();
    const before=await page.evaluate(()=>window.review233.state()),old=await page.evaluate(()=>window.review233.inspect().geometry);
    assert(before.before232);assert(before.components.eyes.startsWith('../232/'));assert.deepEqual(before.features,state.features);assert.equal(before.yaw,state.yaw);assert.equal(before.zoom,state.zoom);assert.notDeepEqual(old.eyes,current.eyes);
    for(const k of Object.keys(current))if(k!=='eyes')assert.deepEqual(old[k],current[k]);
    assert((await page.locator('#status').innerText()).includes('previous 232'));
    await page.locator('#before232').uncheck();await ready();assert.deepEqual((await page.evaluate(()=>window.review233.inspect().geometry)).eyes,current.eyes);
    for(const tone of ['0','1','2','3']){
     await page.locator('#skin').selectOption(tone);await ready();const data=await page.locator('canvas').evaluate(c=>c.toDataURL());fs.writeFileSync(P+'/browser/'+build+'-'+key+'-tone'+tone+'.png',Buffer.from(data.split(',')[1],'base64'));
    }
    await page.locator('#skin').selectOption('1');await ready();
    const after=await page.evaluate(()=>window.review233.inspect().geometry);for(const k of Object.keys(baseline))if(k!=='eyes')assert.deepEqual(after[k],baseline[k]);
    checks.push(build+':'+key+':4 tones; before/after changes eyes only');
   }
   for(const key of ['original','almond','hooded','squint']){
    await page.locator('#eyes').selectOption(key);await ready();assert(await page.locator('#before232').isDisabled());assert(!(await page.locator('#before232').isChecked()));
   }
   assert.equal(await page.locator('#eyes option[value=soft]').count(),0);assert.equal(await page.locator('#eyes option[value=square]').count(),0);
   await page.waitForFunction(()=>['original','tapered','hooded','bean','squint'].every(k=>{const i=document.getElementById('compare-'+k);return i.complete&&i.naturalWidth>0}));
  }
  await page.locator('#build').selectOption('Feminine');await ready();await page.locator('[data-eye=tapered]').click();await ready();await page.screenshot({path:P+'/browser/mobile233.png'});
  const saved=await page.evaluate(()=>window.review233.state().features);await page.reload();await ready();assert.deepEqual(await page.evaluate(()=>window.review233.state().features),saved);
  await page.locator('#before232').check();await ready();const download=page.waitForEvent('download');await page.locator('#png').click();assert((await download).suggestedFilename().includes('before232'));await page.locator('#before232').uncheck();await ready();
  assert(!(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth)));assert.equal(await page.locator('canvas').count(),1);
  const flat=await browser.newPage({viewport:{width:800,height:190}});await flat.goto(new URL('references/outlines233.svg',url).href);await flat.screenshot({path:P+'/browser/outlines233.png'});await flat.close();
  assert.deepEqual(errors,[]);assert.deepEqual(http,[]);
  fs.writeFileSync(P+'/browser233'+(url.startsWith('https')?'-public':'')+'.json',JSON.stringify({url,checks,errors,http,beforeAfterChangesEyesOnly:true,otherEyeOptionsLoad:true,choicePersistence:true,pngVersionLabel:true,mobileLayout:true,flatOutlineCheck:true},null,2));
  console.log('233: contours, before/after controls, four tones, persistence and PNG verified.');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
