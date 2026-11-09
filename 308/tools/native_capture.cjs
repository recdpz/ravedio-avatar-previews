const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || "playwright");

const origin = process.env.PREVIEW_ORIGIN || "http://127.0.0.1:9251";
const out = process.env.CAPTURE_DIR;
const cases = [
  ["r308-curls-pashmina", "Feminine", {hair:"curls",headwear:"pashmina",top:"open",eyes:"hooded",glasses:"reading",lensTint:"clear",detail:"hot"}],
  ["r308-flow-cap", "Masculine", {hair:"flow",headwear:"cap",top:"sweatshirt",eyes:"bean",groom:"short",glasses:"wayfarer",lensTint:"dark",detail:"hot"}],
  ["r308-twin-jersey-pashmina", "Feminine", {hair:"twin-braids",headwear:"pashmina",top:"jersey"}],
  ["r308-ponytail-beanie-jersey", "Feminine", {hair:"ponytail",hairColor:"ombre",headwear:"beanie",top:"jersey",topColor:"white"}],
];

function matrix() {
  const rows = {};
  const grooms = {};
  for (const [build, spec] of Object.entries(catalogue.builds)) {
    for (const hair of Object.keys(spec.hair))
      for (const headwear of Object.keys(catalogue.headwear)) {
        if (!compatible(build,hair,headwear)) continue;
        for (const top of Object.keys(spec.tops))
          for (const finish of ["default","ombre"]) {
            const selection = sanitize(build,{hair,headwear,top,hairColor:finish,
              detail:"sprout",bottom:"pants",groom:"none"});
            const p = assembledPaths(selection,build);
            rows[[build,hair,headwear,top,finish].join("/")] = Object.fromEntries(
              ["hair","hairLengths","headgear","top","extra"].map(role => [role,p[role] ?? null]));
          }
      }
    for (const groom of Object.keys(spec.grooms))
      grooms[[build,groom].join("/")] = assembledPaths(sanitize(build,{groom}),build).groom ?? null;
  }
  return {rows,grooms,colors:catalogue.colors, aliases:catalogue.colorAliases,
    sourceURLs: [manifestUrl,bandanaUrl,hairUrl,pashminaUrl,materialUrl,wardrobeUrl].filter(Boolean).map(String)};
}

async function run() {
  assert(out, "Set CAPTURE_DIR");
  fs.mkdirSync(out,{recursive:true});
  const browser = await chromium.launch({executablePath:process.env.CHROMIUM_PATH,
    args:["--use-angle=d3d11","--ignore-gpu-blocklist"]});
  try {
    const page = await browser.newPage({viewport:{width:1080,height:860}});
    const errors = [];
    page.on("pageerror", e=>errors.push(String(e)));
    page.on("response", r=>{if(r.status()>=400 && !r.url().endsWith("favicon.ico")) errors.push(r.status()+" "+r.url());});
    await page.route("**/270/viewer.js", async route=>{
      const response=await route.fetch();
      const js=await response.text();
      const anchor="  capture: size => {";
      assert(js.includes(anchor));
      await route.fulfill({response,body:js.replace(anchor,"  nativeMatrix: "+matrix.toString()+",\n"+anchor)});
    });

    const matrices={};
    for (const revision of [298,308]) {
      await page.goto(origin+"/"+revision+"/?build=Feminine&top=jersey");
      try {
        await page.waitForFunction(r=>window["review"+r]?.ready(),revision,{timeout:10000});
      } catch (e) {
        throw Error("Preview "+revision+": "+errors.join("\n")+"\n"+(await page.locator("#status").textContent()));
      }
      matrices[revision]=await page.evaluate(r=>window["review"+r].nativeMatrix(),revision);
    }
    fs.writeFileSync(path.join(out,"selectors.json"),JSON.stringify(matrices)+"\n");
    console.log("Resolved",Object.keys(matrices[308].rows).length,"selector rows per revision");

    async function choose(state) {
      return page.evaluate(async state=>{
        const r=window.review308;
        await r.set(state);
        if(!r.ready() || r.errors.length) throw Error(r.errors.join("\n"));
        const value=r.rendered();
        for (const [key,want] of Object.entries(state)) {
          const actual=key==="build"?value.build:key==="view"?r.state().mode:value.features[key];
          if(actual!==want) throw Error(key+" "+actual+" != "+want);
        }
        return value;
      },state);
    }
    async function capture(name, angle, size) {
      await page.locator("#angle").selectOption(angle);
      const data=await page.evaluate(size=>window.review308.capture(size),size);
      fs.writeFileSync(path.join(out,name+"-web.png"),Buffer.from(data.split(",")[1],"base64"));
    }

    const fixtures={};
    for(const [id,build,config] of cases){
      const base={build,hairColor:"default",headgearColor:"default",topColor:"default",
        bottomColor:"default",bottom:"pants",eyes:"original",groom:"none",glasses:"none",
        detail:"none",frameColor:"black",lensTint:"dark",...config};
      const result=await choose({...base,skin:1,view:"face"});
      fixtures[id]={build,features:result.features,parts:result.components};
      for (const angle of ["rightprofile","rear"]) await capture(id+"-"+angle+"-skin1-512",angle,512);
      if (config.top==="jersey") {
        await page.locator("#body").click();
        for (const angle of ["front","threequarter","rear"]) await capture(id+"-body-"+angle+"-skin1-768",angle,768);
      }
      for (const skin of [0,1,2,3]) {
        const result=await choose({...base,skin,view:"chat"});
        assert.deepEqual(result.components,fixtures[id].parts);
        for(const size of [48,64,120,512]) await capture(id+"-front-skin"+skin+"-"+size,"front",size);
      }
      console.log(id,"captured");
    }
    assert.deepEqual(errors,[]);
    fs.writeFileSync(path.join(out,"fixtures.json"),JSON.stringify(fixtures,null,2)+"\n");
  } finally {
    await browser.close();
  }
}
run().catch(e=>{console.error(e);process.exitCode=1});
