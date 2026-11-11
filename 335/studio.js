const byId=id=>document.getElementById(id);
const tables={
  hat:[['none','None'],['cap','Cap'],['beanie','Beanie'],['bucket','Bucket hat'],['cowboy','Cowboy hat'],['ears','Animal ears'],['headband','Bandana'],['pashmina','Pashmina']],
  color:[['default','Brown'],['black','Black'],['auburn','Auburn'],['blonde','Blonde'],['platinum','Platinum'],['pink','Pink'],['purple','Purple'],['ombre','Ombré']],
  angle:[['front','Front'],['threequarter','Three-quarter'],['profile','Left side'],['rightprofile','Right side'],['rear','Back'],['rearquarter','Rear three-quarter'],['above','Above'],['underneath','Underneath']]
};
for(const [key,table] of Object.entries(tables)){
  const field=byId('source-'+key);
  field.replaceChildren(...table.map(([id,label])=>new Option(label,id)));
  field.value=key==='angle'?'threequarter':table[0][0];
  field.addEventListener('change',update);
}
function update(){
  const values=Object.keys(tables).map(key=>byId('source-'+key).value);
  const path='files/review/'+values.join('-')+'.png';
  byId('source-image').src=path;
  byId('source-image').alt=values.join(', ')+' · Blender export review';
  byId('source-link').href=path;
}
update();
