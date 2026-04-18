document.addEventListener("DOMContentLoaded", () => {
  const img = document.getElementById("heroImg");
  if (!img) return;

  const delay = Math.random() * 600 + 300;

  setTimeout(() => {
    img.classList.add("show");
  }, delay);
});