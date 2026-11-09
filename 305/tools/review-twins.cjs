const fs = require("node:fs");
const path = require("node:path");
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || "playwright");
const out = process.env.CAPTURE_DIR;
if (!out) throw Error("Set CAPTURE_DIR");
fs.mkdirSync(out, { recursive: true });
const cases = [
  ["305","Feminine","twin-braids","open"],
  ["305","Feminine","twin-braids","tank"],
  ["305","Feminine","twin-braids","sweatshirt"],
  ["305","Feminine","twin-braids","triangle"],
  ["305","Feminine","twin-braids","jersey"],
  ["305","Feminine","twin-braids","bandeau"],
  ["305","Feminine","twin-braids","strappy"],
  ["305","Feminine","twin-braids","tshirt"],
];
const style = process.argv[2];
const selectedCases = style ? cases.filter(row => row[2] === style) : cases;
if (!selectedCases.length) throw Error("Unknown hairstyle: " + style);
const angles = ["front","threequarter","profile","rightprofile","rearquarter","rear","top","underside","lowrear","lowquarter"];
const origin = process.env.PREVIEW_ORIGIN || "http://127.0.0.1:9251";

async function run() {
  const browser = await chromium.launch({executablePath:process.env.CHROMIUM_PATH,
    args:["--use-angle=d3d11","--ignore-gpu-blocklist"]});
  try {
    const page = await browser.newPage({viewport:{width:1150,height:900}});
    const errors = [];
    page.on("pageerror", e=>errors.push(String(e)));
    await page.route("**/270/viewer.js", async route=>{
      const response = await route.fetch();
      let js = await response.text();
      // Isolated camera crop for diagnosis. No art or lighting overrides.
      js = js.replace("/zoom,y=mode==='chat'?1.90:mode==='face'?1.88:1.28",
        "/zoom,y=mode==='chat'?1.90:mode==='face'?1.88:1.40");
      js = js.replace("mode==='face'?1.5:2.7","mode==='face'?1.5:1.06");
      js = js.replace("angle==='underside'?-1.05:0","angle==='underside'?-.42:0");
      js = js.replace("rearquarter:-2.498,front","lowrear:Math.PI,lowquarter:-2.498,rearquarter:-2.498,front");
      js = js.replace("angle==='underside'?-.42:0","['lowrear','lowquarter','underside'].includes(angle)?-.40:0");
      js = js.replace("  capture: size => {", `  isolateHair: hidden => {
        root?.traverse(o => {if(o.isMesh && ['hair','hairLengths'].includes(o.userData.slot263)) o.visible = !hidden});
        draw();
      },
      capture: size => {`);
      await route.fulfill({response,body:js});
    });
    const rows = [];
    let active;
    for (const [revision,build,hair,top] of selectedCases) {
      if(active!==revision){
        await page.goto(origin+"/"+revision+"/?build=Feminine&hair=curls");
        await page.waitForFunction(r=>window["review"+r]?.ready(),revision);
        active=revision;
      }
      for (const headgearColor of ["bare","khaki"]) {
        const features={build,hair,top,headwear:headgearColor==="bare"?"none":"pashmina",skin:1,
          hairColor:"default",headgearColor:headgearColor==="bare"?"default":headgearColor,bottom:"pants",view:"body",groom:"none",
          glasses:"none",detail:"none"};
        const result = await page.evaluate(async ([r,state])=>{
          const review=window["review"+r];
          await review.set(state);
          if(!review.ready() || review.errors.length) throw Error(review.errors.join("\n"));
          return review.rendered();
        },[revision,features]);
        if(result.features.hair!==hair || result.features.top!==top) throw Error("Wrong assembly");
        rows.push({revision,build,hair,top,headgearColor,parts:result.components});
        await page.locator("#angle").evaluate(select=>{for(const name of ["lowrear","lowquarter"])if(![...select.options].some(o=>o.value===name))select.add(new Option(name,name));});
        for(const angle of angles){
          await page.locator("#angle").selectOption(angle);
          const img=await page.evaluate(r=>window["review"+r].capture(820),revision);
          const name=[revision,build,hair,top,headgearColor,angle,"full"].join("-");
          fs.writeFileSync(path.join(out,name+".png"),Buffer.from(img.split(",")[1],"base64"));
          if(headgearColor==="khaki"&&["front","threequarter","rightprofile","underside","lowrear","lowquarter"].includes(angle)){
            const isolated=await page.evaluate(r=>{
              const review=window["review"+r];
              review.isolateHair(true);
              const img=review.capture(820);
              review.isolateHair(false);
              return img;
            },revision);
            fs.writeFileSync(path.join(out,name.replace(/full$/,"hair-hidden")+".png"),Buffer.from(isolated.split(",")[1],"base64"));
          }
        }
      }
      console.log(revision,build,hair,top);
    }
    if(errors.length) throw Error(errors.join("\n"));
    fs.writeFileSync(path.join(out,"audit.json"),JSON.stringify(rows,null,2));
  } finally {await browser.close();}
}
run().catch(e=>{console.error(e);process.exitCode=1});
