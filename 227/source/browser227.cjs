const fs=require('fs'),assert=require('assert');
const {chromium}=require('C:/Users/Ronnie/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const P='E:/Ravedio-Avatar/catalogue226/revision227',url=process.argv.find(x=>/^https?:/.test(x))||'http://127.0.0.1:9227/227/';
(async()=>{
 const browser=await chromium.launch({executablePath:'C:/Users/Ronnie/AppData/Local/ms-playwright/chromium_headless_shell-1228/chrome-headless-shell-win64/chrome-headless-shell.exe',args:['--enable-webgl','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const errors=[],http=[],cases=[],folder=P+'/browser';fs.mkdirSync(folder,{recursive:true});
 try{
  const page=await browser.newPage({viewport:{width:430,height:950}});page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.status()>=400)http.push([r.status(),r.url()])});
  await page.goto(url,{waitUntil:'networkidle'});
  const wait=()=>page.waitForFunction(()=>window.review227?.ready()&&!document.querySelector('#png').disabled,null,{timeout:90000});await wait();
  const select=async(id,v)=>{await page.locator('#'+id).selectOption(v);await wait()},inspect=()=>page.evaluate(()=>window.review227.inspect());
  const keys=await page.locator('#look option').evaluateAll(os=>os.map(o=>o.value));
  for(const key of keys){
   await select('look',key);const original=await inspect();assert.equal(original.morphs,0);assert.equal(original.parameterNodes,0);
   for(const angle of ['front','profile','rear','top']){
    await select('angle',angle);await page.waitForTimeout(60);
    const data=await page.locator('canvas').evaluate(c=>c.toDataURL());fs.writeFileSync(folder+'/'+key+'-'+angle+'.png',Buffer.from(data.split(',')[1],'base64'));
   }
   for(const tone of ['0','3','1']){await select('skin',tone);assert.deepEqual((await inspect()).geometry,original.geometry)}
   for(const group of ['hair','headgear','glasses','lenses','extra'])if(!await page.locator('#show-'+group).isDisabled()){
    await page.locator('#show-'+group).uncheck();assert.equal((await inspect()).visibleGroups[group]||0,0);await page.locator('#show-'+group).check();
   }
   const size=await page.evaluate(()=>window.review227.cacheSize());assert(size<=12,size);cases.push({key,meshes:Object.values(original.groups).reduce((a,b)=>a+b,0),transmission:original.transmitting,cache:size});
   console.log('BROWSER227',key);
  }
  await page.locator('#body').click();await page.locator('#face').click();await select('angle','front');
  const png=page.waitForEvent('download');await page.locator('#png').click();assert((await png).suggestedFilename().endsWith('.png'));
  const json=page.waitForEvent('download');await page.locator('#save-view').click();const saved=JSON.parse(fs.readFileSync(await(await json).path()));assert.equal(saved.revision,227);
  assert.equal(await page.locator('canvas').count(),1);assert.equal(await page.locator('#lighting').count(),0);assert(!(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth)));
  assert.deepEqual(await page.evaluate(()=>window.review227.errors),[]);assert.deepEqual(errors,[]);assert.deepEqual(http,[]);
  fs.writeFileSync(P+'/browser-proof227.json',JSON.stringify({url,cases,errors,http,checked:['all selectors','four camera angles','light and dark tones preserve geometry','separate visibility controls','bounded component cache','PNG download','saved view','mobile-width layout','fixed lighting'],not_checked:['native app','phone GPU','browser-Blender fidelity acceptance']},null,2));
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
