window.addEventListener("load", () => {
    const img = document.getElementById("heroImg");
  
    // losowe opóźnienie – bardziej "anonimowo"
    const delay = Math.random() * 600 + 300;
  
    setTimeout(() => {
      img.classList.add("show");
    }, delay);
  });
  