const symbolMap = {
  1: "🍒",
  2: "🍋",
  3: "💎",
  4: "7️⃣"
};

async function loadHistory() {
  const username = localStorage.getItem("username");
  if (!username) return;

  try {
    const res = await fetch(`/history?username=${username}`);
    const data = await res.json();

    if (!data.success) return;

    const tbody = document.getElementById("historyBody");
    if (!tbody) return;

    if (data.history.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="6" class="history-empty">Brak historii</td>
        </tr>
      `;
      return;
    }

    tbody.innerHTML = "";

    data.history.forEach((item, index) => {
      const tr = document.createElement("tr");

      tr.className = item.win > 0 ? "win-row" : "lose-row";

      if (index === 0) {
        tr.style.background = "rgba(0,255,200,0.1)";
      }

      const resultSymbols = item.result
        .map(r => symbolMap[r] || "?")
        .join(" ");

      const time = new Date(item.timestamp).toLocaleString();

      tr.innerHTML = `
        <td>${item.game}</td>
        <td>${item.bet}</td>
        <td>${resultSymbols}</td>
        <td>${item.win > 0 ? "+" + item.win : item.win}</td>
        <td>${item.final_balance}</td>
        <td>${time}</td>
      `;

      tbody.appendChild(tr);
    });

  } catch (err) {
    console.log("History error:", err);
  }
}

window.loadHistory = loadHistory;

document.addEventListener("DOMContentLoaded", loadHistory);