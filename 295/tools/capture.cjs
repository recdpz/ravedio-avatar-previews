const fs = require("node:fs");
const path = require("node:path");
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || "playwright");
const revision = process.env.ART_REVISION || "294";
const origin = process.env.PREVIEW_ORIGIN || "http://127.0.0.1:9251";
const output = process.env.CAPTURE_DIR;
const angles = ["front","threequarter","profile","rightprofile","rearquarter","rear","top","underside"];
const args = process.argv.slice(2);
const fixturesOnly = args.includes("--fixtures-only");
const styles = new Set(args);
const feminineTops = ["tank","open","sweatshirt"];

const phoneFixtures = {
  Feminine: {
    hair: "curls", headwear: "pashmina", top: "open", bottom: "pants", eyes: "hooded",
    groom: "none", glasses: "reading", frameColor: "black", lensTint: "clear", detail: "hot",
  },
  Masculine: {
    hair: "flow", headwear: "cap", top: "sweatshirt", bottom: "pants", eyes: "bean",
    groom: "short", glasses: "wayfarer", frameColor: "black", lensTint: "dark", detail: "hot",
  },
};

async function run() {
  if(!output) throw Error("Set CAPTURE_DIR");
  fs.mkdirSync(output,{recursive:true});
  const browser=await chromium.launch({
    executablePath: process.env.CHROMIUM_PATH, headless: true,
    args:["--use-angle=d3d11","--ignore-gpu-blocklist"],
  });
  try {
    const page=await browser.newPage({viewport:{width:1100,height:900}});
    const failures=[];
    page.on("pageerror",error=>failures.push(String(error)));
    page.on("response",response=>{
      if(response.status()>=400&&!response.url().endsWith("favicon.ico"))failures.push(response.url());
    });
    await page.goto(origin+"/"+revision+"/?build=Feminine&hair=curls&headwear=pashmina&mode=face");
    await page.waitForFunction(rev=>window["review"+rev]?.ready(),revision);
    async function choose(config) {
      return page.evaluate(async([rev,config])=>{
        const review=window["review"+rev];
        await review.set(config);
        if(!review.ready()||review.errors.length)throw Error(review.errors.join("\n"));
        const result=review.rendered();
        for(const [key,value] of Object.entries(config)) {
          const actual=key==="build"?result.build:key==="view"?review.state().mode:result.features[key];
          if(actual!==value)throw Error(key+" resolved to "+actual+" instead of "+value);
        }
        return result;
      },[revision,config]);
    }
    async function capture(name, angle, size=480) {
      await page.locator("#angle").selectOption(angle);
      const uri=await page.evaluate(([rev,size])=>window["review"+rev].capture(size),[revision,size]);
      fs.writeFileSync(path.join(output,name+"-"+angle+".png"),Buffer.from(uri.split(",")[1],"base64"));
    }
    const rows=[];
    for(const build of fixturesOnly ? [] : ["Feminine","Masculine"]) {
      await choose({build,headwear:"none"});
      const picks=await page.locator("#hair option").evaluateAll(options=>options.map(o=>[o.value,o.textContent]));
      const topKeys=await page.locator("#top option").evaluateAll(options=>options.map(o=>o.value));
      for(const [hair,label] of picks) {
        if(styles.size&&!styles.has(hair))continue;
        const primary=build==="Feminine"&&["curls","straight","box-braids","twin-braids"].includes(hair);
        const tops=primary?topKeys:build==="Feminine"?feminineTops:
          ["flow","locs","middle-part","afro"].includes(hair)?["tank","buttonup","sweatshirt"]:["tank"];
        for(const top of tops) {
          for(const hairColor of ["default","ombre"]) {
            const result=await choose({build,hair,headwear:"pashmina",top,hairColor,view:"body",
              bottom:"pants",groom:"none",detail:"none",glasses:"none",skin:1});
            rows.push({build,hair,label,top,hairColor,parts:result.components});
          }
          const name=[build,hair,top].join("-");
          await choose({build,hair,headwear:"pashmina",top,hairColor:"default",view:"face"});
          for(const angle of angles)await capture(name,angle);
          if(primary || top==="open" || top==="sweatshirt") {
            await page.locator("#body").click();
            for(const angle of ["front","threequarter","profile","rightprofile","rear"])await capture(name+"-body",angle);
          }
        }
        console.log(build+" "+label);
      }
    }
    const fixtures={};
    for(const [build,features] of Object.entries(phoneFixtures)) {
      const result=await choose({build,...features,hairColor:"default",headgearColor:"default",
        topColor:"default",bottomColor:"default",skin:1,view:"body"});
      fixtures[build]={features:result.features,parts:result.components};
      for(const angle of angles)await capture("fixture-"+build+"-body",angle);
      await page.locator("#face").click();
      for(const angle of ["rightprofile","rear"]) await capture("fixture-"+build+"-fit",angle,512);
      for(const skin of [0,3]) {
        await choose({build,skin,view:"chat"});
        for(const size of [48,64,120,512])await capture("fixture-"+build+"-skin"+skin+"-"+size,"front",size);
      }
    }
    if(failures.length)throw Error(failures.join("\n"));
    fs.writeFileSync(path.join(output,"review.json"),JSON.stringify({revision,rows,fixtures},null,2)+"\n");
  } finally {await browser.close();}
}
run().catch(error=>{console.error(error);process.exitCode=1});