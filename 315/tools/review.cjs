const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || "playwright");
const root = path.resolve(__dirname,"..");
const mapping = JSON.parse(fs.readFileSync(path.join(root,"asset-map.json"))).components;
const base = process.env.PREVIEW_ORIGIN || "http://127.0.0.1:9251";
const out = process.env.CAPTURE_DIR;
const wardrobe = [
  ["Feminine","curls","pashmina","open","pants","reading","hot"],
  ["Feminine","ponytail","beanie","jersey","skirt","rectangular","sprout"],
  ["Feminine","straight","cap","tank","shorts","reading","none"],
  ["Feminine","box-braids","headband","triangle","bikini","none","none"],
  ["Feminine","bob","bucket","sweatshirt","pants","none","none"],
  ["Feminine","side-sweep","cowboy","strappy","shorts","none","sprout"],
  ["Feminine","space-buns","ears","bandeau","skirt","none","none"],
  ["Feminine","twin-braids","none","tshirt","pants","none","none"],
  ["Masculine","flow","cap","sweatshirt","pants","wayfarer","hot","short"],
  ["Masculine","taper","none","tank","shorts","none","none","stubble"],
  ["Masculine","buzz","headband","shirtless","shorts","none","none","patch"],
  ["Masculine","curly-top","beanie","jersey","pants","rectangular","sprout","long"],
  ["Masculine","afro","pashmina","tshirt","pants","none","none","none"],
  ["Masculine","locs","bucket","buttonup","pants","none","none","none"],
  ["Masculine","middle-part","cowboy","jersey","shorts","none","none","none"],
  ["Masculine","sidepart","ears","tank","shorts","none","none","none"]
];
const views = ["front","threequarter","profile","rightprofile","rearquarter","rear","top","underside"];

function choice(row,index) {
  const [build,hair,headwear,top,bottom,glasses,detail,groom="none"] = row;
  return {build,hair,headwear,top,bottom,glasses,detail,groom,view:"body",
    hairColor:index%2 ? "ombre" : "default",skin:index%2 ? 0 : 3,eyes:["original","bean","hooded","tapered"][index%4],
    lensTint:glasses==="reading" ? "clear" : "dark",topColor:top==="jersey" ? "white" : "default"};
}

function pathname(url) {
  return decodeURIComponent(new URL(url,base).pathname.slice(1));
}

async function main() {
  fs.mkdirSync(out,{recursive:true});
  const browser = await chromium.launch({executablePath:process.env.CHROMIUM_PATH,
    args:["--use-angle=d3d11","--ignore-gpu-blocklist"]});
  const results = {};
  try {
    const page = await browser.newPage({viewport:{width:890,height:850}});
    const errors = [];
    page.on("pageerror",e=>errors.push(e.message));
    page.on("response",response=>{
      if(response.status()>=400 && !response.url().endsWith("/favicon.ico"))
        errors.push(response.status()+" "+response.url());
    });
    for(const revision of [314,315]){
      await page.goto(base+"/"+revision+"/");
      await page.waitForFunction(r=>window["review"+r]?.ready(),revision);
      results[revision] = {};
      for(const [index,row] of wardrobe.entries()){
        const state = choice(row,index);
        const info = await page.evaluate(async ([revision,state])=>{
          const api = window["review"+revision];
          await api.set({...state,angle:"threequarter"});
          if(!api.ready() || api.errors.length) throw new Error(api.errors.join("\n"));
          return {state:api.rendered(),inspection:api.inspect(),materials:api.materials()};
        },[revision,state]);
        const label=state.hair;
        for(const key of ["hair","headwear","top","bottom","detail","glasses","lensTint","groom"]){
          assert.equal(info.state.features[key],state[key],label+"/"+key);
        }
        results[revision][label]=info;
        if(revision===315){
          const old=results[314][label];
          assert.deepEqual(info.inspection.geometry,old.inspection.geometry,label);
          assert.deepEqual(info.inspection.groups,old.inspection.groups,label);
          for(const [role,value] of Object.entries(old.state.components)){
            const entry = mapping[pathname(value)];
            const expected = role==="lenses" ? entry[state.lensTint] : entry;
            assert.equal(pathname(info.state.components[role]),"315/assets/"+expected+".glb",label+"/"+role);
          }
          const skin=info.materials.filter(m=>m.name.startsWith("Skin"));
          assert(skin.length && skin.every(m=>Math.abs(m.roughness-.365)<1e-5 && Math.abs(m.clearcoat-.23)<1e-5),label);
          if (["curls","ponytail","flow"].includes(label))
            assert(info.materials.some(m=>m.roughnessMap),label+"/roughness map");
          const lenses=info.materials.filter(m=>m.slot==="lenses");
          for(const lens of lenses){
            assert(Math.abs(lens.opacity-(state.lensTint==="clear" ? .075 : .74))<1e-5,label);
            assert.equal(lens.transmission,0);
            assert.equal(lens.depthWrite,false);
          }
        }
        for(const angle of revision===315 ? views : ["threequarter"]){
          await page.locator("#angle").selectOption(angle);
          const data = await page.evaluate(r=>window["review"+r].capture(400),revision);
          fs.writeFileSync(path.join(out,[revision,label,angle].join("-")+".png"),Buffer.from(data.split(",")[1],"base64"));
        }
      }
      if(revision===315){
        const checks = await page.evaluate(async ()=>{
          const r=window.review315;
          const sample = {build:"Masculine",hair:"flow",headwear:"cap",top:"sweatshirt",bottom:"pants",
            glasses:"wayfarer",detail:"hot",groom:"short"};
          const look = {};
          for(const lensTint of ["dark","clear"]){
            await r.set({...sample,lensTint});
            look[lensTint] = {path:r.rendered().components.lenses,materials:r.materials().filter(m=>m.slot==="lenses")};
          }
          return look;
        });
        assert.notEqual(checks.clear.path,checks.dark.path);
        assert.equal(checks.clear.materials[0].opacity,.075);
        assert.equal(checks.dark.materials[0].opacity,.74);
      }
    }
    assert.deepEqual(errors,[]);
    const report={revision:315,looks:wardrobe.length,angles:views,geometryMatches:wardrobe.length,
                  imageCount:wardrobe.length*(views.length+1),coverage:wardrobe.map(row=>row[1]),lensTintSwap:true};
    fs.writeFileSync(path.join(out,"browser.json"),JSON.stringify(report,null,2)+"\n");
    console.log(report);
  }finally{await browser.close();}
}
main().catch(error=>{console.error(error);process.exitCode=1;});
