// Home page: counters, champion, seasons strip, record highlights, teams.

async function loadHome() {
  const [index, seasons, teams, records] = await Promise.all([
    api(""), api("/seasons"), api("/teams"), api("/records?limit=1"),
  ]);
  const meta = index.meta;
  const latest = await api("/seasons/" + meta.last_season);

  // Big counters in the hero
  const counters = [
    ["matches", "Matches"], ["runs", "Runs scored"], ["sixes", "Sixes hit"], ["players", "Players"],
  ];
  $("#counters").innerHTML = counters.map(([key, label]) =>
    `<div class="counter"><b data-count="${meta[key]}">0</b><span class="muted">${label}</span></div>`).join("");
  document.querySelectorAll("[data-count]").forEach(el => countUp(el, Number(el.dataset.count)));

  // Logo marquee: the list twice so the loop is seamless
  const logos = Object.keys(window.TEAMS).filter(name => window.TEAMS[name].logo);
  const strip = logos.map(name => `<img src="/static/images/teams/${window.TEAMS[name].short}.webp" alt="">`).join("");
  $("#marquee").innerHTML = strip + strip;

  // Latest champion
  const final = latest.playoffs.find(m => m.stage === "Final");
  const champ = window.TEAMS[latest.champion] || {};
  document.documentElement.style.setProperty("--accent", champ.colour || "#2f6bff");
  $("#champion").innerHTML = `
    <div class="section-head reveal">
      <div><p class="eyebrow">IPL ${latest.season} champions</p><h2>${esc(latest.champion)}</h2></div>
      <a class="pill light" href="/seasons/${latest.season}">Season ${latest.season} &rarr;</a>
    </div>
    <div class="grid grid-3">
      <div class="card reveal" style="display:flex;gap:18px;align-items:center">
        ${badge(latest.champion)}
        <div><h3>${esc(final ? final.result_text : "")}</h3><p class="muted">Final · ${esc(final ? final.venue : "")}</p></div>
      </div>
      ${capCard("Orange Cap", latest.orange_cap.player, num(latest.orange_cap.runs) + " runs")}
      ${capCard("Purple Cap", latest.purple_cap.player, num(latest.purple_cap.wickets) + " wickets")}
    </div>`;

  // Seasons strip
  $("#seasons").innerHTML = seasons.map(s => `
    <a class="card" href="/seasons/${s.season}" style="width:220px">
      <p class="eyebrow">${s.season}</p>
      ${badge(s.champion)}
      <h3 style="margin-top:14px">${esc(s.champion)}</h3>
      <p class="muted" style="font-size:.85rem">beat ${esc(teamShort(s.runner_up))}</p>
    </a>`).join("");

  // Record highlights
  const top = records.highest_scores[0];
  const bowl = records.best_bowling[0];
  const total = records.highest_totals[0];
  const runs = records.most_runs[0];
  $("#records").innerHTML = [
    recordCard("Most runs", num(runs.runs), runs.name, `/players/${runs.player_id}`),
    recordCard("Highest score", top.runs + (top.is_out ? "" : "*"), `${top.name} · ${top.balls} balls, ${top.season}`, `/players/${top.player_id}`),
    recordCard("Best bowling", `${bowl.wickets}/${bowl.runs}`, `${bowl.name} · ${bowl.season}`, `/players/${bowl.player_id}`),
    recordCard("Highest total", total.score, `${total.team} v ${teamShort(total.opponent)}, ${total.season}`, `/matches/${total.match_id}`),
  ].join("");

  // Teams grid (current franchises)
  $("#teams").innerHTML = teams.filter(t => t.active).map(t => `
    <a class="card reveal" href="/teams/${t.short}">
      ${badge(t.name)}
      <h3 style="margin-top:16px">${esc(t.name)}</h3>
      <p class="muted" style="font-size:.85rem">${t.titles.length ? t.titles.length + " title" + (t.titles.length > 1 ? "s" : "") : "No titles yet"}</p>
    </a>`).join("");

  reveal();
}

function capCard(label, player, value) {
  return `
    <a class="card reveal" href="/players/${player.player_id}" style="display:flex;gap:18px;align-items:center">
      ${avatar(player)}
      <div><p class="eyebrow" style="margin:0">${label}</p><h3>${esc(player.name)}</h3><p class="muted">${value}</p></div>
    </a>`;
}

function recordCard(label, value, detail, href) {
  return `
    <a class="card tile reveal" href="${href}">
      <p class="eyebrow">${label}</p>
      <b>${esc(value)}</b>
      <span>${esc(detail)}</span>
    </a>`;
}

loadHome();
