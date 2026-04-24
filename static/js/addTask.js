const panel = document.getElementById("panel");
const manual = document.getElementById("manual");
const aiAssist = document.getElementById("aiAssist");
const close = document.getElementById("close");
const addTask = document.getElementById("addTask");

var tabcontent = document.getElementsByClassName("tabcontent");
for (i =0;i<tabcontent.length;++i) {
  tabcontent[i].style.display = "none";
}

var active = manual;
active.classList.add("active");
document.getElementById("manual-panel").style.display = "flex";

panel.style.display = "none";

function openTab(_, tabName) {
  var d = document.getElementById(tabName);
  document.getElementById(active.id + "-panel").style.display = "none";
  document.getElementById(tabName + "-panel").style.display = "flex";
  active.classList.remove("active");
  d.classList.add("active");
  active = d;
}

close.onclick = function() {
  panel.style.display = "none";
}

addTask.onclick = function() {
  panel.style.display = "flex";
}
