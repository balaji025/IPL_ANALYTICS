// Compare page: two player pickers; the chosen ids live in the URL (?a=&b=).

const chosen = new URLSearchParams(location.search);

for (const side of ["a", "b"]) {
  $("#pick-" + side).addEventListener("pick", e => {
    chosen.set(side, e.detail.id);
    history.replaceState(null, "", "?" + chosen.toString());
    loadCompare();
  });
}

async function loadCompare() {
  const a = chosen.get("a"), b = chosen.get("b");
  // Show the name of a player already chosen through the URL
  for (const [side, id] of [["a", a], ["b", b]]) {
    if (id && !$(`#pick-${side} input`).value) {
      api(`/players/${id}`).then(d => { $(`#pick-${side} input`).value = d.player.name; });
    }
  }
  if (!a || !b) return;

  const d = await api(`/players/${a}/vs/${b}`);
  const A = d.a, B = d.b;

  // Names and photos
  const head = c => `
    <a href="/players/${c.player.player_id}" style="display:flex;flex-direction:column;align-items:center;gap:10px;text-align:center">
      ${avatar(c.player, "lg")}
      <b>${esc(c.player.name)}</b>
      <span class="muted" style="font-size:.85rem">${c.player.first_season}–${c.player.last_season}</span>
    </a>`;
  $("#heads").innerHTML = `${head(A)}<span class="label">vs</span>${head(B)}`;

  // One row per stat; the better value is highlighted. "low" means lower is better.
  const stats = [
    ["Matches", c => c.player.matches],
    ["Runs", c => c.batting?.runs],
    ["Batting average", c => c.batting?.average],
    ["Strike rate", c => c.batting?.strike_rate],
    ["Highest score", c => c.batting?.high_score, "none"],
    ["50s / 100s", c => c.batting ? `${c.batting.fifties} / ${c.batting.hundreds}` : null, "none"],
    ["Sixes", c => c.batting?.sixes],
    ["Wickets", c => c.bowling?.wickets],
    ["Economy", c => c.bowling?.economy, "low"],
    ["Bowling average", c => c.bowling?.average, "low"],
    ["Best bowling", c => c.bowling?.best, "none"],
    ["Catches", c => c.fielding.catches],
  ];
  $("#rows").innerHTML = stats.map(([label, get, rule]) => {
    const x = get(A), y = get(B);
    let winX = false, winY = false;
    if (rule !== "none" && x != null && y != null && x !== y) {
      winX = rule === "low" ? x < y : x > y;
      winY = !winX;
    }
    return `
      <div class="compare-row reveal">
        <b class="${winX ? "win" : ""}">${x ?? "–"}</b>
        <span class="label">${label}</span>
        <b class="${winY ? "win" : ""}">${y ?? "–"}</b>
      </div>`;
  }).join("");

  // Their direct battle
  const duel = (batter, bowler, r) => `
    <div class="card reveal">
      <p class="eyebrow">${esc(batter.player.name)} batting v ${esc(bowler.player.name)}</p>
      ${r ? `
        <div class="grid grid-4" style="margin-top:12px">
          <div class="tile"><b>${r.runs}</b><span>Runs</span></div>
          <div class="tile"><b>${r.balls}</b><span>Balls</span></div>
          <div class="tile"><b>${r.dismissals}</b><span>Dismissals</span></div>
          <div class="tile"><b>${r.strike_rate ?? "–"}</b><span>Strike rate</span></div>
        </div>` : `<p class="muted">Never faced each other.</p>`}
    </div>`;
  $("#duel").innerHTML = duel(A, B, d.a_batting_vs_b) + duel(B, A, d.b_batting_vs_a);

  $("#result").hidden = false;
  $("#duel-section").hidden = false;
  reveal();
}

loadCompare();
