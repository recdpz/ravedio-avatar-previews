const fs = require("node:fs");
const path = require("node:path");
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || "playwright");
const revision = process.env.ART_REVISION;
const output = process.env.CAPTURE_DIR;
const styles = ["curls", "straight"];
const hats = ["none", "pashmina", "cap", "beanie", "bucket", "cowboy", "headband", "ears"];
const angles = ["front", "threequarter", "profile", "rightprofile", "rearquarter", "rear", "top", "underside"];
const base = process.env.PREVIEW_ORIGIN || "http://127.0.0.1:9251";

async function run() {
  fs.mkdirSync(output, {recursive:true});
  const browser = await chromium.launch({executablePath:process.env.CHROMIUM_PATH,
    args:["--use-angle=d3d11","--ignore-gpu-blocklist"]});
  try {
    const page = await browser.newPage({viewport:{width:1100,height:900}});
    const errors = [];
    page.on("pageerror", e => errors.push(String(e)));
    page.on("response", r => {if(r.status()>=400 && !r.url().endsWith("favicon.ico")) errors.push(r.url());});
    await page.goto(base + "/" + revision + "/?build=Feminine&hair=curls&mode=face");
    await page.waitForFunction(r => window["review"+r]?.ready(), revision);
    const rows = [];
    for (const hair of styles) {
      for (const headwear of hats) {
        for (const top of headwear === "pashmina" ? ["open","tank","sweatshirt","bandeau","triangle","strappy","tshirt","jersey"] : ["open"]) {
          for (const hairColor of ["default","ombre"]) {
            const features = {build:"Feminine", hair, headwear, top, hairColor, view:"face",
              bottom:"pants", detail:"none", glasses:"none", skin:1};
            const result = await page.evaluate(async ([r, state]) => {
              const review = window["review"+r];
              await review.set(state);
              if (!review.ready() || review.errors.length) throw Error(review.errors.join("\n"));
              return review.rendered();
            }, [revision, features]);
            for (const key of ["hair","headwear","top","hairColor"])
              if (result.features[key] !== features[key]) throw Error("Wrong " + key);
            rows.push({hair,headwear,top,hairColor,parts:result.components});
            for (const cloth of headwear === "pashmina" ? [true,false] : [true]) {
              if (!cloth) await page.locator("#show-cloth").uncheck();
              const chosen = hairColor === "ombre" ? ["threequarter","rear"] :
                ["none","pashmina","headband"].includes(headwear) ? angles : ["threequarter","rightprofile","rear"];
              for (const angle of chosen) {
                await page.locator("#angle").selectOption(angle);
                const data = await page.evaluate(r => window["review"+r].capture(480), revision);
                const name = [hair,headwear,top,hairColor,cloth?"visible":"hidden",angle].join("-");
                fs.writeFileSync(path.join(output,name+".png"),Buffer.from(data.split(",")[1],"base64"));
              }
              if (!cloth) {
                const shown = await page.evaluate(r => window["review"+r].inspect().visible, revision);
                if (shown.headgear || !shown.hair) throw Error("Cloth toggle should leave the fitted hair visible");
                await page.locator("#show-cloth").check();
              }
            }
          }
        }
      }
      console.log(hair);
    }
    if(errors.length) throw Error(errors.join("\n"));
    fs.writeFileSync(path.join(output,"review.json"), JSON.stringify({revision,rows},null,2)+"\n");
  } finally { await browser.close(); }
}
run().catch(error=>{console.error(error);process.exitCode=1});
