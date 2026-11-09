const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || "playwright");
const origin = process.env.PREVIEW_ORIGIN || "http://127.0.0.1:9251";
const out = process.env.CAPTURE_DIR;
const defaults = {headwear:"none", hairColor:"default", headgearColor:"default", topColor:"default",
  bottomColor:"default", glasses:"none", detail:"none", groom:"none", skin:1, view:"face"};
const roles = new Set(["hair", "hairLengths", "groom"]);

function rgb(hex) {
  return [1,3,5].map(i => {
    const n = parseInt(hex.slice(i,i+2), 16) / 255;
    return n <= .04045 ? n / 12.92 : ((n + .055) / 1.055) ** 2.4;
  });
}
function near(actual, expected) {
  assert(actual.every((x,i) => Math.abs(x - expected[i]) < 1e-5),
    JSON.stringify({actual, expected}));
}

async function run() {
  if (!out) throw Error("Set CAPTURE_DIR");
  fs.mkdirSync(out, {recursive:true});
  const browser = await chromium.launch({executablePath:process.env.CHROMIUM_PATH,
    args:["--use-angle=d3d11","--ignore-gpu-blocklist"]});
  try {
    const page = await browser.newPage({viewport:{width:1100,height:870}});
    let revision;
    async function open(r) {
      revision = r;
      await page.goto(origin + "/" + r + "/");
      await page.waitForFunction(r => window["review"+r]?.ready(), r);
    }
    async function choose(state) {
      return page.evaluate(async ([r, state]) => {
        const review = window["review"+r];
        await review.set(state);
        if (!review.ready() || review.errors.length) throw Error(review.errors.join("\n"));
        return {selection:review.rendered(), materials:review.materials()};
      }, [revision,state]);
    }
    async function capture(name, angles) {
      for (const angle of angles) {
        await page.locator("#angle").selectOption(angle);
        const data = await page.evaluate(r => window["review"+r].capture(560), revision);
        fs.writeFileSync(path.join(out, [revision,name,angle].join("-")+".png"),
          Buffer.from(data.split(",")[1], "base64"));
      }
    }
    const styles = {Feminine:["ponytail","space-buns","twin-braids","box-braids","straight","curls","bob","side-sweep"],
      Masculine:["taper","sidepart","buzz","curly-top","afro","flow","locs","middle-part"]};
    const captureStyles = new Set(["ponytail","space-buns","twin-braids","curls","taper","curly-top","buzz"]);
    for (const r of ["300", "301"]) {
      await open(r);
      for (const [build,hairs] of Object.entries(styles)) {
        for (const hair of hairs) {
          const top = build === "Feminine" ? "open" : "tank";
          const outfit = {...defaults,build,hair,top};
          const original = await choose(outfit);
          if (captureStyles.has(hair)) await capture(hair, ["front","threequarter","rear"]);
          if (r === "301") {
            const brown = await choose({...outfit,hairColor:"darkbrown"});
            assert.deepEqual(brown.selection.components, original.selection.components);
            assert.deepEqual(brown.materials.filter(m=>roles.has(m.slot)),
              original.materials.filter(m=>roles.has(m.slot)));
          }
          if (["ponytail","space-buns","taper"].includes(hair)) {
            for (const headwear of ["beanie","headband","pashmina"]) {
              await choose({...outfit,headwear});
              await capture(hair+"-"+headwear, ["threequarter","rearquarter"]);
            }
          }
        }
      }
      for (const build of Object.keys(styles)) {
        const hair = styles[build][0];
        const hoodie = await choose({...defaults,build,hair,top:"sweatshirt",topColor:"lime",view:"body"});
        await capture(build+"-lime-hoodie", ["front","rearquarter"]);
        if (r === "301") {
          const top = rgb("#A6BB57");
          const m = hoodie.materials.filter(m=>m.slot==="top");
          near(m.find(v=>v.name.includes("Top / sweatshirt")).color, top);
          near(m.find(v=>v.name.includes("Hoodie / cavity215")).color, top.map(v=>v*.48));
          near(m.find(v=>v.name.includes("Hoodie / facing215")).color, top.map(v=>v*.78));
          near(m.find(v=>v.name.includes("Hoodie / soft cord")).color, [.7379104,.66538727,.80695224]);
        }
        await choose({...defaults,build,hair,headwear:"pashmina",headgearColor:"black",top:"jersey",topColor:"black",view:"body"});
        await capture(build+"-black-pashmina-jersey", ["front","rearquarter"]);
        await choose({...defaults,build,hair,headwear:"headband",headgearColor:"black",top:"tshirt"});
        await capture(build+"-black-bandana", ["threequarter","rearquarter"]);
      }
      const original = await choose({...defaults,build:"Masculine",hair:"taper",top:"tank",groom:"short",skin:3});
      await capture("short-beard-brown", ["threequarter","profile"]);
      if (r === "301") {
        near(original.materials.find(m=>m.slot==="groom").color, [.16*.82,.059*.82,.03*.82]);
        const auburn = await choose({hairColor:"auburn"});
        near(auburn.materials.find(m=>m.slot==="groom").color, rgb("#984A30").map(v=>v*.82));
        const ombre = await choose({hairColor:"ombre"});
        near(ombre.materials.find(m=>m.slot==="groom").color, [.145*.82,.062*.82,.034*.82]);
      }
    }
    for (const build of Object.keys(styles)) {
      await choose({...defaults,build,hair:styles[build][0]});
      const keys = id => page.locator("#"+id+" option").evaluateAll(ns=>ns.map(n=>n.value).filter(v=>v!=="default"));
      const hairColors = await keys("hairColor");
      const colors = await keys("topColor");
      const headwearColors = await keys("headgearColor");
      const bottomColors = await keys("bottomColor");
      for (const hair of styles[build]) {
        for (const hairColor of hairColors) await choose({hair,hairColor});
      }
      for (const top of await keys("top")) {
        if (top === "shirtless") continue;
        for (const topColor of colors) await choose({top,topColor});
      }
      for (const headwear of (await keys("headwear")).filter(k=>k!=="none")) {
        for (const headgearColor of headwearColors) await choose({headwear,headgearColor});
      }
      for (const bottom of await keys("bottom")) {
        for (const bottomColor of bottomColors) await choose({bottom,bottomColor});
      }
    }
    console.log("Original/Brown material equality, grooming, garment tint and palette selectors verified");
  } finally {await browser.close();}
}
run().catch(error=>{console.error(error);process.exitCode=1});
