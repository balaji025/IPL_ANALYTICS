// Records page: leaderboards, filtered by season and/or team through the URL (?season=&team=).

const params = new URLSearchParams(location.search);

async function loadRecords() {
  const [seasons, teams] = await Promise.all([api("/seasons"), api("/teams")]);

  // Filters: changing one reloads the page with the new query string
  $("#season").innerHTML += seasons.map(s => `<option value="${s.season}">${s.season}</option>`).join("");
  $("#team").innerHTML += teams.map(t => `<option value="${t.short}">${esc(t.name)}</option>`).join("");
  $("#season").value = params.get("season") || "";
  $("#team").value = params.get("team") || "";
  for (const id of ["season", "team"]) {
    $("#" + id).addEventListener("change", () => {
      const next = new URLSearchParams();
      if ($("#season").value) next.set("season", $("#season").value);
      if ($("#team").value) next.set("team", $("#team").value);
      location.search = next.toString();
    });
  }
  const scope = [params.get("season") ? `IPL ${params.get("season")}` : "All seasons",
                 params.get("team") ? `${params.get("team")} players` : "all teams"];
  $("#scope").textContent = scope.join(", ") + ".";

  const r = await api("/records?limit=10&" + params.toString());
  const bat = p => `${p.innings} inns · avg ${p.average ?? "–"} · SR ${p.strike_rate}`;
  const bowl = p => `${p.innings} inns · econ ${p.economy} · avg ${p.average ?? "–"}`;
  const vs = p => `v ${esc(teamShort(p.opponent))}, ${p.season}`;

  const boards = [
    ["Most runs", playerList(r.most_runs, p => num(p.runs), bat)],
    ["Most wickets", playerList(r.most_wickets, p => num(p.wickets), bowl)],
    ["Highest scores", playerList(r.highest_scores, p => `${p.runs}${p.is_out ? "" : "*"} <span class="muted">(${p.balls})</span>`, vs)],
    ["Best bowling", playerList(r.best_bowling, p => `${p.wickets}/${p.runs}`, vs)],
    ["Most sixes", playerList(r.most_sixes, p => num(p.sixes), p => `${p.innings} innings`)],
    ["Best strike rate", playerList(r.best_strike_rate, p => p.strike_rate, p => `${num(p.runs)} runs · ${num(p.balls)} balls`)],
    ["Best economy", playerList(r.best_economy, p => p.economy, p => `${p.overs} overs · ${p.wickets} wickets`)],
    ["Highest team totals", r.highest_totals.map((t, i) => `
      <a class="row reveal" href="/matches/${t.match_id}">
        <span class="muted" style="width:20px">${i + 1}</span>${badge(t.team)}
        <span class="grow">${esc(t.team)}<br><span class="muted" style="font-size:.85rem">v ${esc(teamShort(t.opponent))}, ${t.season}</span></span>
        <span class="num">${esc(t.score)}</span>
      </a>`).join("")],
  ];
  $("#boards").innerHTML = boards.map(([title, html]) => `
    <div><h2 class="reveal" style="font-size:1.6rem;margin-bottom:12px">${title}</h2><div class="list">${html}</div></div>`).join("");

  reveal();
}

loadRecords();
