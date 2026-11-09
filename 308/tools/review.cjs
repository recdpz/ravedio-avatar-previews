const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || "playwright");

const origin = process.env.PREVIEW_ORIGIN || "http://127.0.0.1:9251";
const out = process.env.CAPTURE_DIR;
const angles = ["front", "threequarter", "profile", "rightprofile", "rearquarter", "rear", "top", "underside"];
const colors = ["default", "black", "white", "blue", "teal", "purple", "pink", "red", "lime"];
const defaults = {hair: "ponytail", headwear: "none", glasses: "none", detail: "none",
  top: "jersey", bottom: "pants", skin: 1, topColor: "default", view: "body"};

async function main() {
  assert(out, "Set CAPTURE_DIR");
  fs.mkdirSync(out, {recursive: true});
  const browser = await chromium.launch({executablePath:process.env.CHROMIUM_PATH,
    args:["--use-angle=d3d11","--ignore-gpu-blocklist"]});
  try {
    const page = await browser.newPage({viewport:{width:1150,height:900}});
    const errors = [];
    const requests = new Set();
    page.on("pageerror", e => errors.push(String(e)));
    page.on("response", res => {
      if (res.ok()) requests.add(new URL(res.url()).pathname);
      else errors.push(res.status() + " " + res.url());
    });
    await page.route("**/270/viewer.js", async route => {
      const response = await route.fetch();
      const body = (await response.text())
        .replace("mode==='face'?1.5:2.7", "mode==='face'?1.5:1.06")
        .replace("mode==='face'?1.88:1.28", "mode==='face'?1.88:1.29")
        .replace("angle==='underside'?-1.05:0", "angle==='underside'?-.65:0");
      await route.fulfill({response,body});
    });

    let revision;
    async function choose(features) {
      const result = await page.evaluate(async ([rev, features]) => {
        const review = window["review"+rev];
        await review.set(features);
        if (!review.ready() || review.errors.length) throw Error(review.errors.join("\n"));
        return review.rendered();
      }, [revision, features]);
      for (const [key, value] of Object.entries(features)) {
        if (key === "angle" || key === "view") continue;
        assert.equal(key === "build" ? result.build : result.features[key], value, key);
      }
      return Object.fromEntries(Object.entries(result.components).map(([slot, url]) =>
        [slot, new URL(url, origin+"/"+revision+"/").pathname]));
    }

    async function capture(name, views) {
      for (const angle of views) {
        await page.locator("#angle").selectOption(angle);
        const png = await page.evaluate(rev => window["review"+rev].capture(1000), revision);
        fs.writeFileSync(path.join(out,[revision,name,angle].join("-")+".png"),
          Buffer.from(png.split(",")[1],"base64"));
      }
    }

    const baseline = new Map();
    const rows = [];
    const variants = [
      {build:"Feminine", top:"jersey"},
      {build:"Feminine", top:"jersey", hair:"twin-braids"},
      {build:"Feminine", top:"jersey", hair:"twin-braids", headwear:"pashmina"},
      {build:"Feminine", top:"jersey", hair:"curls", headwear:"pashmina"},
      {build:"Feminine", top:"jersey", hair:"box-braids", headwear:"pashmina"},
      {build:"Feminine", top:"open", hair:"box-braids"},
      {build:"Masculine", top:"jersey", hair:"taper"},
      {build:"Masculine", top:"jersey", hair:"taper", topColor:"white"}
    ];
    for (revision of [307,308]) {
      await page.goto(origin+"/"+revision+"/?build=Feminine&top=jersey");
      await page.waitForFunction(rev => window["review"+rev]?.ready(),revision);
      for (const [i, config] of variants.entries()) {
        const features = {...defaults,...config};
        const parts = await choose(features);
        if (revision === 307) baseline.set(i, parts);
        else {
          const changed = Object.keys(parts).filter(role => parts[role] !== baseline.get(i)[role]);
          assert.deepEqual(changed, config.build === "Feminine" && config.top === "jersey" ? ["top"] : []);
          rows.push({features, parts, changed});
        }
        if (i === 0) await capture("original", angles);
        if (revision === 308 && [1,2,3,4].includes(i)) await capture("fit"+i, ["front","threequarter","rightprofile"]);
      }
    }

    for (const color of colors) {
      await choose({...defaults, build:"Feminine", topColor:color, skin:3});
      await capture("color-"+color, ["front","rear"]);
      if (color !== "default") assert(requests.has("/308/assets/jersey-"+color+".png"), color);
    }
    assert.deepEqual(errors, []);
    fs.writeFileSync(path.join(out,"review.json"),JSON.stringify({rows,colors},null,2)+"\n");
    console.log("Verified 16 before/after selections, nine jersey colors and eight angles");
  } finally {
    await browser.close();
  }
}
main().catch(error=>{console.error(error);process.exitCode=1});
