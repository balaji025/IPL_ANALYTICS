// Player page: photo, key numbers, season chart, phases, best/recent, career, matchups.

const playerId = $("#hero").dataset.player;

async function loadPlayer() {
  const [d, mu] = await Promise.all([
    api(`/players/${playerId}`),
    api(`/players/${playerId}/matchups?limit=8`),
  ]);
  const p = d.player;
  const bat = d.batting;
  const bowl = d.bowling;
  // Mostly a bowler? Then show bowling first.
  const isBowler = bowl && bowl.wickets >= 15 && (!bat || bowl.wickets * 25 > bat.runs);

  const team = window.TEAMS[p.last_team];
  if (team) document.documentElement.style.setProperty("--accent", team.colour);

  // Photo
  const src = photoUrl(p.image_url, 640);
  $("#photo").innerHTML = src
    ? `<img class="player-photo" src="${src}" alt="${esc(p.name)}">`
    : `<div class="player-initials">${initials(p.name)}</div>`;

  // Key numbers
  const batTiles = bat ? [
    [num(bat.runs), "Runs"], [bat.average ?? "–", "Average"], [bat.strike_rate ?? "–", "Strike rate"], [bat.high_score, "Highest score"],
  ] : [];
  const bowlTiles = bowl ? [
    [num(bowl.wickets), "Wickets"], [bowl.economy ?? "–", "Economy"], [bowl.best, "Best bowling"],
  ] : [];
  const tiles = [
    [num(p.matches), "Matches"],
    ...(isBowler ? bowlTiles.concat(batTiles.slice(0, 1)) : batTiles.concat(bowlTiles.slice(0, 1))),
    [num(d.fielding.catches), "Catches"],
    [num(d.player_of_match_awards), "Player of the Match"],
  ];
  $("#tiles").innerHTML = tiles.map(([v, label]) =>
    `<div class="card tile reveal"><b>${esc(v)}</b><span>${label}</span></div>`).join("");

  // Season chart with a Batting / Bowling toggle
  const modes = [];
  if (bat) modes.push("Batting");
  if (bowl) modes.push("Bowling");
  if (isBowler) modes.reverse();
  $("#chart-toggle").innerHTML = modes.map(m => `<button class="pill light" data-mode="${m}">${m}</button>`).join("");
  const chart = echarts.init($("#season-chart"));
  window.addEventListener("resize", () => chart.resize());
  const showChart = mode => {
    document.querySelectorAll("#chart-toggle .pill").forEach(b => b.classList.toggle("on", b.dataset.mode === mode));
    $("#chart-title").textContent = mode === "Batting" ? "Runs per season" : "Wickets per season";
    chart.setOption(seasonChart(d.seasons, mode), true);
  };
  $("#chart-toggle").addEventListener("click", e => { if (e.target.dataset.mode) showChart(e.target.dataset.mode); });
  showChart(modes[0]);

  // Phases
  const phaseNames = { powerplay: "Powerplay (1–6)", middle: "Middle (7–15)", death: "Death (16–20)" };
  const order = ["powerplay", "middle", "death"];
  if (!isBowler && d.phases.batting.length) {
    const rows = order.map(name => d.phases.batting.find(r => r.phase === name)).filter(Boolean);
    const max = Math.max(...rows.map(r => r.runs));
    $("#phases").innerHTML = rows.map(r => phaseCard(phaseNames[r.phase], num(r.runs) + " runs",
      `Strike rate ${r.strike_rate ?? "–"} · ${r.outs} outs`, r.runs / max)).join("");
  } else if (d.phases.bowling.length) {
    const rows = order.map(name => d.phases.bowling.find(r => r.phase === name)).filter(Boolean);
    const max = Math.max(...rows.map(r => r.wickets));
    $("#phases").innerHTML = rows.map(r => phaseCard(phaseNames[r.phase], num(r.wickets) + " wickets",
      `Economy ${r.economy ?? "–"} · ${r.overs} overs`, max ? r.wickets / max : 0)).join("");
  } else {
    $("#phases-section").remove();
  }

  // Best performances
  const best = [
    ...d.best_batting.slice(0, 3).map(b => perfRow(b.match_id, b.opponent,
      `${b.runs}${b.is_out ? "" : "*"} <span class="muted">(${b.balls})</span>`, b.season)),
    ...d.best_bowling.slice(0, 3).map(b => perfRow(b.match_id, b.opponent,
      `${b.wickets}/${b.runs}`, b.season)),
  ];
  $("#best").innerHTML = best.join("") || `<p class="muted">No performances yet.</p>`;

  // Recent matches
  $("#recent").innerHTML = d.recent_matches.map(m => {
    const parts = [];
    if (m.runs != null) parts.push(`${m.runs}${m.is_out ? "" : "*"} <span class="muted">(${m.balls})</span>`);
    if (m.wickets != null) parts.push(`${m.wickets}/${m.runs_conceded}`);
    return perfRow(m.match_id, m.opponent, parts.join(" &nbsp;·&nbsp; ") || `<span class="muted">DNB</span>`, m.date);
  }).join("");

  // Career tables
  let html = "";
  if (bat) html += `<table><tr><th>Batting</th><th>Inn</th><th>Runs</th><th>HS</th><th>Avg</th><th>SR</th><th>100s</th><th>50s</th><th>4s</th><th>6s</th></tr>
    <tr><td>IPL</td><td>${bat.innings}</td><td>${num(bat.runs)}</td><td>${bat.high_score}</td><td>${bat.average ?? "–"}</td>
    <td>${bat.strike_rate ?? "–"}</td><td>${bat.hundreds}</td><td>${bat.fifties}</td><td>${bat.fours}</td><td>${bat.sixes}</td></tr></table>`;
  if (bowl) html += `<table style="margin-top:24px"><tr><th>Bowling</th><th>Inn</th><th>Overs</th><th>Wkts</th><th>Best</th><th>Avg</th><th>Econ</th><th>SR</th><th>4w</th><th>5w</th></tr>
    <tr><td>IPL</td><td>${bowl.innings}</td><td>${bowl.overs}</td><td>${bowl.wickets}</td><td>${bowl.best}</td><td>${bowl.average ?? "–"}</td>
    <td>${bowl.economy ?? "–"}</td><td>${bowl.strike_rate ?? "–"}</td><td>${bowl.four_wkts}</td><td>${bowl.five_wkts}</td></tr></table>`;
  html += `<table style="margin-top:24px"><tr><th>Fielding</th><th>Catches</th><th>Stumpings</th><th>Run outs</th></tr>
    <tr><td>IPL</td><td>${d.fielding.catches}</td><td>${d.fielding.stumpings}</td><td>${d.fielding.run_outs}</td></tr></table>`;
  $("#career").innerHTML = html;

  // Matchups: bowlers faced most (or batters bowled to most, for bowlers)
  const list = isBowler ? mu.as_bowler : mu.as_batter;
  if (!list.length) {
    $("#matchups-section").remove();
  } else {
    if (isBowler) $("#matchups-section h2").textContent = "Most-faced batters";
    $("#matchups").innerHTML = `<table>
      <tr><th>${isBowler ? "Batter" : "Bowler"}</th><th>Balls</th><th>Runs</th><th>Outs</th><th>SR</th><th>4s</th><th>6s</th></tr>
      ${list.map(r => `<tr><td><a href="/players/${r.player_id}">${esc(r.name)}</a></td><td>${r.balls}</td><td>${r.runs}</td>
        <td>${r.dismissals}</td><td>${r.strike_rate ?? "–"}</td><td>${r.fours}</td><td>${r.sixes}</td></tr>`).join("")}
    </table>`;
  }

  reveal();
}

function seasonChart(seasons, mode) {
  const accent = getComputedStyle(document.documentElement).getPropertyValue("--accent").trim();
  const key = mode === "Batting" ? "batting" : "bowling";
  const value = s => s[key] ? (key === "batting" ? s[key].runs : s[key].wickets) : 0;
  return {
    grid: { left: 8, right: 8, top: 16, bottom: 8, containLabel: true },
    tooltip: {
      trigger: "axis",
      formatter: ([pt]) => {
        const s = seasons[pt.dataIndex];
        const x = s[key];
        if (!x) return `${s.season}<br>${s.team}<br>Did not ${key === "batting" ? "bat" : "bowl"}`;
        return key === "batting"
          ? `<b>${s.season}</b> · ${teamShort(s.team)}<br>${x.runs} runs in ${x.innings} inns<br>Avg ${x.average ?? "–"} · SR ${x.strike_rate ?? "–"}`
          : `<b>${s.season}</b> · ${teamShort(s.team)}<br>${x.wickets} wickets in ${x.innings} inns<br>Econ ${x.economy ?? "–"}`;
      },
    },
    xAxis: axisStyle({ type: "category", data: seasons.map(s => s.season), splitLine: { show: false } }),
    yAxis: axisStyle({ type: "value" }),
    series: [{
      type: "bar", data: seasons.map(value), barMaxWidth: 36,
      itemStyle: { color: accent, borderRadius: [6, 6, 0, 0] },
      emphasis: { itemStyle: { opacity: .8 } },
    }],
    animationDuration: 900, animationEasing: "cubicOut",
  };
}

function phaseCard(title, value, detail, share) {
  return `
    <div class="card tile reveal">
      <p class="eyebrow">${title}</p>
      <b>${value}</b>
      <span>${detail}</span>
      <div class="bar"><i style="--w:${Math.round(share * 100)}%"></i></div>
    </div>`;
}

function perfRow(matchId, opponent, figures, when) {
  return `
    <a class="row reveal" href="/matches/${matchId}">
      ${badge(opponent)}
      <span class="grow">v ${esc(opponent)}<br><span class="muted" style="font-size:.85rem">${esc(when)}</span></span>
      <span class="num">${figures}</span>
    </a>`;
}

loadPlayer();
