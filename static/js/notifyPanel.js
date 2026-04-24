const panel = document.getElementById("panelNotify");
const manual = document.getElementById("manualNotify");
const aiAssist = document.getElementById("aiAssistNotify");
const close = document.getElementById("closeNotify");
const addTask = document.getElementById("notify");
const formManual = document.forms[0];
const dateWarning = document.getElementById("dateWarning");
const taskCountThreshold = 3;

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

for (const el of formManual.elements) {
  if (el.name === "deadlineDate") {
    el.addEventListener("change", function() {
      if (this.checkValidity()) {
        fetch("/getTaskCount/" + this.value).then((responce) => {
          if (responce.status != 200) {
            return {count: 0};
          }

          return responce.json();
        }).then((js) => {
            if (js.count >= taskCountThreshold) {
              dateWarning.style.display = "block";
            } else {
              dateWarning.style.display = "none";
            }
          })
      }
    });
  }
}

close.onclick = function() {
  panel.style.display = "none";
}

addTask.onclick = function() {
  panel.style.display = "flex";
}
