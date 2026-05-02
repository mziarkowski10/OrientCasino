const username = localStorage.getItem("username");

if (!username) window.location.href = "login.html";

const spinSound = new Audio("/static/assets/spin.mp3");
const winSound = new Audio("/static/assets/win.mp3");

const symbolMap = {
  1: "🍒",
  2: "🍋",
  3: "💎",
  4: "7️⃣"
};

const symbols = ["🍒", "🍋", "💎", "7️⃣"];

const reels = [
  document.getElementById("reel1"),
  document.getElementById("reel2"),
  document.getElementById("reel3")
];

const spinBtn = document.getElementById("spinBtn");
const resultText = document.getElementById("resultText");
const betInput = document.getElementById("bet");

betInput.addEventListener("input", (e) => {
  let val = e.target.value;

  if (val.includes(".")) {
    const [int, dec] = val.split(".");
    e.target.value = int + "." + dec.slice(0, 2);
  }
});

let spinning = false;

function spinReel(reel) {
  reel.innerHTML = "";

  for (let i = 0; i < 20; i++) {
    const el = document.createElement("span");
    el.textContent = symbols[Math.floor(Math.random() * symbols.length)];
    reel.appendChild(el);
  }

  reel.style.transition = "none";
  reel.style.transform = "translateY(0)";

  setTimeout(() => {
    reel.style.transition = "transform 0.6s cubic-bezier(.17,.67,.83,.67)";
    reel.style.transform = "translateY(-1500px)";
  }, 50);
}

function stopReel(reel, symbol) {
  reel.innerHTML = "";

  const el = document.createElement("span");
  el.textContent = symbol;
  reel.appendChild(el);

  reel.style.transform = "translateY(0)";
}

spinBtn.onclick = async () => {
  if (spinning) return;

  let bet = Number(betInput.value);
  bet = Math.round(bet * 100) / 100;

  if (!bet || bet < 10) {
    resultText.textContent = "Minimalny bet to 10";
    resultText.className = "result lose-text";
    return;
  }

  spinning = true;
  spinBtn.disabled = true;
  betInput.disabled = true;

  resultText.textContent = "";

  try {
    spinSound.currentTime = 0;
    spinSound.play();
  } catch {}

  reels.forEach((reel, i) => {
    setTimeout(() => spinReel(reel), i * 150);
  });

  try {
    const res = await fetch("/slots", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        username,
        bet
      })
    });

    const data = await res.json();

    if (!data.success) {
      resultText.textContent = data.message || "Błąd";
      resultText.className = "result lose-text";
      resetUI();
      return;
    }

    if (!Array.isArray(data.result)) {
      resultText.textContent = "Błąd danych";
      resultText.className = "result lose-text";
      resetUI();
      return;
    }

    reels.forEach((reel, i) => {
      setTimeout(() => {
        stopReel(reel, symbolMap[data.result[i]] || "?");
      }, 1200 + i * 400);
    });

    setTimeout(() => {
      if (data.win > 0) {
        resultText.textContent = "WYGRANA: " + data.win;
        resultText.className = "result win-text";

        try {
          winSound.play();
        } catch {}
      } else {
        resultText.textContent = "Przegrana";
        resultText.className = "result lose-text";
      }

      const balanceEl = document.getElementById("balanceDisplay");

      if (balanceEl && typeof data.balance !== "undefined") {
        balanceEl.textContent = "Saldo: " + data.balance;
      }

      resetUI();
    }, 1200 + 3 * 400);

  } catch (err) {
    console.error(err);
    resultText.textContent = "Błąd połączenia";
    resultText.className = "result lose-text";
    resetUI();
  }
};

function resetUI() {
  spinning = false;
  spinBtn.disabled = false;

  const betInput = document.getElementById("bet");
  if (betInput) betInput.disabled = false;
}