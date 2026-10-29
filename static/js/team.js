// Team page: titles, record, finishing positions, rivalries, top players, totals, recent matches.

const teamKey = $("#hero").dataset.team;

async function loadTeam() {
  const [d, vs, recent] = await Promise.all([
    api(`/teams/${teamKey}`),
    api(`/teams/${teamKey}/vs-all`),
    api(`/matches?team=${teamKey}&limit=8`),
  ]);
  const t = d.team;

  // Header
  $("#logo").innerHTML = badge(t.name, "lg");
  const first = d.seasons.length ? d.seasons[d.seasons.length - 1].season : "";
  const last = d.seasons.length ? d.seasons[0].season : "";
  $("#span").textContent = `IPL ${first}–${last}`;
  $("#titles").innerHTML = d.titles.length
    ? d.titles.map(y => `<a class="chip" href="/seasons/${y}">🏆 ${y}</a>`).join("")
    : `<span class="muted">No titles yet</span>`;

  // Key numbers
  const playoffs = d.seasons.filter(s => s.finish !== "League stage").length;
  const tiles = [
    [d.record.played, "Matches"], [d.record.won, "Won"], [d.record.win_pct + "%", "Win rate"],
    [d.titles.length, "Titles"], [d.finals.length, "Finals"], [playoffs, "Playoff seasons"],
  ];
  $("#tiles").innerHTML = tiles.map(([v, label]) =>
    `<div class="card tile reveal"><b>${esc(v)}</b><span>${label}</span></div>`).join("");

  // Finishing position each season (1 at the top)
  const seasons = d.seasons.slice().reverse();
  const accent = getComputedStyle(document.documentElement).getPropertyValue("--accent").trim();
  const chart = echarts.init($("#finish-chart"));
  window.addEventListener("resize", () => chart.resize());
  chart.setOption({
    grid: { left: 8, right: 16, top: 16, bottom: 8, containLabel: true },
    tooltip: {
      trigger: "axis",
      formatter: ([pt]) => {
        const s = seasons[pt.dataIndex];
        return `<b>${s.season}</b> · ${s.finish}<br>League position ${s.position}<br>${s.won} won, ${s.lost} lost · ${s.points} pts`;
      },
    },
    xAxis: axisStyle({ type: "category", data: seasons.map(s => s.season), splitLine: { show: false } }),
    yAxis: axisStyle({ type: "value", inverse: true, min: 1, max: 10, interval: 1, name: "Position",
                       nameTextStyle: { color: "#6b6b73" } }),
    series: [{
      type: "line", data: seasons.map(s => s.position), smooth: 0.3, symbolSize: 12,
      lineStyle: { color: accent, width: 3 },
      itemStyle: { color: p => seasons[p.dataIndex].finish === "Champion" ? "#f5b301" : accent },
    }],
    animationDuration: 1000, animationEasing: "cubicOut",
  });

  // Record against every opponent
  $("#vs-all").innerHTML = vs.opponents.map(o => `
    <a class="row reveal" href="/teams/${teamKey}/vs/${o.short}">
      ${badge(o.opponent)}
      <span class="grow">${esc(o.opponent)}
        <div class="bar" style="max-width:320px"><i style="--w:${o.win_pct || 0}%"></i></div>
      </span>
      <span class="num">${o.won}–${o.lost}<br><span class="muted" style="font-weight:500;font-size:.8rem">${o.win_pct ?? "–"}% won</span></span>
    </a>`).join("");

  // Top players
  $("#top-bat").innerHTML = playerList(d.top_run_scorers.slice(0, 5), p => num(p.runs),
    p => `${p.innings} inns · avg ${p.average ?? "–"} · SR ${p.strike_rate}`);
  $("#top-bowl").innerHTML = playerList(d.top_wicket_takers.slice(0, 5), p => num(p.wickets),
    p => `${p.innings} inns · econ ${p.economy} · avg ${p.average ?? "–"}`);

  // Highest and lowest totals
  const totalRow = r => `
    <a class="row reveal" href="/matches/${r.match_id}">
      ${badge(r.opponent)}
      <span class="grow">v ${esc(r.opponent)}<br><span class="muted" style="font-size:.85rem">${r.season}</span></span>
      <span class="num">${esc(r.score)}</span>
    </a>`;
  $("#highest").innerHTML = d.highest_totals.map(totalRow).join("");
  $("#lowest").innerHTML = d.lowest_totals.map(totalRow).join("");

  // Recent matches
  $("#recent").innerHTML = recent.map(matchRow).join("");

  reveal();
}

loadTeam();
