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
  const playerId = localStorage.getItem("player_id");
  const username = localStorage.getItem("username");
  const authBox = document.getElementById("authBox");

  if (!authBox) return;

  if (playerId && username) {
    authBox.innerHTML = `
      <span>👤 ${username}</span>
      <span id="balanceDisplay">Balance: ...</span>
      <button class="btn ghost logout-btn">Log out</button>
    `;
  } else {
    authBox.innerHTML = `
      <a class="btn ghost login-link" href="/login-page">Log in</a>
      <a class="btn primary login-link" href="/login-page?mode=register">Sign up</a>
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
  const playerId = localStorage.getItem("player_id");
  if (!playerId) return;

  try {
    const res = await fetch("/balance", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ player_id: parseInt(playerId) })
    });

    const data = await res.json();

    if (data.success) {
      const el = document.getElementById("balanceDisplay");
      if (el) {
        el.textContent = `Balance: ${data.balance}$`;
      }
    }

  } catch {
    console.log("Balance error");
  }
}

function goToSlots() {
  const playerId = localStorage.getItem("player_id");

  if (playerId) {
    window.location.href = "/slots";
  } else {
    window.location.href = "/login-page";
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