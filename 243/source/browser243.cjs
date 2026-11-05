const fs=require('fs'),assert=require('assert'),{chromium}=require('C:/Users/Ronnie/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const P='E:/Ravedio-Avatar/catalogue243',base='http://127.0.0.1:9243/243/';
(async()=>{const b=await chromium.launch({executablePath:'C:/Users/Ronnie/AppData/Local/ms-playwright/chromium_headless_shell-1228/chrome-headless-shell-win64/chrome-headless-shell.exe',args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});try{
const p=await b.newPage({viewport:{width:1300,height:1000}}),errors=[],http=[],checks=[];p.on('pageerror',e=>errors.push(e.message));p.on('response',r=>{if(r.status()>=400)http.push([r.status(),r.url()])});
await p.goto(base+'?build=Feminine&hair=ponytail&headwear=pashmina&top=open&angle=threequarter');const ready=()=>p.waitForFunction(()=>window.review243?.ready());await ready();const set=async(k,v)=>{await p.selectOption('#'+k,v);await ready()};
for(const build of ['Feminine','Masculine']){
 await set('build',build);await set('hair',build==='Feminine'?'ponytail':'taper');
 for(const top of await p.locator('#top option').evaluateAll(os=>os.map(o=>o.value))){await set('top',top);assert((await p.evaluate(()=>window.review243.state())).components.headgear.includes(build+'-'+top+'-pashmina243'));checks.push([build,top,'top route']);}
 await set('top',build==='Feminine'?'open':'tank');const after=await p.evaluate(()=>window.review243.inspect());await p.check('#previous');await ready();const before=await p.evaluate(()=>window.review243.inspect());for(const group of ['base','hair','eyes','mouth','top','bottom','groom','lashes'])assert.deepEqual(after.geometry[group],before.geometry[group]);assert.notDeepEqual(after.geometry.headgear,before.geometry.headgear);await p.uncheck('#previous');await ready();checks.push([build,'242 comparison protects neighbors']);
 for(const color of ['black','white']){await set('headgearColor',color);checks.push([build,color,'cloth color']);}await set('headgearColor','default');
 await set('glasses','rectangular');await set('lensTint','clear');assert.deepEqual(await p.evaluate(()=>window.review243.inspect().transmission),[]);await set('glasses','none');checks.push([build,'clear glasses']);
}
await p.setViewportSize({width:430,height:950});await p.waitForTimeout(100);assert.equal(await p.locator('canvas').count(),1);assert(!(await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth)));assert.deepEqual(errors,[]);assert.deepEqual(http,[]);
fs.writeFileSync(P+'/browser243.json',JSON.stringify({checks,errors,http,oneCanvas:true,mobileLayout:true},null,2));console.log('BROWSER243',checks.length,'checks; no loading errors; comparison and mobile layout passed');
}finally{await b.close()}})().catch(e=>{console.error(e);process.exit(1)});
