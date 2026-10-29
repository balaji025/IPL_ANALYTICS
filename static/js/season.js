// Season page: champion, caps, points table, playoffs, leaders, every match.

const year = Number($("#hero").dataset.year);

async function loadSeason() {
  const [seasons, s, matches] = await Promise.all([
    api("/seasons"), api(`/seasons/${year}`), api(`/matches?season=${year}&limit=200`),
  ]);

  const champ = window.TEAMS[s.champion] || {};
  document.documentElement.style.setProperty("--accent", champ.colour || "#2f6bff");

  // Season picker (oldest first)
  $("#years").innerHTML = seasons.slice().reverse().map(x =>
    `<a class="pill ${x.season === year ? "on" : "light"}" href="/seasons/${x.season}">${x.season}</a>`).join("");
  // Centre the selected year inside the strip (scrolling only the strip, not the page)
  const strip = $("#years"), current = $("#years .on");
  if (current) strip.scrollLeft = current.offsetLeft - strip.offsetLeft - strip.clientWidth / 2 + current.offsetWidth / 2;

  // Champion
  $("#champion").innerHTML = `
    <a href="/teams/${champ.short}" style="display:inline-flex;align-items:center;gap:16px">
      ${badge(s.champion)}
      <span><span class="muted">Champions</span><br><b style="font-size:1.3rem">${esc(s.champion)}</b>
      <span class="muted"> · beat ${esc(s.runner_up)}</span></span>
    </a>`;

  // Counters
  const counters = [[s.matches, "Matches"], [s.summary.runs, "Runs"], [s.summary.sixes, "Sixes"], [s.summary.run_rate, "Runs per over"]];
  $("#counters").innerHTML = counters.map(([v, label]) =>
    `<div class="counter"><b>${num(v)}</b><span class="muted">${label}</span></div>`).join("");

  // Caps
  const cap = (label, c, value) => `
    <a class="card reveal" href="/players/${c.player.player_id}" style="display:flex;gap:18px;align-items:center">
      ${avatar(c.player)}
      <div><p class="eyebrow" style="margin:0">${label}</p><h3>${esc(c.player.name)}</h3><p class="muted">${value}</p></div>
    </a>`;
  $("#caps").innerHTML = cap("Orange Cap · most runs", s.orange_cap, num(s.orange_cap.runs) + " runs")
                       + cap("Purple Cap · most wickets", s.purple_cap, num(s.purple_cap.wickets) + " wickets");

  // Points table
  $("#table").innerHTML = `<table>
    <tr><th>Team</th><th>P</th><th>W</th><th>L</th><th>NR</th><th>Pts</th><th>NRR</th></tr>
    ${s.points_table.map(r => `
      <tr>
        <td><a href="/teams/${r.short}" style="display:flex;align-items:center;gap:12px">
          <span class="muted" style="width:18px">${r.position}</span>${badge(r.team)}
          <span class="long-name">${esc(r.team)}</span><span class="short-name">${esc(r.short)}</span></a></td>
        <td>${r.played}</td><td>${r.won}</td><td>${r.lost}</td><td>${r.no_result}</td>
        <td><b>${r.points}</b></td><td>${r.nrr > 0 ? "+" : ""}${r.nrr.toFixed(3)}</td>
      </tr>`).join("")}
  </table>`;

  // Playoffs (oldest first so the final is last)
  $("#playoffs").innerHTML = matches.filter(m => m.stage !== "League").reverse().map(matchRow).join("");

  // Leaders
  $("#top-bat").innerHTML = playerList(s.top_run_scorers.slice(0, 5), p => num(p.runs),
    p => `${p.innings} inns · avg ${p.average ?? "–"} · SR ${p.strike_rate}`);
  $("#top-bowl").innerHTML = playerList(s.top_wicket_takers.slice(0, 5), p => num(p.wickets),
    p => `${p.innings} inns · econ ${p.economy} · avg ${p.average ?? "–"}`);

  // Every match: first 10, then all on request
  const league = matches.filter(m => m.stage === "League");
  const show = n => {
    $("#matches").innerHTML = league.slice(0, n).map(matchRow).join("");
    reveal();
  };
  show(10);
  $("#show-all").addEventListener("click", e => { show(league.length); e.target.remove(); });

  reveal();
}

loadSeason();
