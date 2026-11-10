const fields = Object.fromEntries(["look","skin","view","crop","match"].map(name=>[name,document.getElementById(name)]));
const angleCases = new Set(["ponytail-beanie-jersey","flow-cap-bare-eyes","flow-long"]);
const cropNames = {original:"Original crop",chat:"New chat crop",profile:"New profile crop"};

function update() {
  const skin = fields.skin.value;
  const canRotate = skin === "3" && angleCases.has(fields.look.value);
  for (const option of fields.view.options) option.disabled = option.value !== "front" && !canRotate;
  if (!canRotate) fields.view.value = "front";
  const front = fields.view.value === "front";
  fields.crop.disabled = !front;
  fields.match.disabled = !front;
  for (const revision of [316,317]) {
    const key = revision+"-"+fields.look.value+"-skin"+skin;
    const title = fields.look.selectedOptions[0].textContent;
    const mode = front ? (revision === 316 && !fields.match.checked ? "original" : fields.crop.value) : fields.view.value;
    const large = document.getElementById("large-"+revision);
    large.src = "./files/review/"+key+"-"+mode+".png";
    document.getElementById("zoom-"+revision).href = large.src;
    large.alt = revision+" "+title+", "+(front ? cropNames[mode] : fields.view.selectedOptions[0].textContent);
    const caption = document.getElementById("caption-"+revision);
    const number = document.createElement("strong");
    number.textContent = revision === 316 ? "316 · Reference" : "317 · Revised";
    caption.replaceChildren(number, front ? " · "+cropNames[mode] : "");
    for (const img of document.getElementById("chat-"+revision).querySelectorAll("img")) {
      const chatCrop = revision === 316 ? "original" : "chat";
      img.src = "./files/review/"+key+"-"+chatCrop+"-"+img.width+".png";
      img.alt = revision+" "+title+" at "+img.width+" pixels";
    }
  }
}
for (const field of Object.values(fields)) field.addEventListener("change",update);
update();
