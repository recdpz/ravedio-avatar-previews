const fs = require("node:fs");
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || "playwright");
const revision = process.env.ART_REVISION || "307";
const origin = process.env.PREVIEW_ORIGIN || "http://127.0.0.1:9251";
async function run() {
  const browser = await chromium.launch({executablePath:process.env.CHROMIUM_PATH, args:["--use-angle=d3d11","--ignore-gpu-blocklist"]});
  try {
    const page = await browser.newPage({viewport:{width:1050,height:850}});
    await page.goto(origin + "/" + revision + "/");
    await page.waitForFunction(r => window["review"+r]?.ready(), revision);
    const rows = await page.evaluate(async r => {
      const review = window["review"+r];
      async function choose(state) {
        await review.set(state);
        if (!review.ready() || review.errors.length) throw Error(review.errors.join("\n"));
        const {build, features, components} = review.rendered();
        return {build, features, components};
      }
      function keys(field) { return Array.from(document.getElementById(field).options).filter(o => !o.disabled).map(o => o.value); }
      const receipts = [];
      for (const build of ["Feminine"]) {
        await choose({build,headwear:"none",view:"face",groom:"none",hairColor:"default",glasses:"none",detail:"none"});
        for (const hair of keys("hair").filter(value=>["box-braids","twin-braids","ponytail"].includes(value))) {
          await choose({build,hair,headwear:"none"});
          for (const headwear of keys("headwear")) {
            for (const hairColor of ["default","ombre"]) {
              const tops = hair === "twin-braids" || (hair === "box-braids" && ["pashmina","none"].includes(headwear)) ? keys("top") : ["open"];
              for (const top of tops) receipts.push(await choose({build,hair,headwear,hairColor,top}));
            }
          }
        }
      }
      return receipts;
    }, revision);
    fs.writeFileSync(process.argv[2], JSON.stringify(rows,null,2)+"\n");
    console.log("Resolved", rows.length, "hair selections");
  } finally {await browser.close();}
}
run().catch(e=>{console.error(e);process.exitCode=1});
