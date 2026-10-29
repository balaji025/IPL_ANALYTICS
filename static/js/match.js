// Match page: scores, result, worm / runs-per-over charts, full scorecards.

const matchId = $("#hero").dataset.match;

async function loadMatch() {
  const d = await api(`/matches/${matchId}`);
  const m = d.match;
  const main = d.innings.filter(i => !i.super_over);

  // Scores
  $("#scores").innerHTML = [m.team1, m.team2].map(team => {
    const inn = main.find(i => i.team === team);
    return `
      <a href="/teams/${teamShort(team)}" style="display:flex;align-items:center;gap:16px">
        ${badge(team, "lg")}
        <span><b style="font-size:1.2rem">${esc(team)}</b><br>
        <span class="big" style="font-size:2.4rem;font-weight:800">${inn ? esc(inn.score) : "–"}</span>
        <span class="muted">${inn ? `(${inn.overs} ov)` : "did not bat"}</span></span>
      </a>`;
  }).join("");
  $("#result").textContent = m.result_text || "";
  const pom = m.player_of_match;
  $("#extra").innerHTML = [
    pom ? `Player of the Match: <a href="/players/${pom.player_id}" style="text-decoration:underline">${esc(pom.name)}</a>` : "",
    `Toss: ${esc(m.toss_winner)} chose to ${esc(m.toss_decision)}`,
  ].filter(Boolean).join(" · ");

  // Charts
  const chart = echarts.init($("#chart"));
  window.addEventListener("resize", () => chart.resize());
  const show = type => {
    document.querySelectorAll("[data-chart]").forEach(b => b.classList.toggle("on", b.dataset.chart === type));
    $("#chart-title").textContent = type === "worm" ? "Run rate worm" : "Runs per over";
    chart.setOption(type === "worm" ? wormChart(main) : oversChart(main), true);
  };
  document.querySelectorAll("[data-chart]").forEach(b => b.addEventListener("click", () => show(b.dataset.chart)));
  show("worm");

  // Scorecards (super overs included, labelled)
  $("#scorecards").innerHTML = d.innings.map(scorecard).join("");

  reveal();
}

// One colour per innings: the batting team's colour, or grey for the second
// innings if both teams use the same colour.
function inningsColours(innings) {
  const colours = innings.map(inn => (window.TEAMS[inn.team] || {}).colour || "#888");
  if (colours.length > 1 && colours[0] === colours[1]) colours[1] = "#a1a1aa";
  return colours;
}

// Cumulative runs after each over, with a dot where wickets fell.
function wormChart(innings) {
  const colours = inningsColours(innings);
  return {
    grid: { left: 8, right: 16, top: 40, bottom: 8, containLabel: true },
    legend: { top: 0, textStyle: { color: "#6b6b73" } },
    tooltip: { trigger: "axis" },
    xAxis: axisStyle({ type: "category", data: Array.from({ length: 20 }, (_, i) => i + 1), name: "Over",
                       splitLine: { show: false } }),
    yAxis: axisStyle({ type: "value" }),
    series: innings.map((inn, i) => {
      let total = 0;
      const points = inn.overs_detail.map(o => (total += o.runs));
      return {
        name: teamShort(inn.team), type: "line", data: points, smooth: 0.2, showSymbol: false,
        lineStyle: { width: 3, color: colours[i] },
        itemStyle: { color: colours[i] },
        markPoint: {
          symbol: "circle", symbolSize: 9, label: { show: false },
          data: inn.overs_detail.flatMap((o, k) => o.wickets ? [{ coord: [k, points[k]], value: o.wickets }] : []),
        },
      };
    }),
    animationDuration: 1200, animationEasing: "cubicOut",
  };
}

// Runs scored in each over, side by side for both innings.
function oversChart(innings) {
  const colours = inningsColours(innings);
  return {
    grid: { left: 8, right: 16, top: 40, bottom: 8, containLabel: true },
    legend: { top: 0, textStyle: { color: "#6b6b73" } },
    tooltip: {
      trigger: "axis",
      formatter: pts => `Over ${pts[0].axisValue}<br>` + pts.map(p => {
        const o = innings[p.seriesIndex].overs_detail[p.dataIndex];
        return `${p.marker}${p.seriesName}: ${p.value} runs${o && o.wickets ? `, ${o.wickets} wkt` : ""}`;
      }).join("<br>"),
    },
    xAxis: axisStyle({ type: "category", data: Array.from({ length: 20 }, (_, i) => i + 1), splitLine: { show: false } }),
    yAxis: axisStyle({ type: "value" }),
    series: innings.map((inn, i) => ({
      name: teamShort(inn.team), type: "bar", barGap: "10%",
      data: inn.overs_detail.map(o => o.runs),
      itemStyle: { color: colours[i], borderRadius: [4, 4, 0, 0] },
    })),
    animationDuration: 900, animationEasing: "cubicOut",
  };
}

function scorecard(inn) {
  const title = inn.super_over ? `${esc(inn.team)} · Super Over` : esc(inn.team);
  const batting = inn.batting.map(b => `
    <tr>
      <td><a href="/players/${b.player_id}">${esc(b.name)}</a><span class="how">${esc(b.dismissal)}</span></td>
      <td><b>${b.runs}</b></td><td>${b.balls}</td><td>${b.fours}</td><td>${b.sixes}</td><td>${b.strike_rate ?? "–"}</td>
    </tr>`).join("");
  const bowling = inn.bowling.map(b => `
    <tr>
      <td><a href="/players/${b.player_id}">${esc(b.name)}</a></td>
      <td>${b.overs}</td><td>${b.maidens}</td><td>${b.runs}</td><td><b>${b.wickets}</b></td><td>${b.economy ?? "–"}</td>
    </tr>`).join("");
  return `
    <div class="card reveal" style="margin-bottom:24px">
      <div class="section-head" style="margin-bottom:16px">
        <div style="display:flex;align-items:center;gap:14px">${badge(inn.team)}<h3 style="font-size:1.3rem">${title}</h3></div>
        <h3 style="font-size:1.3rem">${esc(inn.score)} <span class="muted" style="font-weight:500">(${inn.overs} ov)</span></h3>
      </div>
      ${inn.batting.length ? `<div class="table-wrap"><table class="scorecard">
        <tr><th>Batter</th><th>R</th><th>B</th><th>4s</th><th>6s</th><th>SR</th></tr>
        ${batting}
        <tr class="total"><td>Extras</td><td>${inn.extras}</td><td colspan="4"></td></tr>
      </table></div>` : ""}
      ${inn.bowling.length ? `<div class="table-wrap" style="margin-top:20px"><table class="scorecard">
        <tr><th>Bowler</th><th>O</th><th>M</th><th>R</th><th>W</th><th>Econ</th></tr>
        ${bowling}
      </table></div>` : ""}
    </div>`;
}

loadMatch();
