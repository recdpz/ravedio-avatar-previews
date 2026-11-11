// Platform-neutral portions of the existing 335 viewer's material policy.
export const linearFromSrgb = v => v<=.04045?v/12.92:((v+.055)/1.055)**2.4;
export const srgbFromLinear = v => v<=.0031308?12.92*v:1.055*v**(1/2.4)-.055;
export function neutralizeHairVertexColors(colors,itemSize=3){
  const result=new Float32Array(colors.length);let mean=0,count=colors.length/itemSize;
  for(let i=0;i<count;i++)mean+=.2126*colors[i*itemSize]+.7152*colors[i*itemSize+1]+.0722*colors[i*itemSize+2];
  mean/=count;
  for(let i=0;i<count;i++){
    const j=i*itemSize,l=.2126*colors[j]+.7152*colors[j+1]+.0722*colors[j+2];
    const shade=Math.max(.70,Math.min(1.18,Math.sqrt(l/Math.max(.001,mean))));
    result[j]=result[j+1]=result[j+2]=shade;
    if(itemSize===4)result[j+3]=colors[j+3];
  }
  return result;
}
export function dyeClothRgba(source,linearTarget,isPashmina){
  const result=new Uint8ClampedArray(source),target=linearTarget.map(v=>srgbFromLinear(v)*255);
  for(let i=0;i<result.length;i+=4){
    const light=.2126*source[i]+.7152*source[i+1]+.0722*source[i+2];
    if(light>=140||source[i+2]<=source[i])continue;
    const weave=light-(isPashmina?32:40);
    for(let c=0;c<3;c++)result[i+c]=Math.round(target[c]+weave);
  }
  return result;
}
export function drawTortoise64(context){
  context.fillStyle='#A17A49';context.fillRect(0,0,64,64);
  for(let i=0;i<24;i++){
    context.fillStyle=i%2?'#2C1A0F':'#694020';context.beginPath();
    context.ellipse((i*31)%64,(i*17)%64,5+i%7,4+i%5,i,0,Math.PI*2);context.fill();
  }
}
