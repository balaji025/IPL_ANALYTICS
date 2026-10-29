// Teams page: current and former franchises, plus a head-to-head picker.

async function loadTeams() {
  const teams = await api("/teams");
  const current = teams.filter(t => t.active);
  const former = teams.filter(t => !t.active);

  $("#current").innerHTML = current.map(t => `
    <a class="card reveal" href="/teams/${t.short}">
      <div style="display:flex;justify-content:space-between;align-items:start">
        ${badge(t.name, "lg")}
        <span class="chip">${t.first_season}–${t.last_season}</span>
      </div>
      <h3 style="margin-top:18px;font-size:1.3rem">${esc(t.name)}</h3>
      <p class="muted">${t.record.played} played · ${t.record.won} won · ${t.record.win_pct}% wins</p>
      <div class="chips" style="margin-top:14px">
        ${t.titles.length ? t.titles.map(y => `<span class="chip">🏆 ${y}</span>`).join("") : `<span class="muted">No titles yet</span>`}
      </div>
    </a>`).join("");

  $("#former").innerHTML = former.map(t => `
    <a class="row reveal" href="/teams/${t.short}">
      ${badge(t.name)}
      <span class="grow">${esc(t.name)}<br><span class="muted" style="font-size:.85rem">${t.first_season}–${t.last_season}</span></span>
      <span class="num">${t.record.won}–${t.record.lost}</span>
    </a>`).join("");

  // Head-to-head picker
  const options = teams.map(t => `<option value="${t.short}">${esc(t.name)}</option>`).join("");
  $("#vs-a").innerHTML = options;
  $("#vs-b").innerHTML = options;
  $("#vs-a").value = "CSK";
  $("#vs-b").value = "MI";
  $("#vs-go").addEventListener("click", () => {
    const a = $("#vs-a").value, b = $("#vs-b").value;
    if (a !== b) location.href = `/teams/${a}/vs/${b}`;
  });

  reveal();
}

loadTeams();
