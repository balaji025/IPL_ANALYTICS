// Shared helpers for every page. Each page has its own small script that
// fetches from the API and writes HTML into the page.

// ---------- Data ----------
async function api(path) {
  const res = await fetch("/api" + path);
  if (!res.ok) throw new Error(path + " -> " + res.status);
  return res.json();
}

// ---------- Small helpers ----------
const $ = (selector, root = document) => root.querySelector(selector);

// Escape text before putting it into HTML.
function esc(value) {
  return String(value ?? "").replace(/[&<>"']/g, c =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

function num(value) {
  return value == null ? "–" : Number(value).toLocaleString("en-IN");
}

function initials(name) {
  return esc((name || "?").split(" ").map(w => w[0]).slice(0, 2).join(""));
}

// iplt20.com photos are ~1 MB PNGs; their image service returns small WebP versions.
function photoUrl(url, width = 256) {
  if (!url) return null;
  const path = url.replace("https://www.iplt20.com", "");
  return `https://www.iplt20.com/_next/image?url=${encodeURIComponent(path)}&w=${width}&q=75`;
}

function avatar(player, size = "") {
  const src = photoUrl(player.image_url, size === "lg" ? 640 : 256);
  return src
    ? `<img class="avatar ${size}" src="${src}" alt="" loading="lazy">`
    : `<span class="avatar ${size}">${initials(player.name)}</span>`;
}

// Team logo if we have one, otherwise a coloured circle with the short code.
function badge(teamName, size = "") {
  const t = window.TEAMS[teamName] || { short: "?", colour: "#888", logo: false };
  return t.logo
    ? `<img class="badge ${size}" src="/static/images/teams/${t.short}.webp" alt="${esc(t.short)}" loading="lazy">`
    : `<span class="badge-text ${size}" style="background:${t.colour}">${esc(t.short)}</span>`;
}

function teamShort(teamName) {
  return (window.TEAMS[teamName] || {}).short || teamName;
}

// ---------- Smooth scrolling ----------
if (window.Lenis && !matchMedia("(prefers-reduced-motion: reduce)").matches) {
  const lenis = new Lenis({ duration: 1.1 });
  requestAnimationFrame(function raf(time) {
    lenis.raf(time);
    requestAnimationFrame(raf);
  });
}

// ---------- Fade sections in as they scroll into view ----------
const revealObserver = new IntersectionObserver(entries => {
  for (const entry of entries) {
    if (entry.isIntersecting) {
      entry.target.classList.add("in");
      revealObserver.unobserve(entry.target);
    }
  }
}, { threshold: 0.12 });

// Call after adding new HTML so new .reveal elements animate too.
function reveal(root = document) {
  root.querySelectorAll(".reveal:not(.in)").forEach(el => revealObserver.observe(el));
}

// Count a number up from 0 (used for the big stats).
function countUp(el, target) {
  const start = performance.now();
  const duration = 1200;
  requestAnimationFrame(function step(now) {
    const t = Math.min((now - start) / duration, 1);
    el.textContent = num(Math.round(target * (1 - Math.pow(1 - t, 3))));
    if (t < 1) requestAnimationFrame(step);
  });
}

// ---------- Mobile menu ----------
$("#menu-btn").addEventListener("click", () => $(".nav").classList.toggle("open"));

// ---------- Player search (any element with data-search) ----------
document.querySelectorAll("[data-search]").forEach(box => {
  const input = $("input", box);
  const results = $(".search-results", box);
  let timer;

  input.addEventListener("input", () => {
    clearTimeout(timer);
    const q = input.value.trim();
    if (q.length < 2) return box.classList.remove("open");
    timer = setTimeout(async () => {
      const players = await api("/players?limit=8&q=" + encodeURIComponent(q));
      results.innerHTML = players.length
        ? players.map(p => `
            <a href="/players/${p.player_id}" data-id="${p.player_id}" data-name="${esc(p.name)}">
              ${avatar(p)}
              <span>${esc(p.name)}<small>${esc(p.teams.map(teamShort).join(" · "))} · ${p.first_season}–${p.last_season}</small></span>
            </a>`).join("")
        : `<a>No players found</a>`;
      box.classList.add("open");
    }, 200);
  });

  // data-search="pick": choosing a player fires a "pick" event instead of opening their page.
  const pick = link => {
    if (box.dataset.search !== "pick") return (location.href = link.href);
    input.value = link.dataset.name;
    box.classList.remove("open");
    box.dispatchEvent(new CustomEvent("pick", { detail: { id: link.dataset.id, name: link.dataset.name } }));
  };
  results.addEventListener("click", e => {
    const link = e.target.closest("a[href]");
    if (link) { e.preventDefault(); pick(link); }
  });
  input.addEventListener("keydown", e => {
    const first = $("a[href]", results);
    if (e.key === "Enter" && first) pick(first);
  });
  document.addEventListener("click", e => { if (!box.contains(e.target)) box.classList.remove("open"); });
});

// ---------- Building blocks used by several pages ----------

// One match as a clickable row: date, teams, scores, result.
function matchRow(m) {
  const scores = m.scores || {};
  const label = m.stage === "League" ? `Match ${m.match_number || ""}` : m.stage;
  return `
    <a class="row reveal" href="/matches/${m.match_id}">
      <span class="grow">
        <span class="muted" style="font-size:.8rem">${esc(m.date)} · ${esc(label)} · ${esc(m.venue)}</span><br>
        <b>${esc(teamShort(m.team1))}</b> ${esc(scores[m.team1] || "")} &nbsp;v&nbsp;
        <b>${esc(teamShort(m.team2))}</b> ${esc(scores[m.team2] || "")}<br>
        <span style="font-size:.9rem">${esc(m.result_text || "")}</span>
      </span>
      ${badge(m.winner || m.team1)}
    </a>`;
}

// A ranked list of players with one big number on the right.
function playerList(players, value, detail) {
  if (!players.length) return `<p class="muted">No data.</p>`;
  return players.map((p, i) => `
    <a class="row reveal" href="/players/${p.player_id}">
      <span class="muted" style="width:20px">${i + 1}</span>
      ${avatar(p)}
      <span class="grow">${esc(p.name)}<br><span class="muted" style="font-size:.85rem">${detail(p)}</span></span>
      <span class="num">${value(p)}</span>
    </a>`).join("");
}

// Shared look for ECharts axes.
function axisStyle(extra = {}) {
  return Object.assign({
    axisTick: { show: false }, axisLine: { lineStyle: { color: "#d4d4d8" } },
    axisLabel: { color: "#6b6b73" }, splitLine: { lineStyle: { color: "#ececef" } },
  }, extra);
}

reveal();
