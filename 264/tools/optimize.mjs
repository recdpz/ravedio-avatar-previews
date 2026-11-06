import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {MeshoptSimplifier as S} from './vendor/meshopt_simplifier.mjs';
await S.ready;
const D=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const variant=process.argv[2]||'pass2',out=path.join(D,variant==='pass2'?'assets':variant);fs.mkdirSync(out,{recursive:true});
const types={5121:Uint8Array,5123:Uint16Array,5125:Uint32Array,5126:Float32Array},widths={SCALAR:1,VEC2:2,VEC3:3,VEC4:4};
export function readGLB(file){const raw=fs.readFileSync(file),n=raw.readUInt32LE(12),g=JSON.parse(raw.subarray(20,20+n));return{g,bin:raw.subarray(28+n),raw}}
function array(g,bin,i){const a=g.accessors[i],v=g.bufferViews[a.bufferView],T=types[a.componentType],w=widths[a.type];if(!T||!w||a.sparse)throw Error('Unsupported accessor '+i);const stride=v.byteStride||T.BYTES_PER_ELEMENT*w,start=(v.byteOffset||0)+(a.byteOffset||0),data=new T(a.count*w);for(let n=0;n<a.count;n++)new Uint8Array(data.buffer,n*w*T.BYTES_PER_ELEMENT,w*T.BYTES_PER_ELEMENT).set(bin.subarray(start+n*stride,start+n*stride+w*T.BYTES_PER_ELEMENT));return data}
function floats(a,info){if(!info.normalized)return new Float32Array(a);const max=info.componentType===5121?255:65535;return Float32Array.from(a,x=>x/max)}
for(const build of ['Feminine','Masculine']){
 const source=path.join(D,'sources',build+'-hoodie-pants-cap263.glb'),{g,bin,raw}=readGLB(source),q=structuredClone(g);q.bufferViews=[];q.accessors=[];q.buffers=[];let offset=0;const chunks=[],rows=[];
 function view(data,target){const buf=Buffer.from(data.buffer,data.byteOffset,data.byteLength),pad=(4-offset%4)%4;if(pad){chunks.push(Buffer.alloc(pad));offset+=pad}const index=q.bufferViews.length;q.bufferViews.push({buffer:0,byteOffset:offset,byteLength:buf.length,...(target?{target}:{})});chunks.push(buf);offset+=buf.length;return index}
 function acc(data,sourceInfo,target){const a={...sourceInfo,bufferView:view(data,target),byteOffset:0,count:data.length/widths[sourceInfo.type]};delete a.sparse;const w=widths[a.type];if(a.min||a.max||a.type==='VEC3'){const lo=Array(w).fill(Infinity),hi=Array(w).fill(-Infinity);for(let n=0;n<data.length;n++){const k=n%w;lo[k]=Math.min(lo[k],data[n]);hi[k]=Math.max(hi[k],data[n])}a.min=lo;a.max=hi}const i=q.accessors.length;q.accessors.push(a);return i}
 for(let mi=0;mi<g.meshes.length;mi++){
  const mesh=g.meshes[mi],node=g.nodes.find(n=>n.mesh===mi),role=node?.extras?.component159||'unknown',name=node?.name||mesh.name;
  for(let pi=0;pi<mesh.primitives.length;pi++){
   const p=mesh.primitives[pi],np=q.meshes[mi].primitives[pi];if(p.mode!==undefined&&p.mode!==4||p.targets)throw Error('Unsupported geometry');
   const attrs=Object.fromEntries(Object.entries(p.attributes).map(([k,v])=>[k,array(g,bin,v)])),pos=attrs.POSITION,indices=new Uint32Array(array(g,bin,p.indices));let reduced=indices,error=0,locks=0;
   const preserve=['eyes','mouth','lashes','extra','glasses','lenses'].includes(role)||indices.length<1800||/cord|drawstring|cuff|seam|hem|binding|opening|button|tie|elastic/i.test(name);
   const scale=S.getScale(pos,3);let budget=variant==='pass2'?.00035:.0007;
   if(role==='hair')budget=variant==='pass2'?.00020:.00045;
   if(role==='base')budget=variant==='pass2'?.00025:.0004;
   if(!preserve){const channels=[],weights=[];for(const [k,w]of [['NORMAL',.35],['TEXCOORD_0',1],['COLOR_0',2]]){if(!attrs[k])continue;const info=g.accessors[p.attributes[k]],size=widths[info.type];channels.push([floats(attrs[k],info),size]);weights.push(...Array(size).fill(w))}const stride=weights.length,values=new Float32Array(pos.length/3*stride);for(let i=0;i<pos.length/3;i++){let c=0;for(const [a,n]of channels){for(let j=0;j<n;j++)values[i*stride+c++]=a[i*n+j]}}
    const target=Math.max(12,Math.floor(indices.length*.06/3)*3);[reduced,error]=S.simplifyWithAttributes(indices,pos,3,values,stride,weights,null,target,budget,['LockBorder','ErrorAbsolute']);if(reduced.length<3)throw Error('Empty mesh');
   }
   // Compact referenced vertices, copying every surviving attribute exactly. No rescaling/recentering/quantization.
   const remap=new Map();let used=[];const ii=new Uint32Array(reduced.length);for(let i=0;i<reduced.length;i++){const v=reduced[i];if(!remap.has(v)){remap.set(v,used.length);used.push(v)}ii[i]=remap.get(v)}
   for(const[k,a]of Object.entries(attrs)){const info=g.accessors[p.attributes[k]],w=widths[info.type],v=new a.constructor(used.length*w);for(let j=0;j<used.length;j++)v.set(a.subarray(used[j]*w,used[j]*w+w),j*w);np.attributes[k]=acc(v,info,34962)}
   const id=used.length<65536?new Uint16Array(ii):ii;np.indices=acc(id,{componentType:used.length<65536?5123:5125,type:'SCALAR'},34963);
   rows.push({name,role,primitive:pi,preserve,before_triangles:indices.length/3,after_triangles:reduced.length/3,before_vertices:pos.length/3,after_vertices:used.length,absolute_error:error,error_limit:budget,scale,material:p.material});
  }
 }
 // Keep texture payloads and every material, node, role and transform unchanged.
 for(let i=0;i<(g.images||[]).length;i++){const im=g.images[i];if(im.bufferView!==undefined){const v=g.bufferViews[im.bufferView];q.images[i].bufferView=view(bin.subarray(v.byteOffset||0,(v.byteOffset||0)+v.byteLength));}}
 q.buffers=[{byteLength:offset}];q.asset.generator='Ravedio264 attribute-aware meshoptimizer derivative; semantic nodes/materials preserved';const js=Buffer.from(JSON.stringify(q)),jb=Buffer.concat([js,Buffer.alloc((4-js.length%4)%4,32)]),bb=Buffer.concat([...chunks,Buffer.alloc((4-offset%4)%4)]);const header=Buffer.alloc(20);header.writeUInt32LE(0x46546c67,0);header.writeUInt32LE(2,4);header.writeUInt32LE(28+jb.length+bb.length,8);header.writeUInt32LE(jb.length,12);header.writeUInt32LE(0x4e4f534a,16);const bh=Buffer.alloc(8);bh.writeUInt32LE(bb.length,0);bh.writeUInt32LE(0x004e4942,4);const result=Buffer.concat([header,jb,bh,bb]);const file=build+'-optimized264.glb';fs.writeFileSync(path.join(out,file),result);const metrics={build,variant,source:path.relative(D,source),source_sha256:crypto.createHash('sha256').update(raw).digest('hex'),file,bytes_before:raw.length,bytes_after:result.length,triangles_before:rows.reduce((s,r)=>s+r.before_triangles,0),triangles_after:rows.reduce((s,r)=>s+r.after_triangles,0),primitives_before:rows.length,primitives_after:rows.length,materials:g.materials.length,rows};fs.writeFileSync(path.join(out,build+'-metrics.json'),JSON.stringify(metrics,null,2)+'\n');console.log(build,metrics.triangles_before,'->',metrics.triangles_after,'bytes',raw.length,'->',result.length);
}
