
let loader = document.getElementById("loader");
let logout = document.getElementById("logout");
let prev = document.getElementById("prevMonth");
let next = document.getElementById("nextMonth");
let label = document.getElementById("calLabel");
let focused = [];

function formatDateTime(d) {
  return "" + d.getDate() + "-" + d.getMonth() + "-" + d.getFullYear() + " " + d.getHours() + ":" + d.getMinutes();
}

function toggleTask(el, id) {
  fetch("/getTask/" + id).then((responce) => {
    if (responce.status != 200) {
      return;
    }

    return responce.json();}).then((js) => {
      if (js.isDone == "1") {
        fetch("/undoTask/" + id).then((_) => {
          el.classList.remove("checked");
          document.getElementById("task-" + id).classList.remove("done");
        })
      } else {
        fetch("/markDoneTask/" + id).then((_) => {
          el.classList.add("checked");
          document.getElementById("task-" + id).classList.add("done");
        })
      }
    })
}

var Cal = function(divId) {
  this.divId = divId;
  this.DaysOfWeek = [
    'Понедельник',
    'Вторник',
    'Среда',
    'Четверг',
    'Пятница',
    'Суббота',
    'Воскресенье'
  ];
  this.ShortDaysOfWeek = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"];
  this.Months =['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'];
  var d = new Date();
  this.currMonth = d.getMonth();
  this.currYear = d.getFullYear();
  this.currDay = d.getDate();
};
Cal.prototype.showcurr = function() {
  this.showMonth(this.currYear, this.currMonth);
}
Cal.prototype.nextMonth = function() {
  label.innerHTML = "Загрузка...";
  loader.style.display = "flex";
  if ( this.currMonth == 11 ) {
    this.currMonth = 0;
    this.currYear = this.currYear + 1;
  }
  else {
    this.currMonth = this.currMonth + 1;
  }
  this.showcurr();
};
Cal.prototype.previousMonth = function() {
  label.innerHTML = "Загрузка...";
  loader.style.display = "flex";
  if ( this.currMonth == 0 ) {
    this.currMonth = 11;
    this.currYear = this.currYear - 1;
  }
  else {
    this.currMonth = this.currMonth - 1;
  }
  this.showcurr();
};
Cal.prototype.showMonth = function(y, m) {

  label.innerHTML = this.Months[this.currMonth] + ", " + this.currYear;

  var d = new Date(),
  firstDayOfMonth = new Date(y, m, 7).getDay(),
  lastDateOfMonth =  new Date(y, m+1, 0).getDate(),
  lastDayOfLastMonth = m == 0 ? new Date(y-1, 11, 0).getDate() : new Date(y, m, 0).getDate();
  var html = '<table class="calendar">';
  //html += '<thead><tr>';
  //html += '<td colspan="7">' + this.Months[m] + ' ' + y + '</td>';
  //html += '</tr></thead>';
  html += '<tr class="days pc">';
  for(var i=0; i < this.DaysOfWeek.length;i++) {
    if (i >= 5)
    {
      html += '<td style="text-align: center;">' + this.DaysOfWeek[i] + '</td>';
    } else {
      html += '<td style="text-align: center;">' + this.DaysOfWeek[i] + '</td>';
    }
  }
  html += '</tr><tr class="days phone">';
  for(var i=0;i<this.ShortDaysOfWeek.length;i++) {
    html += '<td style="text-align: center;">' + this.ShortDaysOfWeek[i] + '</td>';;
  }
  html += "</td>";
  var i=1;
  do {
    var dow = new Date(y, m, i).getDay();
    if ( dow == 1 ) {
      html += '<tr>';
    }
    else if ( i == 1 ) {
      html += '<tr>';
      var k = lastDayOfLastMonth - firstDayOfMonth+1;
      for(var j=0; j < firstDayOfMonth; j++) {
        html += '<td class="not-current" onclick="foc(this)"><span>' + k + '</span><div class="task-wrapper">';
        var s = "" + k + "-" + this.currMonth + "-" + this.currYear;
        let xhr = new XMLHttpRequest();
        xhr.open("GET", "/getTasks/" + s, false);
        xhr.send(null);
        if (xhr.status === 200) {
          if (!xhr.responseText) {this.data = [];}
          else {this.data = JSON.parse(xhr.responseText)}
        } else {
          alert("Ошибка! Невозможно получить данные о заданиях: " + xhr.status);
          return;
        }
        html += "<ul class='tasklist'>";
        let panel = "<div class='tasklist-panel'><p class='title'>Задания:</p><ul class='tasklist-expand'>";
        for (const task of this.data) {
          s += `<li id='task-${task.id}' class='${(task.isDone == 1 ? "done" : "")} task task-` + task.priority + `'>` + task.task + "</li>";
          panel += "<li class='task task-" + task.priority + "'><ul><li>"
            + task.task + "</li><li class='secondary'>" + task.deadline.substring(0, task.deadline.length-3) + "</li></ul><span class='check" 
            + (task.isDone == "1" ? " checked" : "") + `' onclick='toggleTask(this, ${task.id})'></span></li>`;
        }
        panel += "</ul></div>";
        html += "</ul>";
        html += panel + '</div></td>';
        k++;
      }
      d.setMonth(d.getMonth() +1);
    }
    var chk = new Date();
    var chkY = chk.getFullYear();
    var chkM = chk.getMonth();
    var s = "";
    var ss = "" + i + "-" + (1+Number(this.currMonth)) + "-" + this.currYear;
    let xhr = new XMLHttpRequest();
    xhr.open("GET", "/getTasks/" + ss, false);
    xhr.send(null);
    if (xhr.status === 200) {
      if (!xhr.responseText) {this.data = [];}
      else {this.data = JSON.parse(xhr.responseText);}
    } else {
      alert("Ошибка! Невоможно получить данные о заданиях: " + xhr.status);
      return;
    }
    s += "<ul class='tasklist'>";
    let panel = "<div class='tasklist-panel'><p class='title'>Задания:</p><ul class='tasklist-expand'>";
    for (const task of this.data) {
      s += `<li id='task-${task.id}' class='${(task.isDone == 1 ? "done" : "")} task task-` + task.priority + `'>` + task.task + "</li>";
      panel += "<li class='task task-" + task.priority + "'><ul><li>"
        + task.task + "</li><li class='secondary'>" + task.deadline.substring(0, task.deadline.length-3) + "</li></ul><span class='check" 
        + (task.isDone == "1" ? " checked" : "") + `' onclick='toggleTask(this, ${task.id})'></span></li>`;
    }
    panel += "</ul></div>";
    s += "</ul>";
    html += '</td>';
    if (chkY == this.currYear && chkM == this.currMonth && i == this.currDay) {
      html += `<td class="today" onclick="foc(this)"><span>` + i + `</span><div class="task-wrapper">`
        + s + panel + '</div></td>';
    } else {
      html += '<td class="normal" onclick="foc(this)"><span>' + i + '</span><div class="task-wrapper">'
        + s + panel + '</div></td>';
    }
    if ( dow == 0 ) {
      html += '</tr>';
    }
    else if ( i == lastDateOfMonth ) {
      var k=1;
      for(dow; dow < 7; dow++) {
        html += '<td class="not-current">' + k + '</td>';
        k++;
      }
    }
    i++;
  }while(i <= lastDateOfMonth);
  html += '</table>';
  document.getElementById(this.divId).innerHTML = html;
  loader.style.display = "none";
};
window.onload = function() {
  var c = new Cal("calendar");
  c.showcurr();
  getId('nextMonth').onclick = function() {
    c.nextMonth();
  };
  getId('prevMonth').onclick = function() {
    c.previousMonth();
  };
}
logout.onclick = function() {
  fetch("/logout").then(() => {window.location.href = "/login";})
}
function getId(id) {
  return document.getElementById(id);
}

function foc(el) {
  if (el.classList.contains("focused")) {
    el.classList.remove("focused");
    for (i=0;i<focused.length;++i) {
      focused[i].classList.remove("focused");
    }
    focused = [];
  } else {
    for (i=0;i<focused.length;++i) {
      focused[i].classList.remove("focused");
    }
    focused = [];
    focused.push(el);
    el.classList.add("focused")
  }
}
