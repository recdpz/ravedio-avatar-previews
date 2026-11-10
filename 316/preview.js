const fields = Object.fromEntries(["look","skin","view","plate"].map(name=>[name,document.getElementById(name)]));

function update() {
  const skin=fields.skin.value;
  for(const option of fields.view.options) option.disabled = option.value!=="chat" && skin!=="3";
  if(skin!=="3") fields.view.value="chat";
  document.documentElement.style.setProperty("--plate",fields.plate.value);
  for(const revision of [314,316]){
    const key=revision+"-"+fields.look.value+"-skin"+skin;
    const title=fields.look.selectedOptions[0].textContent;
    const large=document.getElementById("large-"+revision);
    large.src="./files/raw/"+key+"-"+fields.view.value+".png";
    large.alt=revision+" "+title+", "+fields.view.selectedOptions[0].textContent;
    for(const img of document.getElementById("chat-"+revision).querySelectorAll("img")){
      img.src="./files/chat/"+key+"-"+img.width+".png";
      img.alt=revision+" "+title+" at "+img.width+" pixels";
    }
  }
}
for(const field of Object.values(fields)) field.addEventListener("change",update);
update();
