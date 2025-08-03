async function addInterest() {
  const ticker = document.getElementById("ticker").value;
  await fetch("/api/interests", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ticker })
  });
  loadInterests();
}

async function loadInterests() {
  const res = await fetch("/api/interests");
  const data = await res.json();
  document.getElementById("ticker-list").innerHTML = data.map(t => `<li>${t}</li>`).join("");
}

window.onload = loadInterests;
