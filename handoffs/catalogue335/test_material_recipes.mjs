import assert from 'node:assert/strict';
import {linearFromSrgb,srgbFromLinear,neutralizeHairVertexColors,dyeClothRgba,drawTortoise64} from './material_recipes.mjs';

for(const value of [0,.01,.04045,.2,.5,1]){
  assert.ok(Math.abs(srgbFromLinear(linearFromSrgb(value))-value)<1e-6);
}
const source=new Float32Array([.2,.1,.05,.8,.4,.2,.1,.4]);
const neutral=neutralizeHairVertexColors(source,4);
for(let i=0;i<neutral.length;i+=4){
  assert.equal(neutral[i],neutral[i+1]);assert.equal(neutral[i],neutral[i+2]);
  assert.ok(neutral[i]>=.7&&neutral[i]<=1.180001);
  assert.equal(neutral[i+3],source[i+3]);
}
const pixels=new Uint8ClampedArray([20,30,80,255,240,245,250,128,100,40,20,255]);
const dyed=dyeClothRgba(pixels,[.2,.01,.01],true);
assert.notDeepEqual([...dyed.slice(0,3)],[...pixels.slice(0,3)]);
assert.deepEqual([...dyed.slice(4)],[...pixels.slice(4)]);
assert.equal(dyed[3],255);assert.equal(dyed[7],128);
const marks=[];
drawTortoise64({set fillStyle(v){marks.push(v);},fillRect(){},beginPath(){},ellipse(){marks.push('spot');},fill(){}});
assert.equal(marks.filter(v=>v==='spot').length,24);
console.log('Material recipes: color round trips, pigment neutralization, alpha/pattern preservation and tortoise marks passed.');
