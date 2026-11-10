// Resolve the pinned preview's asset choices without reproducing its fit logic.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const [root, output, priorMatrix, priorFixtures, revision] = process.argv.slice(2);
assert(root && output && priorMatrix && priorFixtures && ["308","314"].includes(revision),
       "Pass the art checkout, output JSON, 308 selector capture, 308 fixture capture and revision");
const read = name => fs.readFileSync(path.join(root, name), "utf8");
const json = name => JSON.parse(read(name));
const base = "http://preview/" + revision + "/";
const html = read(revision + "/index.html");
const viewer = new URL(html.match(/type="module" src="([^"]+)"/)[1], base).pathname.slice(1);
const sourceFiles = [revision + "/index.html", viewer, "270/assets.json", "263/catalogue263.json", "235/face-palette209.json"];
function resource(attribute) {
    const match = html.match(new RegExp('data-' + attribute + '="([^"]+)"'));
    assert(match, attribute);
    const url = new URL(match[1], base);
    sourceFiles.push(url.pathname.slice(1));
    return [url, json(url.pathname.slice(1))];
}
const [bandanaUrl, bandanaFits] = resource("bandana-fits");
const [hairUrl, hairFits] = resource("hair-fits");
const [pashminaUrl, pashminaFits] = resource("pashmina-fits");
const [wardrobeUrl, wardrobeFits] = resource("wardrobe-fits");
const [materialUrl, materialAssets] = resource("material-assets");
const [detailUrl, detailFits] = revision === "314" ? resource("detail-fits") : [null, null];
const catalogue = json("263/catalogue263.json");
for (const [model, styles] of Object.entries(hairFits)) {
    for (const [style, fit] of Object.entries(styles)) {
        Object.assign(catalogue.builds[model].hair[style], {label: fit.label});
    }
}
const browser = jsonFromFile(priorMatrix)["308"];
function jsonFromFile(file) { return JSON.parse(fs.readFileSync(file, "utf8")); }
const script = read(viewer);
function section(start, end) {
    const a = script.indexOf(start), b = script.indexOf(end, a + start.length);
    assert(a !== -1 && b > a, start);
    return script.slice(a, b);
}
const resolver = vm.runInNewContext([
    section("function bandanaFit(", "function bandanaNote("),
    section("const defaults=", "try{const saved="),
    section("function paths(", "function component("),
    "({assembledPaths, sanitize, compatible})",
].join("\n"), {
    URL, catalogue, bandanaUrl, bandanaFits, hairUrl, hairFits, pashminaUrl, pashminaFits,
    wardrobeUrl, wardrobeFits, showLashes: true,
    manifestUrl: new URL("http://preview/270/assets.json"), manifest: json("270/assets.json"),
    document: {baseURI: base}, materialAssets, detailUrl, detailFits,
    materialPaths: new Map(Object.entries(materialAssets.components).map(([from,to]) =>
        [new URL(from, materialUrl).href, new URL(to, materialUrl).href])),
});
const uri = value => value ? decodeURIComponent(new URL(value, base).pathname).slice(1) : null;
function select(build, values, roles) {
    const p = resolver.assembledPaths(resolver.sanitize(build, values), build);
    return Object.fromEntries(roles.map(role => [role, uri(p[role])]));
}

const rows = {};
const builds = {};
for (const [build, spec] of Object.entries(catalogue.builds)) {
    for (const hair of Object.keys(spec.hair)) {
        for (const headwear of Object.keys(catalogue.headwear)) {
            if (!resolver.compatible(build, hair, headwear)) continue;
            for (const top of Object.keys(spec.tops)) {
                for (const finish of ["default", "ombre"]) {
                    const key = [build,hair,headwear,top,finish].join("/");
                    const p = select(build, {hair,headwear,top,hairColor:finish,detail:"sprout",bottom:"pants",groom:"none"},
                        ["hair","hairLengths","headgear","top","extra"]);
                    if (revision === "308") {
                        for (const [role, value] of Object.entries(p)) {
                            assert.equal(value, uri(browser.rows[key][role]), key + "/" + role);
                        }
                    }
                    const {extra, ...rest} = p;
                    rows[key] = {...rest, sprout: extra};
                }
            }
        }
    }
    const faces = {}, grooms = {}, bases = {}, bottoms = {}, glasses = {};
    for (const eye of Object.keys(spec.eyes)) faces[eye] = select(build, {eyes:eye}, ["eyes","lashes","mouth","nose"]);
    for (const groom of Object.keys(spec.grooms)) {
        grooms[groom] = select(build, {groom}, ["groom"]).groom;
        if (revision === "308") assert.equal(grooms[groom], uri(browser.grooms[build + "/" + groom]));
    }
    for (const bottom of Object.keys(spec.bottoms)) {
        const regular = select(build, {bottom}, ["base","bottom"]);
        bottoms[bottom] = regular.bottom;
        bases[bottom] = {clothed:regular.base};
        if (Object.hasOwn(spec.tops,"shirtless")) bases[bottom].shirtless = select(build,{bottom,top:"shirtless"},["base"]).base;
    }
    for (const style of Object.keys(catalogue.glasses)) glasses[style] = select(build,{glasses:style},["glasses","lenses"]);
    builds[build] = {faces,grooms,bases,bottoms,glasses,hot:select(build,{detail:"hot"},["extra"]).extra};
}
assert.deepEqual(Object.keys(rows).sort(), Object.keys(browser.rows).sort());
const labels = collection => Object.fromEntries(Object.entries(collection).map(([key,value]) => [key,value.label]));
const options = {
    builds: Object.fromEntries(Object.entries(catalogue.builds).map(([build,spec]) =>
        [build,Object.fromEntries(["hair","eyes","grooms","tops","bottoms"].map(name => [name,labels(spec[name])]))])),
    headwear:labels(catalogue.headwear), glasses:labels(catalogue.glasses), details:labels(catalogue.details),
    colors:browser.colors, color_aliases:browser.aliases, lens_defaults:catalogue.lensDefaults,
};
const fixtures = jsonFromFile(priorFixtures);
const cases = {};
for (const [id, item] of Object.entries(fixtures)) {
    cases[id.slice(5)] = {...item, baseline_scene: id, native: true};
}
cases["twin-jersey-bare"] = {...fixtures["r308-twin-jersey-pashmina"],
    features: {...fixtures["r308-twin-jersey-pashmina"].features, headwear:"none"},
    baseline_scene:"r308-twin-jersey-pashmina", native:false};
cases["flow-cap-bare-eyes"] = {...fixtures["r308-flow-cap"],
    features: {...fixtures["r308-flow-cap"].features, glasses:"none", detail:"none"},
    baseline_scene:"r308-flow-cap", native:false};
for (const item of Object.values(cases)) {
    const {build, features, parts} = item;
    const choice = resolver.sanitize(build, features);
    assert.deepEqual({...choice}, features);
    const selected = resolver.assembledPaths(choice, build);
    if (revision === "308" && item.native) {
        assert.deepEqual(Object.fromEntries(Object.entries(selected).map(([k,v]) => [k,uri(v)])),
                         Object.fromEntries(Object.entries(parts).map(([k,v]) => [k,uri(v)])));
    }
    item.parts = Object.fromEntries(Object.entries(selected).map(([k,v]) => [k,uri(v)]));
}
fs.writeFileSync(output, JSON.stringify({revision:Number(revision),sourceFiles, rows, builds, options, cases},null,2)+"\n");
console.log("Resolved", Object.keys(rows).length, "selectors and", Object.keys(cases).length, "fixtures for", revision);
