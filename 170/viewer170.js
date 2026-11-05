const $=id=>document.getElementById(id),hero=$('hero'),cover=$('cover'),cache=new Map();
const colors=[[.8713671191987972,.6038273388553378,.4793201831008268],[.8148465722161012,.6239603916950761,.3419144249086609],[.5149176653765214,.3049873140698863,.18782077230067787],[.21586050011389926,.10461648409110419,.07421356838014963]];
const sets={Feminine:[['bandeau','Bandeau'],['triangle','Triangle top'],['strappy','Strappy crop'],['tshirt','T-shirt'],['jersey','Jersey'],['open','Open shirt'],['tank','Tank'],['sweatshirt','Hoodie']],Masculine:[['tank','Tank'],['jersey','Jersey'],['sweatshirt','Hoodie']]};
const eyes=[['original','Original'],['soft','Round'],['almond','Almond'],['lowarc','Narrow']];
const oldEyes=[['original','Original'],['soft','Soft'],['almond','Almond'],['lowarc','Low arc']];
let lighting='studio';
let comparison='after',build='Feminine',chosenTop='tank',eye='original',tone=1,angle='threequarter',mode='body',showTop=true,live=null,loading=false,generation=0,eyeGeneration=0;
const memory={Feminine:{top:'tank',eye:'original'},Masculine:{top:'jersey',eye:'original'}};
function eyeLabel(){return (comparison==='before'?oldEyes:eyes).find(x=>x[0]===eye)[1]}
function topLabel(){return sets[build].find(x=>x[0]===chosenTop)[1]}
function prefix(){return comparison==='before'?'../169/':''}
function menu(){ $('top').replaceChildren(...sets[build].map(([v,label])=>new Option(label,v)));$('top').value=chosenTop;$('eyes').replaceChildren(...(comparison==='before'?oldEyes:eyes).map(([v,label])=>new Option(label,v)));$('eyes').value=eye;$('eyes').disabled=false;}
function remember(){memory[build]={top:chosenTop,eye};}
function display(){
 const isEyeView=mode==='face'&&['front','threequarter','profile'].includes(angle);
 const poster=isEyeView?prefix()+build+'-eyes-'+eye+'-face-'+angle+'.webp':prefix()+build+'-'+chosenTop+'-'+angle+'.webp';
 if(cover.dataset.poster!==poster){cover.dataset.poster=poster;const im=new Image();im.onload=()=>{if(cover.dataset.poster===poster){cover.src=poster;cover.alt=isEyeView?'Blender eye reference: '+build+' '+eyeLabel()+', '+angle:'Blender render: '+build+' '+topLabel()+', '+angle}};im.src=poster;}
 cover.style.transform=isEyeView?'none':mode==='face'?'scale(1.8)':mode==='outfit'?'scale(2.1)':'none';cover.style.transformOrigin=mode==='face'?'50% 28%':'50% 52%';
 $('full').href=poster;$('full').textContent=isEyeView?'Rendered '+eyeLabel()+' eyes':'Rendered outfit · Original eyes';$('baseDownload').href=prefix()+build+'-base.glb';$('topDownload').href=prefix()+build+'-'+chosenTop+'-top.glb';$('eyeDownload').hidden=false;$('eyeDownload').href=prefix()+build+'-eyes-'+eye+'.glb';
 for(const key of ['body','outfit','face'])$(key).setAttribute('aria-pressed',String(mode===key));
 $('eyeNote').textContent=comparison==='before'?'169 uses its previous eye shapes: Original, Soft, Almond and Low arc.':'Original stays unchanged. Round, Almond and Narrow are revised candidates.';
 if(live&&live.root){live.root.traverse(o=>{if(o.isMesh)for(const mat of(Array.isArray(o.material)?o.material:[o.material])){if(mat.name.startsWith('Skin'))mat.color.setRGB(...colors[tone]);mat.envMapIntensity=.7;}});live.topRoot.visible=showTop;draw();}
 $('hint').textContent=live&&live.root?live.label:'Blender render '+(comparison==='before'?'169':'170')+' · Light warm';
}
function component(key){if(!cache.has(key))cache.set(key,new Promise((resolve,reject)=>new THREE.GLTFLoader().load(key+'.glb',g=>resolve(g.scene),undefined,reject)).catch(e=>{cache.delete(key);throw e}));return cache.get(key);}
function orient(){if(!live)return;live.yaw={front:0,threequarter:-.464,profile:-Math.PI/2,rightprofile:Math.PI/2,rear:Math.PI,top:0}[angle];live.pitch=angle==='top'?1.07:0;live.zoom=1;draw();}
function draw(){if(!live)return;const {r,s,c}=live,w=hero.clientWidth,h=hero.clientHeight;r.setSize(w,h,false);const span=(mode==='face'?1.5:mode==='outfit'?1.25:2.7)/live.zoom,y=mode==='face'?1.88:mode==='outfit'?1.23:1.28;c.left=-span*w/h/2;c.right=span*w/h/2;c.top=span/2;c.bottom=-span/2;c.updateProjectionMatrix();c.position.set(6*Math.sin(live.yaw)*Math.cos(live.pitch),y+6*Math.sin(live.pitch),6*Math.cos(live.yaw)*Math.cos(live.pitch));c.lookAt(0,y,0);r.render(s,c);}
function setLabel(){live.label='Live 3D '+(comparison==='before'?'169':'170')+' · '+build+' · '+eyeLabel()+' eyes · '+(lighting==='studio'?'Soft studio':'Previous 3D');}
async function loadSelection(){
 if(!live)return;const id=++generation;++eyeGeneration;const pick={build,top:chosenTop,eye,comparison};const pre=pick.comparison==='before'?'../169/':'';
 $('png').disabled=true;$('status').textContent='Loading '+pick.build+' '+topLabel()+'…';
 try{
  const requests=[component(pre+pick.build+'-base'),component(pre+pick.build+'-'+pick.top+'-top')];requests.push(component(pre+pick.build+'-eyes-'+pick.eye));
  const parts=await Promise.all(requests);if(id!==generation||pick.build!==build||pick.top!==chosenTop||pick.eye!==eye||pick.comparison!==comparison)return;
  const root=new THREE.Group(),base=parts[0].clone(true),top=parts[1].clone(true),eyeRoot=parts[2]?parts[2].clone(true):null;root.add(base,top);if(eyeRoot)root.add(eyeRoot);
  const old=live.root;live.root=root;live.topRoot=top;live.eyeRoot=eyeRoot;live.pick=pick;live.s.add(root);if(old)live.s.remove(old);
  setLabel();cover.style.visibility='hidden';live.r.domElement.style.visibility='visible';$('png').disabled=false;display();$('status').textContent='3D ready. Drag to rotate; scroll or pinch to zoom. Hide the top to inspect the shoulders.';
 }catch(e){if(id===generation){$('status').textContent='Could not load this selection. The previous model or rendered view remains visible.';$('start').hidden=false;}}
}
async function loadEyes(){
 if(!live)return start();
 if(!live.pick||live.pick.build!==build||live.pick.top!==chosenTop||live.pick.comparison!==comparison)return loadSelection();
 const target=live.root,id=++eyeGeneration,pick={build,eye,comparison};$('status').textContent='Updating '+eyeLabel()+' eyes…';
 try{const part=await component((pick.comparison==='before'?'../169/':'')+pick.build+'-eyes-'+pick.eye);if(id!==eyeGeneration||live.root!==target||build!==pick.build||eye!==pick.eye||comparison!==pick.comparison)return;
  const replacement=part.clone(true);target.add(replacement);if(live.eyeRoot)target.remove(live.eyeRoot);live.eyeRoot=replacement;live.pick.eye=eye;setLabel();$('png').disabled=false;display();$('status').textContent='Eyes updated. Body, outfit and camera remain in place.';
 }catch(e){if(id===eyeGeneration)$('status').textContent='These eyes could not load. The previous eyes remain visible.';}
}
function environment(r,soft=false){const s=new THREE.Scene();s.background=new THREE.Color().setRGB(.095,.105,.12);function panel(w,h,x,y,z,color,rx=0,ry=0){const ob=new THREE.Mesh(new THREE.PlaneGeometry(w,h),new THREE.MeshBasicMaterial({color,side:THREE.DoubleSide}));ob.position.set(x,y,z);ob.rotation.set(rx,ry,0);s.add(ob);}panel(4,7,-4,2,0,'#fff6e9',0,Math.PI/2);panel(2,7,4,2,0,'#e2dbe8',0,-Math.PI/2);panel(5,3,0,6,0,'#e3e4ed',Math.PI/2);panel(3,5,-2,1,-5,'#eeeae3');const generator=new THREE.PMREMGenerator(r),env=generator.fromScene(s,.035).texture;generator.dispose();return env;}
async function start(){
 if(live)return loadSelection();if(loading)return;loading=true;
 try{const r=new THREE.WebGLRenderer({antialias:true,alpha:true,preserveDrawingBuffer:true});r.setPixelRatio(Math.min(devicePixelRatio,1.5));r.outputEncoding=THREE.sRGBEncoding;r.toneMapping=THREE.ACESFilmicToneMapping;r.toneMappingExposure=.95;
  const s=new THREE.Scene(),env=environment(r),environments={previous:env,studio:env};s.environment=env;const ambient=new THREE.HemisphereLight(0xe6ebf3,0x554f59,.20);s.add(ambient);const key=new THREE.DirectionalLight(0xfff0dd,.85);key.position.set(-3,5,4);s.add(key);const rim=new THREE.DirectionalLight(0xe1d7f0,.25);rim.position.set(4,3,-2);s.add(rim);
  const fill=new THREE.DirectionalLight(0xf1eff4,.20);fill.position.set(0,1,6);s.add(fill);live={r,s,environments,ambient,fill,c:new THREE.OrthographicCamera(-1,1,1,-1,.01,100),root:null,yaw:0,pitch:0,zoom:1};hero.appendChild(r.domElement);$('start').hidden=true;applyLighting();orient();
  const pointers=new Map();let drag=null,pinch=0,pinchZoom=1;
  r.domElement.addEventListener('pointerdown',e=>{pointers.set(e.pointerId,[e.clientX,e.clientY]);r.domElement.setPointerCapture(e.pointerId);drag=[e.clientX,e.clientY];if(pointers.size===2){const p=[...pointers.values()];pinch=Math.hypot(p[0][0]-p[1][0],p[0][1]-p[1][1]);pinchZoom=live.zoom;}});
  r.domElement.addEventListener('pointermove',e=>{if(!pointers.has(e.pointerId))return;pointers.set(e.pointerId,[e.clientX,e.clientY]);if(pointers.size===2){const p=[...pointers.values()],d=Math.hypot(p[0][0]-p[1][0],p[0][1]-p[1][1]);if(pinch)live.zoom=Math.max(.7,Math.min(3,pinchZoom*d/pinch));}else if(drag){live.yaw-=(e.clientX-drag[0])*.008;live.pitch=Math.max(-1.2,Math.min(1.2,live.pitch+(e.clientY-drag[1])*.006));drag=[e.clientX,e.clientY];}draw();});
  function release(e){pointers.delete(e.pointerId);drag=pointers.size?[...pointers.values()][0]:null;if(pointers.size<2)pinch=0;}
  r.domElement.addEventListener('pointerup',release);r.domElement.addEventListener('pointercancel',release);r.domElement.addEventListener('wheel',e=>{e.preventDefault();live.zoom=Math.max(.7,Math.min(3,live.zoom*Math.exp(-e.deltaY*.001)));draw();},{passive:false});
  await loadSelection();
 }catch(e){$('status').textContent='3D is unavailable here. The actual Blender renders remain available.';}finally{loading=false;}
}
$('compare').onchange=e=>{comparison=e.target.value;menu();display();if(live)loadSelection();};
$('build').onchange=e=>{remember();build=e.target.value;chosenTop=memory[build].top;eye=memory[build].eye;menu();display();if(live)loadSelection();};
$('top').onchange=e=>{chosenTop=e.target.value;remember();display();if(live)loadSelection();};
$('eyes').onchange=e=>{eye=e.target.value;remember();display();loadEyes();};
$('skin').onchange=e=>{tone=Number(e.target.value);live?display():start();};
$('angle').onchange=e=>{angle=e.target.value;display();orient();};
$('showTop').onchange=e=>{showTop=e.target.checked;if(!live)start();else display();};
for(const key of ['body','outfit','face'])$(key).onclick=()=>{mode=key;display();};
$('start').onclick=start;$('reset').onclick=()=>{angle='threequarter';mode='body';$('angle').value=angle;display();orient();};
document.querySelectorAll('[data-eye]').forEach(button=>button.onclick=()=>{remember();build=button.dataset.build;chosenTop=memory[build].top;eye=button.dataset.eye;comparison='after';mode='face';angle='front';$('build').value=build;$('compare').value=comparison;$('angle').value=angle;remember();menu();display();live?loadSelection():start();orient();hero.scrollIntoView({behavior:'smooth',block:'center'});});
$('png').onclick=()=>{if(!live||!live.root)return;draw();live.r.domElement.toBlob(blob=>{if(!blob)return;const url=URL.createObjectURL(blob),link=document.createElement('a');link.href=url;link.download='Ravedio'+(comparison==='before'?'169':'170')+'-'+build+'-'+chosenTop+'-'+eye+'.png';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);},'image/png');};
window.addEventListener('resize',draw);menu();display();

function applyLighting(){if(!live)return;live.s.environment=live.environments[lighting];live.ambient.intensity=lighting==='studio'?.26:.20;live.ambient.groundColor.setHex(lighting==='studio'?0x7e7a83:0x554f59);live.fill.intensity=lighting==='studio'?.12:0;if(live.root){setLabel();display();}else draw();}
$('lighting').onchange=e=>{lighting=e.target.value;live?applyLighting():start();};
