const fs=require("node:fs");
const {chromium}=require(process.env.PLAYWRIGHT_MODULE || "playwright");
const revision = process.env.ART_REVISION || "299";
const origin = process.env.PREVIEW_ORIGIN || "http://127.0.0.1:9251";
async function run(){
  const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH,args:["--use-angle=d3d11","--ignore-gpu-blocklist"]});
  try{
    const page=await browser.newPage();
    await page.goto(origin+"/"+revision+"/");
    await page.waitForFunction(r=>window["review"+r]?.ready(),revision);
    const rows=[];
    for(const build of ["Feminine","Masculine"]){
      await page.evaluate(([r,build])=>window["review"+r].set({build,headwear:"pashmina"}),[revision,build]);
      const hairs=await page.locator("#hair option").evaluateAll(list=>list.map(o=>o.value));
      const tops=await page.locator("#top option").evaluateAll(list=>list.map(o=>o.value));
      for(const hair of hairs){
        for(const top of tops){
          const features={build,hair,top,headwear:"pashmina",skin:1,hairColor:"default",headgearColor:"default",bottom:"pants",view:"body",groom:"none",glasses:"none",detail:"none"};
          const r=await page.evaluate(async ([r,state])=>{
            const review=window["review"+r];await review.set(state);
            if(!review.ready()||review.errors.length)throw Error(review.errors.join("\n"));
            return review.rendered();
          },[revision,features]);
          if(r.build!==build||r.features.hair!==hair||r.features.top!==top||r.features.headwear!=="pashmina")throw Error(JSON.stringify(r));
          rows.push({revision,build,hair,top,headgearColor:"default",parts:r.components});
        }
        console.log(build,hair);
      }
    }
    fs.writeFileSync(process.argv[2],JSON.stringify(rows,null,2)+"\n");
  }finally{await browser.close()}
}
run().catch(error=>{console.error(error);process.exitCode=1});
