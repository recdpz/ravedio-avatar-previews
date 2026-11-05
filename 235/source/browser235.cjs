const fs=require('fs'),assert=require('assert');const{chromium}=require('C:/Users/Ronnie/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');const P='E:/Ravedio-Avatar/catalogue235',url=process.argv.find(x=>/^https?:/.test(x))||'http://127.0.0.1:9235/235/';fs.mkdirSync(P+'/browser',{recursive:true});
(async()=>{const browser=await chromium.launch({executablePath:'C:/Users/Ronnie/AppData/Local/ms-playwright/chromium_headless_shell-1228/chrome-headless-shell-win64/chrome-headless-shell.exe',args:['--enable-webgl','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});const errors=[],http=[],checks=[];try{
 const page=await browser.newPage({viewport:{width:750,height:950}});page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.status()>=400)http.push([r.status(),r.url()])});await page.goto(url);
 async function ready(){for(let i=0;i<240;i++){assert.deepEqual(errors,[]);if(await page.evaluate(()=>!!window.review235?.ready()))return;await page.waitForTimeout(200)}throw Error('Preview not ready')}
 const set=async(id,v)=>{await page.locator('#'+id).selectOption(v);await ready()};const shot=async(name)=>{const data=await page.locator('canvas').evaluate(c=>c.toDataURL());fs.writeFileSync(P+'/browser/'+name+'.png',Buffer.from(data.split(',')[1],'base64'))};await ready();
 assert(!(await page.locator('#detail option[value=gems]').count()));assert.equal(await page.locator('#frameColor option').count(),4);
 for(const build of ['Feminine','Masculine']){
  await set('build',build);const start=await page.evaluate(()=>window.review235.state());assert.equal(start.features.nose,'none');assert.equal(start.features.mouth,'line');
  await set('headwear','none');
  for(const eye of ['original','almond','tapered','hooded','bean','squint']){await set('eyes',eye);assert((await page.evaluate(()=>window.review235.state())).components.eyes);checks.push(build+':eye:'+eye)}
  const hairs=await page.locator('#hair option').evaluateAll(os=>os.map(o=>o.value));
  for(const hair of hairs){await set('hair',hair);assert.equal(await page.locator('#headwear option:disabled').count(),0);await set('detail','sprout');await set('angle','front');await shot(build+'-'+hair+'-front');await set('angle','profile');await shot(build+'-'+hair+'-profile');checks.push(build+':hair:'+hair)}
  await set('detail','none');await set('hair',build==='Feminine'?'ponytail':'taper');
  for(const style of ['rectangular','reading','wayfarer','cat-eye','heart','wraparound','kaleidoscope']){
   await set('glasses',style);assert.equal((await page.evaluate(()=>window.review235.state())).features.lensTint,style==='reading'?'clear':'dark');assert.deepEqual(await page.evaluate(()=>window.review235.inspect().transmission),[]);for(const tint of ['clear','dark']){await set('lensTint',tint);await set('angle','front');await shot(build+'-'+style+'-'+tint)}checks.push(build+':glasses:'+style)
  }
  await set('glasses','rectangular');for(const color of ['black','tortoise','silver','gold']){await set('frameColor',color);await shot(build+'-frames-'+color)}
  for(const tone of ['0','1','2','3']){await set('skin',tone);await shot(build+'-skin'+tone)}await set('skin','1');
  for(const hat of ['cap','beanie','bucket','cowboy','headband','ears','pashmina']){await set('headwear',hat);await set('detail','sprout');for(const angle of ['front','profile','rear']){await set('angle',angle);await shot(build+'-'+hat+'-'+angle)}checks.push(build+':hat:'+hat)}
  await set('headwear','none');await set('glasses','none');await set('detail','none');
  if(build==='Masculine')for(const style of ['taper','buzz','curly-top','afro','flow','locs','middle-part']){await set('hair',style);for(const color of ['black','blonde','pink']){await set('hairColor',color);await set('groom','short');await set('angle','threequarter');await shot(style+'-'+color)}await set('hairColor','default')}
 }
 await page.setViewportSize({width:430,height:950});assert(!(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth)));assert.equal(await page.locator('canvas').count(),1);const dl=page.waitForEvent('download');await page.locator('#save').click();assert((await dl).suggestedFilename().includes('235'));assert.deepEqual(errors,[]);assert.deepEqual(http,[]);fs.writeFileSync(P+'/browser235'+(url.startsWith('https')?'-public':'')+'.json',JSON.stringify({url,checks,errors,http,oneCanvas:true,mobileLayout:true},null,2));console.log('235 controls verified',checks.length)
 }finally{await browser.close()}})().catch(e=>{console.error(e);process.exit(1)});
