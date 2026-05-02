document.addEventListener("DOMContentLoaded", () => {

  const loginForm = document.getElementById('loginForm');
  const registerForm = document.getElementById('registerForm');
  const loginToggle = document.getElementById('loginToggle');
  const registerToggle = document.getElementById('registerToggle');

  const loginUsername = document.getElementById('loginUsername');
  const loginPassword = document.getElementById('loginPassword');

  const regUsername = document.getElementById('regUsername');
  const regEmail = document.getElementById('regEmail');
  const regPassword = document.getElementById('regPassword');
  const regPassword2 = document.getElementById('regPassword2');

  loginToggle.onclick = () => {
    loginForm.classList.remove('hidden');
    registerForm.classList.add('hidden');
  };

  registerToggle.onclick = () => {
    registerForm.classList.remove('hidden');
    loginForm.classList.add('hidden');
  };

  loginForm.onsubmit = async (e) => {
    e.preventDefault();

    const username = loginUsername.value.trim();
    const password = loginPassword.value;

    try {
      const res = await fetch(`/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
      });

      const data = await res.json();

      if (!data.success) {
        alert(data.message || "Błąd logowania");
        return;
      }

      localStorage.setItem("username", username);
      localStorage.setItem("player_id", data.player_id);

      const redirect = localStorage.getItem("redirectAfterLogin");

      if (redirect && !redirect.includes("login")) {
        localStorage.removeItem("redirectAfterLogin");
        window.location.href = redirect;
      } else {
        window.location.href = "index.html";
      }

    } catch {
      alert("Brak połączenia z serwerem");
    }
  };

  registerForm.onsubmit = async (e) => {
    e.preventDefault();

    const username = regUsername.value.trim();
    const email = regEmail.value.trim();
    const password = regPassword.value;
    const password2 = regPassword2.value;

    if (password !== password2) {
      alert("Hasła się nie zgadzają!");
      return;
    }

    try {
      const res = await fetch(`/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, email, password })
      });

      const data = await res.json();

      if (!data.success) {
        alert(data.message || "Błąd rejestracji");
        return;
      }

      alert("Konto utworzone!");
      registerForm.classList.add('hidden');
      loginForm.classList.remove('hidden');

    } catch {
      alert("Brak połączenia z serwerem");
    }
  };

  const params = new URLSearchParams(window.location.search);
  const mode = params.get("mode");

  if (mode === "register") {
    registerForm.classList.remove("hidden");
    loginForm.classList.add("hidden");
  } else {
    loginForm.classList.remove("hidden");
    registerForm.classList.add("hidden");
  }

});