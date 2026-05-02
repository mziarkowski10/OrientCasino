document.addEventListener("DOMContentLoaded", () => {
  initHero();
  setupAuthBox();
  bindNavigation();
  loadBalance();
});

function initHero() {
  const img = document.getElementById("heroImg");
  if (!img) return;

  const delay = Math.random() * 600 + 300;

  setTimeout(() => {
    img.classList.add("show");
  }, delay);
}

function setupAuthBox() {
  const username = localStorage.getItem("username");
  const authBox = document.getElementById("authBox");

  if (!authBox) return;

  if (username) {
    authBox.innerHTML = `
      <span>👤 ${username}</span>
      <span id="balanceDisplay">Saldo: ...</span>
      <button class="btn ghost logout-btn">Wyloguj</button>
    `;
  } else {
    authBox.innerHTML = `
      <span id="balanceDisplay">Saldo: ...</span>
      <a class="btn ghost login-link" href="login.html">Zaloguj</a>
      <a class="btn primary login-link" href="login.html?mode=register">Rejestracja</a>
    `;
  }

  bindLogout();
  setupLoginRedirect();
}

function bindLogout() {
  const btn = document.querySelector(".logout-btn");

  if (btn) {
    btn.addEventListener("click", () => {
      localStorage.removeItem("username");
      localStorage.removeItem("player_id");
      window.location.reload();
    });
  }
}

async function loadBalance() {
  const username = localStorage.getItem("username");
  if (!username) return;

  try {
    const res = await fetch("/balance", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username })
    });

    const data = await res.json();

    if (data.success) {
      const el = document.getElementById("balanceDisplay");
      if (el) {
        el.textContent = `Saldo: ${data.balance}`;
      }
    }

  } catch {
    console.log("Balance error");
  }
}

function goToSlots() {
  const username = localStorage.getItem("username");

  if (username) {
    window.location.href = "slots_game.html";
  } else {
    window.location.href = "login.html";
  }
}

function bindNavigation() {
  document.querySelectorAll(".go-slots").forEach(el => {
    el.addEventListener("click", (e) => {
      e.preventDefault();
      goToSlots();
    });
  });
}

function setupLoginRedirect() {
  document.querySelectorAll(".login-link").forEach(link => {
    link.addEventListener("click", () => {
      localStorage.setItem("redirectAfterLogin", window.location.href);
    });
  });
}