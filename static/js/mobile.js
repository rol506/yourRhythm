const btn = document.getElementById("mobileMenu");
const btnClose = document.getElementById("closeMobileMenu");
const aside = document.getElementById("aside");

function op() {
  aside.classList.add("open");
}

function cl() {
  aside.classList.remove("open");
}

btn.onclick = op;
btnClose.onclick = cl;
