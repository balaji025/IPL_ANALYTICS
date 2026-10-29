// Team vs team: wins each, last five, top performers on both sides, every meeting.

const keyA = $("#hero").dataset.a;
const keyB = $("#hero").dataset.b;

async function loadTeamVs() {
  const d = await api(`/teams/${keyA}/vs/${keyB}`);
  const A = d.team_a, B = d.team_b;
  const winsA = d.wins[A.short], winsB = d.wins[B.short];

  // Big numbers: logo, wins, "v", wins, logo
  $("#vs").innerHTML = `
    <a href="/teams/${A.short}">${badge(A.name, "lg")}<h3>${esc(A.name)}</h3></a>
    <div style="display:flex;align-items:center;gap:20px">
      <span class="big">${winsA}</span><span class="muted">v</span><span class="big">${winsB}</span>
    </div>
    <a href="/teams/${B.short}">${badge(B.name, "lg")}<h3>${esc(B.name)}</h3></a>`;

  // Win share bar in both teams' colours
  const total = winsA + winsB || 1;
  $("#share").innerHTML = `
    <i style="width:${winsA / total * 100}%;background:${A.colour}"></i>
    <i style="width:${winsB / total * 100}%;background:${B.colour}"></i>`;
  const extra = [d.tied ? `${d.tied} tied (decided by Super Over)` : "", d.no_result ? `${d.no_result} no result` : ""]
    .filter(Boolean).join(" · ");
  $("#summary").textContent = `${d.played} matches${extra ? " · " + extra : ""}`;

  // Last five: a dot in the winner's colour
  $("#form").innerHTML = d.last_5.map(w => {
    const t = window.TEAMS[w];
    return t ? `<span style="background:${t.colour}" title="${esc(w)}">${esc(t.short)}</span>`
             : `<span style="background:#a1a1aa" title="No result">NR</span>`;
  }).join("") || `<p class="muted">They have never met.</p>`;

  // Top performers on each side
  const batDetail = p => `${p.innings} inns · avg ${p.average ?? "–"} · SR ${p.strike_rate}`;
  const bowlDetail = p => `${p.innings} inns · econ ${p.economy}`;
  $("#a-bat").innerHTML = playerList(d.a.top_run_scorers, p => num(p.runs), batDetail);
  $("#b-bat").innerHTML = playerList(d.b.top_run_scorers, p => num(p.runs), batDetail);
  $("#a-bowl").innerHTML = playerList(d.a.top_wicket_takers, p => num(p.wickets), bowlDetail);
  $("#b-bowl").innerHTML = playerList(d.b.top_wicket_takers, p => num(p.wickets), bowlDetail);

  // Every meeting. The head-to-head API has no scores, so fetch them from the match list.
  const withScores = await api(`/matches?team=${keyA}&opponent=${keyB}&limit=200`);
  $("#matches").innerHTML = withScores.map(matchRow).join("");

  reveal();
}

loadTeamVs();
