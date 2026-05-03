const symbolMap = {
  1: "🍒",
  2: "🍋",
  3: "💎",
  4: "7️⃣"
};

async function loadHistory() {
  const tbody = document.getElementById("historyBody");
  if (!tbody) return;

  const username = localStorage.getItem("username");

  if (!username) {
    tbody.innerHTML = `
      <tr>
        <td colspan="6" class="history-empty">
          Log in to view history
        </td>
      </tr>
    `;
    return;
  }

  try {
    const res = await fetch(`/history?username=${encodeURIComponent(username)}`);
    const data = await res.json();

    if (!data.success) {
      tbody.innerHTML = `
        <tr>
          <td colspan="6" class="history-empty">Loading error</td>
        </tr>
      `;
      return;
    }

    if (!Array.isArray(data.history) || data.history.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="6" class="history-empty">No history</td>
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

      const resultSymbols = Array.isArray(item.result)
        ? item.result.map(r => symbolMap[r] || "?").join(" ")
        : "-";

      let time = "-";
      try {
        time = new Date(item.timestamp).toLocaleString();
      } catch {}

      tr.innerHTML = `
        <td>${item.game || "-"}</td>
        <td>${item.bet ?? "-"}$</td>
        <td>${resultSymbols}</td>
        <td>${item.win > 0 ? "+" + item.win : item.win}$</td>
        <td>${item.final_balance ?? "-"}$</td>
        <td>${time}</td>
      `;

      tbody.appendChild(tr);
    });

  } catch (err) {
    console.error("History error:", err);

    tbody.innerHTML = `
      <tr>
        <td colspan="6" class="history-empty">
          Server connection error
        </td>
      </tr>
    `;
  }
}

async function clearHistory() {
  const username = localStorage.getItem("username");
  if (!username) return;

  const confirmDelete = confirm("Are you sure you want to delete your history");
  if (!confirmDelete) return;

  try {
    const res = await fetch("/history/clear", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username })
    });

    const data = await res.json();

    if (!data.success) {
      alert(data.message || "Error deleting history");
      return;
    }

    await loadHistory();

  } catch (err) {
    console.error(err);
    alert("Server connection error");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadHistory();

  const btn = document.getElementById("clearHistoryBtn");
  if (btn) {
    btn.addEventListener("click", clearHistory);
  }
});