
let chart;
let tasks;
let taskStats;

const tasklist = document.getElementById("tasks");
const graph = document.getElementById("graph");
const ctx = document.getElementById("completion");
const chartText = document.getElementById("chartText");

let d = new Date();
let s = "" + d.getDate() + "-" + (1+Number(d.getMonth())) + "-" + d.getFullYear();
let xhr = new XMLHttpRequest();
xhr.open("GET", "/getTasks/" + s, false);
xhr.send(null);
if (xhr.status === 200) {
  if (!xhr.responseText) {tasks = [];}
  else {tasks = JSON.parse(xhr.responseText)}
} else {
  alert("Ошибка! Невозможно получить данные о заданиях: " + xhr.status);
}

s = "" + (Number(d.getDate())-d.getDay()+1) + "-" + (1+Number(d.getMonth())) + "-" + d.getFullYear();
xhr = new XMLHttpRequest();
xhr.open("GET", "/getCompletionStats/" + s, false);
xhr.send(null);
if (xhr.status === 200) {
  if (!xhr.responseText) {taskStats = [];}
  else {taskStats = JSON.parse(xhr.responseText).tasks}
} else {
  alert("Ошибка! Невозможно получить данные о заданиях: " + xhr.status);
}

const data = {
  labels: ["Выполнено", "Не выполнено"],
  datasets: [{
    data: [completed, all-completed],
    backgroundColor: ['#87896F', '#c0bbba'],
    hoverOffset: 5,
  }]
};

const graphData = {
  labels: ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
  datasets: [{
    data: [0, 0, 0, 0, 0, 0, 0],
    fill: false,
    borderColor: '#cdc8c8',
    backgroundColor: '#cdc8c8'
  }]
};

for (var t of taskStats) {
  let d = new Date(Date.parse(t.completionDate));
  let idx = d.getDay() - 1;
  graphData.datasets[0].data[idx]++;
  console.log(idx);
}

let html = "<ul class='tasklist-expand'>";
for (var t of tasks) {
  html += `<li style='color: black;' id="task-${t.id}" class="${(t.isDone == 1 ? "done ":"")}task task-${t.priority}"><ul><li class="phone">${t.task}</li>`;
  html += `<li class="secondary">${t.deadline.substr(0, t.deadline.length-3)}</li></ul>`;
  html += `<span class="check${(t.isDone == 1 ? " checked":"")}" onclick="toggleTask(this, ${t.id})"></span></li>`;
}
html += "</ul>";
tasklist.innerHTML = "<div class='block'><span>Задачи на сегодня:</span></div>" + html;

chartText.innerHTML = Math.round(completed / all * 100) + "%";
chart = new Chart(ctx, {
  type: 'doughnut',
  data: data,
  options: {
    cutout: "60%",
    responsive: false,
    plugins: {
      legend: {
        display: true,
        position: "bottom",
      },
    },
    elements: {
      center: {
        text: "ladno",
        color: "black"
      }
    }
  },
});

graphChart = new Chart(graph, {
  type: 'bar',
  data: graphData,
  options: {
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          stepSize: 1
        }
      }
    }
  },
});

loader.style.display = "none";

function updateCharts() {

  let d = new Date();
  let s = "" + d.getDate() + "-" + (1+Number(d.getMonth())) + "-" + d.getFullYear();
  let xhr = new XMLHttpRequest();
  xhr.open("GET", "/getTasks/" + s, false);
  xhr.send(null);
  if (xhr.status === 200) {
    if (!xhr.responseText) {tasks = [];}
    else {tasks = JSON.parse(xhr.responseText)}
  } else {
    alert("Ошибка! Невозможно получить данные о заданиях: " + xhr.status);
  }

  s = "" + (Number(d.getDate())-d.getDay()+1) + "-" + (1+Number(d.getMonth())) + "-" + d.getFullYear();
  xhr = new XMLHttpRequest();
  xhr.open("GET", "/getCompletionStats/" + s, false);
  xhr.send(null);
  if (xhr.status === 200) {
    if (!xhr.responseText) {taskStats = [];}
    else {taskStats = JSON.parse(xhr.responseText).tasks}
  } else {
    alert("Ошибка! Невозможно получить данные о заданиях: " + xhr.status);
  }

  const data = {
    labels: ["Выполнено", "Не выполнено"],
    datasets: [{
      data: [completed, all-completed],
      backgroundColor: ['#87896F', '#c0bbba'],
      hoverOffset: 5,
    }]
  };

  const graphData = {
    labels: ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
    datasets: [{
      data: [0, 0, 0, 0, 0, 0, 0],
      fill: false,
      borderColor: '#cdc8c8',
      backgroundColor: '#cdc8c8'
    }]
  };

  for (var t of taskStats) {
    let d = new Date(Date.parse(t.completionDate));
    let idx = d.getDay() - 1;
    graphData.datasets[0].data[idx]++;
    console.log(idx);
  }

  let html = "<ul class='tasklist-expand'>";
  for (var t of tasks) {
    html += `<li style='color: black;' id="task-${t.id}" class="${(t.isDone == 1 ? "done ":"")}task task-${t.priority}"><ul><li class="phone">${t.task}</li>`;
    html += `<li class="secondary">${t.deadline.substr(0, t.deadline.length-3)}</li></ul>`;
    html += `<span class="check${(t.isDone == 1 ? " checked":"")}" onclick="toggleTask(this, ${t.id})"></span></li>`;
  }
  html += "</ul>";
  tasklist.innerHTML = "<div class='block'><span>Задачи на сегодня:</span></div>" + html;

  chartText.innerHTML = Math.round(completed / all * 100) + "%";

  chart.data = data;
  chart.update();

  graphChart.data = graphData;
  graphChart.update();
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
          completed--;
          updateCharts();
          //window.location.reload();
          //chart.data.datasets.forEach((dataset) => {
          //  dataset.data = [completed, all-completed]
          //});
          //chart.update();
          //chartText.innerHTML = Math.round(completed / all * 100) + "%";
        })
      } else {
        fetch("/markDoneTask/" + id).then((_) => {
          el.classList.add("checked");
          document.getElementById("task-" + id).classList.add("done");
          completed++;
          updateCharts();
          //window.location.reload();
          //chart.data.datasets.forEach((dataset) => {
          //  dataset.data = [completed, all-completed]
          //});
          //chart.update();
          //hartText.innerHTML = Math.round(completed / all * 100) + "%";
        })
      }
    })
}


