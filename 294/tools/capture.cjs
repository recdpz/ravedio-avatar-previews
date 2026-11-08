const fs = require("node:fs");
const path = require("node:path");
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || "playwright");
const revision = process.env.ART_REVISION || "293";
const origin = process.env.PREVIEW_ORIGIN || "http://127.0.0.1:9251";
const output = process.env.CAPTURE_DIR;
if (!output) throw Error("Set CAPTURE_DIR to a writable directory");
const hats = ["none", "cap", "beanie", "bucket", "cowboy", "headband", "ears", "pashmina"];
const angles = {
  left: [-.72, -.32],
  right: [.72, -.32],
  below: [.22, -.83],
  back: [2.68, -.41],
  front: [0, 0],
  rear: [Math.PI, 0],
  otherRear: [-2.68, -.41],
};
const hairSlots = ["hair", "hairLengths"];
const styles = new Set(process.argv.slice(2));

async function run() {
  fs.mkdirSync(output, {recursive: true});
  const browser = await chromium.launch({
    executablePath: process.env.CHROMIUM_PATH, headless: true,
    args: ["--use-angle=d3d11", "--ignore-gpu-blocklist"],
  });
  try {
    const page = await browser.newPage({viewport: {width: 1100, height: 900}});
    const failures = [];
    page.on("pageerror", error => failures.push(String(error)));
    page.on("response", response => {
      if (response.status() >= 400 && !response.url().endsWith("favicon.ico")) failures.push(response.url());
    });
    await page.route("**/270/viewer.js", async route => {
      const response = await route.fetch();
      const source = (await response.text())
        .replace("function draw(size)", "let inspectionTarget; function draw(size)")
        .replace("mode==='face'?1.88:1.28", "mode==='face'?(inspectionTarget??1.88):1.28")
        .replace("  capture: size => {", [
          "  inspectPose: (turn, tilt, scale, target, only) => {",
          "    yaw=turn; pitch=tilt; zoom=scale; inspectionTarget=target;",
          "    root.traverse(o=>{if(o.isMesh)o.visible=only===null||only.includes(o.userData.slot263)});",
          "    draw();",
          "  }, capture: size => {",
        ].join("\n"));
      await route.fulfill({response, body: source});
    });
    await page.goto(origin + "/" + revision + "/?build=Feminine&hair=side-sweep&mode=face");
    await page.waitForFunction(rev => window["review"+rev]?.ready(), revision);
    const rows = [];
    async function capture(row, mode, key) {
      const [yaw, pitch] = angles[key];
      const height = row.build === "Feminine" ? 1.69 : 1.83;
      const png = await page.evaluate(([rev,a,b,h,only]) => {
        const review = window["review"+rev];
        review.inspectPose(a,b,1.27,h,only);
        return review.capture(448);
      }, [revision,yaw,pitch,height,mode === "solo" ? hairSlots : null]);
      const file = [row.build, row.hair, row.headwear, row.top, mode, key].join("-");
      fs.writeFileSync(path.join(output,file+".png"),Buffer.from(png.split(",")[1],"base64"));
    }
    async function check(build, hair, label, headwear, top, hairColor = "default") {
      const options = {build,hair,headwear,top,hairColor,view:"face",bottom:"pants",groom:"none",detail:"none",glasses:"none"};
      const result = await page.evaluate(async ([rev, config])=>{
        const review=window["review"+rev];
        await review.set(config);
        if(!review.ready()||review.errors.length)throw Error(review.errors.join("\n"));
        return review.rendered();
      }, [revision, options]);
      if (result.features.hair !== hair || result.features.headwear !== headwear || result.features.top !== top) {
        throw Error("Unexpected selection " + JSON.stringify(result.features));
      }
      const row = {build,hair,label,headwear,top,hairColor,parts:result.components};
      if (hairColor === "default") {
        for (const angle of ["left","right","below","back"]) await capture(row,"avatar",angle);
        if (hair === "box-braids" || (hair === "flow" && headwear === "cap")) {
          for (const angle of ["rear","otherRear"]) await capture(row,"avatar",angle);
        }
        if(headwear==="none") for (const angle of ["left","right","below","back","front"]) await capture(row,"solo",angle);
      }
      rows.push(row);
    }

    for (const build of ["Feminine","Masculine"]) {
      await page.evaluate(async ([rev,build]) => window["review"+rev].set({build,headwear:"none"}),[revision,build]);
      const picks = await page.locator("#hair option").evaluateAll(options=>options.map(o=>[o.value,o.textContent]));
      for(const [hair,label] of picks) {
        if(styles.size&&!styles.has(hair))continue;
        const top = build==="Feminine"?"tank":"shirtless";
        for (const hat of hats) {
          await check(build,hair,label,hat,top);
          // Record exact Ombré paths as well. The live view shares the same assembly.
          await check(build,hair,label,hat,top,"ombre");
        }
        if(build==="Feminine" && ["straight","side-sweep","curls","twin-braids","box-braids","space-buns","ponytail"].includes(hair)){
          for(const top of ["open","sweatshirt"]) for(const hat of ["none","pashmina"]) {
            await check(build,hair,label,hat,top);
            if(hair==="twin-braids")await check(build,hair,label,hat,top,"ombre");
          }
        }
        console.log(build+" "+label);
      }
    }
    if(failures.length)throw Error(failures.join("\n"));
    fs.writeFileSync(path.join(output,"review.json"),JSON.stringify({revision,rows},null,2)+"\n");
  } finally { await browser.close(); }
}
run().catch(error=>{console.error(error);process.exitCode=1});