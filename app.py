"""
IPL Analytics - JSON API over data/ipl.sqlite.

Only Flask + the standard library, so it fits PythonAnywhere's free tier.
The database is built offline by build/build_data.py and opened read-only.
"""
import os
import sqlite3

from flask import Flask, abort, g, jsonify, render_template, request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("IPL_DB", os.path.join(BASE_DIR, "data", "ipl.sqlite"))

app = Flask(__name__, template_folder="templates", static_folder="static")
app.json.sort_keys = False


# ----------------------------------------------------------------------------
# Database helpers
# ----------------------------------------------------------------------------
def db():
    if "db" not in g:
        g.db = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def rows(sql, *args):
    return [dict(r) for r in db().execute(sql, args).fetchall()]


def one(sql, *args):
    r = db().execute(sql, args).fetchone()
    return dict(r) if r else None


def arg_int(name, default=None, lo=None, hi=None):
    try:
        v = int(request.args.get(name, default))
    except (TypeError, ValueError):
        return default
    if lo is not None:
        v = max(lo, v)
    if hi is not None:
        v = min(hi, v)
    return v


def team_or_404(key):
    t = one("SELECT * FROM teams WHERE short = ? COLLATE NOCASE OR name = ? COLLATE NOCASE", key, key)
    if not t:
        abort(404, description=f"Unknown team '{key}'")
    return t


def player_or_404(pid):
    p = one(f"""SELECT {PLAYER_COLS}, name AS cricsheet_name, full_name, matches, last_team
                FROM players WHERE player_id = ?""", pid)
    if not p:
        abort(404, description=f"Unknown player '{pid}'")
    p["teams"] = p["teams"].split("|") if p["teams"] else []
    return p


# ----------------------------------------------------------------------------
# Cricket maths
# ----------------------------------------------------------------------------
def ratio(a, b, scale=1, nd=2):
    return round(a * scale / b, nd) if a is not None and b else None


def overs(balls):
    return f"{balls // 6}.{balls % 6}" if balls is not None else None


BAT_AGG = """
    COUNT(*) AS innings, SUM(runs) AS runs, SUM(balls) AS balls, SUM(is_out) AS outs,
    SUM(fours) AS fours, SUM(sixes) AS sixes,
    SUM(runs >= 50 AND runs < 100) AS fifties, SUM(runs >= 100) AS hundreds
"""

BOWL_AGG = """
    COUNT(*) AS innings, SUM(balls) AS balls, SUM(runs) AS runs, SUM(wickets) AS wickets,
    SUM(maidens) AS maidens, SUM(wickets >= 4) AS four_wkts, SUM(wickets >= 5) AS five_wkts
"""


def bat_rates(d):
    if not d or not d.get("innings"):
        return None
    d["average"] = ratio(d["runs"], d["outs"])
    d["strike_rate"] = ratio(d["runs"], d["balls"], 100)
    return d


def bowl_rates(d):
    if not d or not d.get("innings"):
        return None
    d["overs"] = overs(d["balls"])
    d["economy"] = ratio(d["runs"], d["balls"], 6)
    d["average"] = ratio(d["runs"], d["wickets"])
    d["strike_rate"] = ratio(d["balls"], d["wickets"], 1, 1)
    return d


def score_str(runs, wickets):
    return f"{runs}" if wickets == 10 else f"{runs}/{wickets}"


def dismissal(how, bowler, fielder):
    if not how:
        return "not out"
    return {
        "caught": f"c {fielder} b {bowler}",
        "caught and bowled": f"c & b {bowler}",
        "bowled": f"b {bowler}",
        "lbw": f"lbw b {bowler}",
        "stumped": f"st {fielder} b {bowler}",
        "hit wicket": f"hit wicket b {bowler}",
        "run out": f"run out ({fielder})" if fielder else "run out",
    }.get(how, how)


def result_text(m):
    if m["result"] == "no result":
        return "No result"
    if not m["winner"]:
        return None
    if m["result"] == "tie":
        return f"{m['winner']} won the Super Over"
    margin = (f"{m['won_by_runs']} runs" if m["won_by_runs"]
              else f"{m['won_by_wickets']} wickets" if m["won_by_wickets"] else "")
    text = f"{m['winner']} won by {margin}".strip()
    return text + (f" ({m['method']})" if m["method"] else "")


PLAYER_COLS = "player_id, display_name AS name, image_url, role, country, teams, first_season, last_season"


def player_ref(pid):
    if not pid:
        return None
    p = one(f"SELECT {PLAYER_COLS} FROM players WHERE player_id = ?", pid)
    if p:
        p["teams"] = p["teams"].split("|") if p["teams"] else []
    return p


# ----------------------------------------------------------------------------
# Meta / seasons
# ----------------------------------------------------------------------------
@app.get("/api")
def api_index():
    return jsonify(
        meta=dict((r["key"], r["value"]) for r in rows("SELECT * FROM meta")),
        endpoints=sorted(str(r) for r in app.url_map.iter_rules() if str(r).startswith("/api")),
    )


@app.get("/api/seasons")
def seasons():
    data = rows("""
        SELECT s.season, s.matches, s.champion, s.runner_up,
               s.orange_cap_id, o.display_name AS orange_cap, s.orange_cap_runs,
               s.purple_cap_id, p.display_name AS purple_cap, s.purple_cap_wickets
        FROM seasons s
        LEFT JOIN players o ON o.player_id = s.orange_cap_id
        LEFT JOIN players p ON p.player_id = s.purple_cap_id
        ORDER BY s.season DESC
    """)
    return jsonify(data)


@app.get("/api/seasons/<int:year>")
def season(year):
    s = one("SELECT * FROM seasons WHERE season = ?", year)
    if not s:
        abort(404, description=f"No data for season {year}")
    table = rows("""
        SELECT p.position, p.team, t.short, t.colour, p.played, p.won, p.lost, p.no_result,
               p.points, p.nrr
        FROM points_table p JOIN teams t ON t.name = p.team
        WHERE p.season = ? ORDER BY p.position
    """, year)
    playoffs = [dict(m, result_text=result_text(m)) for m in rows(
        "SELECT * FROM matches WHERE season = ? AND stage <> 'League' ORDER BY date", year)]
    top_bat = rows(f"""
        SELECT b.player_id, p.display_name AS name, p.image_url, {BAT_AGG}
        FROM batting_innings b JOIN players p USING (player_id)
        WHERE b.season = ? GROUP BY b.player_id ORDER BY runs DESC LIMIT 10
    """, year)
    top_bowl = rows(f"""
        SELECT b.player_id, p.display_name AS name, p.image_url, {BOWL_AGG}
        FROM bowling_innings b JOIN players p USING (player_id)
        WHERE b.season = ? GROUP BY b.player_id ORDER BY wickets DESC, runs LIMIT 10
    """, year)
    totals = one("""
        SELECT SUM(runs) AS runs, SUM(balls) AS balls, MAX(runs) AS highest
        FROM innings_totals WHERE season = ? AND super_over = 0
    """, year)
    sixes = one("SELECT SUM(sixes) AS sixes, SUM(fours) AS fours FROM batting_innings WHERE season = ?", year)
    return jsonify(
        season=year,
        champion=s["champion"], runner_up=s["runner_up"], matches=s["matches"],
        orange_cap=dict(player=player_ref(s["orange_cap_id"]), runs=s["orange_cap_runs"]),
        purple_cap=dict(player=player_ref(s["purple_cap_id"]), wickets=s["purple_cap_wickets"]),
        summary=dict(runs=totals["runs"], run_rate=ratio(totals["runs"], totals["balls"], 6),
                     highest_total=totals["highest"], **sixes),
        points_table=table,
        playoffs=playoffs,
        top_run_scorers=[bat_rates(r) for r in top_bat],
        top_wicket_takers=[bowl_rates(r) for r in top_bowl],
    )


# ----------------------------------------------------------------------------
# Teams
# ----------------------------------------------------------------------------
def team_record(name, opponent=None):
    # "? IS NULL" switches the opponent filter off when no opponent is given.
    r = one("""
        SELECT COUNT(*) AS played,
               SUM(winner = ?) AS won,
               SUM(result = 'no result') AS no_result,
               SUM(result = 'tie') AS tied
        FROM matches
        WHERE ? IN (team1, team2) AND (? IS NULL OR ? IN (team1, team2))
    """, name, name, opponent, opponent)
    r["won"] = r["won"] or 0
    r["no_result"] = r["no_result"] or 0
    r["tied"] = r["tied"] or 0
    r["lost"] = r["played"] - r["won"] - r["no_result"]
    r["win_pct"] = ratio(r["won"], r["played"] - r["no_result"], 100, 1)
    return r


@app.get("/api/teams")
def teams():
    out = []
    for t in rows("SELECT * FROM teams ORDER BY active DESC, name"):
        t["record"] = team_record(t["name"])
        t["titles"] = [r["season"] for r in rows(
            "SELECT season FROM seasons WHERE champion = ? ORDER BY season", t["name"])]
        span = one("SELECT MIN(season) AS first, MAX(season) AS last FROM appearances WHERE team = ?", t["name"])
        t.update(first_season=span["first"], last_season=span["last"])
        out.append(t)
    return jsonify(out)


@app.get("/api/teams/<key>")
def team(key):
    t = team_or_404(key)
    name = t["name"]
    by_season = rows("""
        SELECT p.season, p.position, p.played, p.won, p.lost, p.no_result, p.points, p.nrr,
               CASE WHEN s.champion = p.team THEN 'Champion'
                    WHEN s.runner_up = p.team THEN 'Runner-up'
                    WHEN EXISTS (SELECT 1 FROM matches m WHERE m.season = p.season AND m.stage <> 'League'
                                 AND p.team IN (m.team1, m.team2)) THEN 'Playoffs'
                    ELSE 'League stage' END AS finish
        FROM points_table p JOIN seasons s USING (season)
        WHERE p.team = ? ORDER BY p.season DESC
    """, name)
    top_bat = rows(f"""
        SELECT b.player_id, p.display_name AS name, p.image_url, {BAT_AGG}
        FROM batting_innings b JOIN players p USING (player_id)
        WHERE b.team = ? GROUP BY b.player_id ORDER BY runs DESC LIMIT 10
    """, name)
    top_bowl = rows(f"""
        SELECT b.player_id, p.display_name AS name, p.image_url, {BOWL_AGG}
        FROM bowling_innings b JOIN players p USING (player_id)
        WHERE b.team = ? GROUP BY b.player_id ORDER BY wickets DESC, runs LIMIT 10
    """, name)
    highest = rows("""
        SELECT match_id, season, opponent, runs, wickets, balls FROM innings_totals
        WHERE team = ? AND super_over = 0 ORDER BY runs DESC LIMIT 5
    """, name)
    # Lowest totals only count completed innings (all out or 20 overs).
    lowest = rows("""
        SELECT match_id, season, opponent, runs, wickets, balls FROM innings_totals
        WHERE team = ? AND super_over = 0 AND (wickets = 10 OR balls >= 120)
        ORDER BY runs LIMIT 5
    """, name)
    for r in highest + lowest:
        r["score"] = score_str(r["runs"], r["wickets"])
    return jsonify(
        team=t,
        record=team_record(name),
        titles=[r["season"] for r in rows("SELECT season FROM seasons WHERE champion = ? ORDER BY season", name)],
        finals=[r["season"] for r in rows(
            "SELECT season FROM seasons WHERE ? IN (champion, runner_up) ORDER BY season", name)],
        seasons=by_season,
        top_run_scorers=[bat_rates(r) for r in top_bat],
        top_wicket_takers=[bowl_rates(r) for r in top_bowl],
        highest_totals=highest,
        lowest_totals=lowest,
    )


@app.get("/api/teams/<key>/vs-all")
def team_vs_all(key):
    t = team_or_404(key)
    opponents = rows("""
        SELECT CASE WHEN team1 = ? THEN team2 ELSE team1 END AS opponent FROM matches
        WHERE ? IN (team1, team2) GROUP BY opponent ORDER BY opponent
    """, t["name"], t["name"])
    out = []
    for o in opponents:
        rec = team_record(t["name"], o["opponent"])
        meta = one("SELECT short, colour, active FROM teams WHERE name = ?", o["opponent"])
        out.append(dict(opponent=o["opponent"], **(meta or {}), **rec))
    return jsonify(team=t, opponents=out)


@app.get("/api/teams/<a>/vs/<b>")
def team_vs_team(a, b):
    ta, tb = team_or_404(a), team_or_404(b)
    if ta["name"] == tb["name"]:
        abort(400, description="Pick two different teams")
    A, B = ta["name"], tb["name"]
    matches = [dict(m, result_text=result_text(m)) for m in rows("""
        SELECT * FROM matches WHERE (team1 = ? AND team2 = ?) OR (team1 = ? AND team2 = ?)
        ORDER BY date DESC
    """, A, B, B, A)]
    def side(team, opponent):
        top_bat = rows(f"""
            SELECT x.player_id, p.display_name AS name, p.image_url, {BAT_AGG}
            FROM batting_innings x JOIN players p USING (player_id)
            WHERE x.team = ? AND x.opponent = ?
            GROUP BY x.player_id ORDER BY runs DESC LIMIT 5
        """, team, opponent)
        top_bowl = rows(f"""
            SELECT x.player_id, p.display_name AS name, p.image_url, {BOWL_AGG}
            FROM bowling_innings x JOIN players p USING (player_id)
            WHERE x.team = ? AND x.opponent = ?
            GROUP BY x.player_id ORDER BY wickets DESC, runs LIMIT 5
        """, team, opponent)
        highest = one("""
            SELECT match_id, season, runs, wickets FROM innings_totals
            WHERE team = ? AND opponent = ? AND super_over = 0 ORDER BY runs DESC LIMIT 1
        """, team, opponent)
        titles = one("SELECT COUNT(*) AS n FROM seasons WHERE champion = ?", team)["n"]
        return dict(top_run_scorers=[bat_rates(r) for r in top_bat],
                    top_wicket_takers=[bowl_rates(r) for r in top_bowl],
                    highest_total=highest, titles=titles)

    rec = team_record(A, B)
    return jsonify(
        team_a=ta, team_b=tb,
        played=rec["played"], no_result=rec["no_result"], tied=rec["tied"],
        wins={ta["short"]: rec["won"], tb["short"]: rec["lost"]},
        last_5=[m["winner"] for m in matches[:5]],
        a=side(A, B), b=side(B, A),
        matches=matches,
    )


# ----------------------------------------------------------------------------
# Players
# ----------------------------------------------------------------------------
@app.get("/api/players")
def players():
    q = (request.args.get("q") or "").strip()
    team = request.args.get("team")
    limit = arg_int("limit", 20, 1, 100)
    where, args = [], []
    if q:
        where.append("(display_name LIKE ? OR name LIKE ?)")
        args += [f"%{q}%", f"%{q}%"]
    if team:
        where.append("teams LIKE ?")
        args.append(f"%{team_or_404(team)['name']}%")
    sql = f"""SELECT {PLAYER_COLS}, matches FROM players
              {'WHERE ' + ' AND '.join(where) if where else ''}
              ORDER BY (display_name LIKE ?) DESC, matches DESC LIMIT ?"""
    out = rows(sql, *args, f"{q}%", limit)
    for p in out:
        p["teams"] = p["teams"].split("|") if p["teams"] else []
    return jsonify(out)


def player_career(pid):
    bat = bat_rates(one(f"SELECT {BAT_AGG} FROM batting_innings WHERE player_id = ?", pid))
    bowl = bowl_rates(one(f"SELECT {BOWL_AGG} FROM bowling_innings WHERE player_id = ?", pid))
    field = one("""SELECT SUM(catches + cb_catches) AS catches, SUM(stumpings) AS stumpings,
                          SUM(run_outs) AS run_outs FROM fielding_innings WHERE player_id = ?""", pid)
    if bat:
        hs = one("""SELECT runs, is_out FROM batting_innings WHERE player_id = ?
                    ORDER BY runs DESC, is_out ASC LIMIT 1""", pid)
        bat["high_score"] = f"{hs['runs']}{'' if hs['is_out'] else '*'}"
    if bowl:
        bb = one("""SELECT wickets, runs FROM bowling_innings WHERE player_id = ?
                    ORDER BY wickets DESC, runs ASC LIMIT 1""", pid)
        bowl["best"] = f"{bb['wickets']}/{bb['runs']}"
    field = {k: v or 0 for k, v in field.items()}
    return bat, bowl, field


@app.get("/api/players/<pid>")
def player(pid):
    p = player_or_404(pid)
    bat, bowl, field = player_career(pid)

    seasons = {r["season"]: dict(season=r["season"], team=r["team"], matches=r["matches"])
               for r in rows("""SELECT season, team, COUNT(*) AS matches FROM appearances
                                WHERE player_id = ? GROUP BY season, team ORDER BY season""", pid)}
    for r in rows(f"SELECT season, {BAT_AGG} FROM batting_innings WHERE player_id = ? GROUP BY season", pid):
        seasons[r.pop("season")]["batting"] = bat_rates(r)
    for r in rows(f"SELECT season, {BOWL_AGG} FROM bowling_innings WHERE player_id = ? GROUP BY season", pid):
        seasons[r.pop("season")]["bowling"] = bowl_rates(r)

    phases = dict(
        batting=[dict(r, strike_rate=ratio(r["runs"], r["balls"], 100), average=ratio(r["runs"], r["outs"]))
                 for r in rows("""SELECT phase, SUM(runs) AS runs, SUM(balls) AS balls, SUM(outs) AS outs,
                                         SUM(boundaries) AS boundaries, SUM(dots) AS dots
                                  FROM batting_phase WHERE player_id = ? GROUP BY phase""", pid)],
        bowling=[dict(r, economy=ratio(r["runs"], r["balls"], 6), overs=overs(r["balls"]))
                 for r in rows("""SELECT phase, SUM(balls) AS balls, SUM(runs) AS runs, SUM(wickets) AS wickets,
                                         SUM(dots) AS dots
                                  FROM bowling_phase WHERE player_id = ? GROUP BY phase""", pid)],
    )
    best_bat = rows("""SELECT b.match_id, b.season, b.opponent, b.runs, b.balls, b.fours, b.sixes, b.is_out, m.date
                       FROM batting_innings b JOIN matches m USING (match_id)
                       WHERE player_id = ? ORDER BY runs DESC, balls LIMIT 5""", pid)
    best_bowl = rows("""SELECT b.match_id, b.season, b.opponent, b.wickets, b.runs, b.balls, m.date
                        FROM bowling_innings b JOIN matches m USING (match_id)
                        WHERE player_id = ? AND wickets > 0 ORDER BY wickets DESC, runs LIMIT 5""", pid)
    recent = rows("""SELECT m.match_id, m.date, m.season, a.team,
                            CASE WHEN m.team1 = a.team THEN m.team2 ELSE m.team1 END AS opponent,
                            b.runs, b.balls, b.is_out, w.wickets, w.runs AS runs_conceded, w.balls AS balls_bowled
                     FROM appearances a JOIN matches m USING (match_id)
                     LEFT JOIN batting_innings b ON b.match_id = a.match_id AND b.player_id = a.player_id
                     LEFT JOIN bowling_innings w ON w.match_id = a.match_id AND w.player_id = a.player_id
                     WHERE a.player_id = ? ORDER BY m.date DESC LIMIT 10""", pid)
    pom = one("SELECT COUNT(*) AS n FROM matches WHERE player_of_match = ?", pid)["n"]

    return jsonify(
        player=p,
        player_of_match_awards=pom,
        batting=bat, bowling=bowl, fielding=field,
        seasons=list(seasons.values()),
        phases=phases,
        best_batting=best_bat, best_bowling=best_bowl,
        recent_matches=recent,
    )


@app.get("/api/players/<pid>/matchups")
def player_matchups(pid):
    player_or_404(pid)
    limit = arg_int("limit", 15, 1, 100)

    def fmt(r):
        r["strike_rate"] = ratio(r["runs"], r["balls"], 100)
        r["average"] = ratio(r["runs"], r["dismissals"])
        return r

    vs_bowlers = rows(f"""SELECT m.bowler_id AS player_id, p.display_name AS name, p.image_url,
                                 m.matches, m.balls, m.runs, m.dismissals, m.fours, m.sixes, m.dots
                          FROM matchups m JOIN players p ON p.player_id = m.bowler_id
                          WHERE m.batter_id = ? ORDER BY m.balls DESC LIMIT ?""", pid, limit)
    vs_batters = rows(f"""SELECT m.batter_id AS player_id, p.display_name AS name, p.image_url,
                                 m.matches, m.balls, m.runs, m.dismissals, m.fours, m.sixes, m.dots
                          FROM matchups m JOIN players p ON p.player_id = m.batter_id
                          WHERE m.bowler_id = ? ORDER BY m.balls DESC LIMIT ?""", pid, limit)
    return jsonify(as_batter=[fmt(r) for r in vs_bowlers], as_bowler=[fmt(r) for r in vs_batters])


@app.get("/api/players/<a>/vs/<b>")
def player_vs_player(a, b):
    pa, pb = player_or_404(a), player_or_404(b)

    def card(p):
        bat, bowl, field = player_career(p["player_id"])
        return dict(player=p, batting=bat, bowling=bowl, fielding=field)

    def duel(batter, bowler):
        r = one("SELECT * FROM matchups WHERE batter_id = ? AND bowler_id = ?", batter, bowler)
        if not r:
            return None
        r["strike_rate"] = ratio(r["runs"], r["balls"], 100)
        r["average"] = ratio(r["runs"], r["dismissals"])
        return r

    return jsonify(a=card(pa), b=card(pb),
                   a_batting_vs_b=duel(a, b), b_batting_vs_a=duel(b, a))


# ----------------------------------------------------------------------------
# Matches
# ----------------------------------------------------------------------------
@app.get("/api/matches")
def matches():
    where, args = [], []
    if request.args.get("season"):
        where.append("season = ?")
        args.append(arg_int("season"))
    for key in ("team", "opponent"):
        if request.args.get(key):
            where.append("? IN (team1, team2)")
            args.append(team_or_404(request.args[key])["name"])
    if request.args.get("venue"):
        where.append("venue = ?")
        args.append(request.args["venue"])
    limit = arg_int("limit", 50, 1, 200)
    offset = arg_int("offset", 0, 0)
    data = rows(f"""SELECT * FROM matches {'WHERE ' + ' AND '.join(where) if where else ''}
                    ORDER BY date DESC, match_id DESC LIMIT ? OFFSET ?""", *args, limit, offset)
    for m in data:
        m["result_text"] = result_text(m)
        m["scores"] = {r["team"]: score_str(r["runs"], r["wickets"]) for r in rows(
            "SELECT team, runs, wickets FROM innings_totals WHERE match_id = ? AND super_over = 0", m["match_id"])}
    return jsonify(data)


@app.get("/api/matches/<int:mid>")
def match(mid):
    m = one("SELECT * FROM matches WHERE match_id = ?", mid)
    if not m:
        abort(404, description=f"Unknown match {mid}")
    m["result_text"] = result_text(m)
    m["player_of_match"] = player_ref(m["player_of_match"])
    names = dict(db().execute("""SELECT p.player_id, p.display_name FROM appearances a
                                 JOIN players p USING (player_id) WHERE a.match_id = ?""", (mid,)).fetchall())
    innings = []
    for t in rows("SELECT * FROM innings_totals WHERE match_id = ? ORDER BY innings", mid):
        i = t["innings"]
        batting = rows("""SELECT player_id, position, runs, balls, fours, sixes, is_out, how_out,
                                 out_bowler, out_fielder FROM batting_innings
                          WHERE match_id = ? AND innings = ? ORDER BY position""", mid, i)
        for b in batting:
            b["name"] = names.get(b["player_id"])
            b["dismissal"] = dismissal(b.pop("how_out"), names.get(b.pop("out_bowler")),
                                       names.get(b.pop("out_fielder")))
            b["strike_rate"] = ratio(b["runs"], b["balls"], 100)
        bowling = rows("""SELECT player_id, balls, runs, wickets, maidens, dots, wides, noballs
                          FROM bowling_innings b WHERE match_id = ? AND innings = ?
                          ORDER BY (SELECT MIN(over_no) FROM over_summary o WHERE o.match_id = b.match_id
                                    AND o.innings = b.innings AND o.bowler_id = b.player_id)""", mid, i)
        for b in bowling:
            b["name"] = names.get(b["player_id"])
            b["overs"] = overs(b["balls"])
            b["economy"] = ratio(b["runs"], b["balls"], 6)
        by_over = rows("""SELECT over_no, runs, wickets, bowler_id FROM over_summary
                          WHERE match_id = ? AND innings = ? ORDER BY over_no""", mid, i)
        innings.append(dict(
            innings=i, team=t["team"], super_over=bool(t["super_over"]),
            score=score_str(t["runs"], t["wickets"]), runs=t["runs"], wickets=t["wickets"],
            overs=overs(t["balls"]), run_rate=ratio(t["runs"], t["balls"], 6), extras=t["extras"],
            batting=batting, bowling=bowling, overs_detail=by_over,
        ))
    return jsonify(match=m, innings=innings)


# ----------------------------------------------------------------------------
# Records
# ----------------------------------------------------------------------------
@app.get("/api/records")
def records():
    season = arg_int("season")
    team = team_or_404(request.args["team"])["name"] if request.args.get("team") else None
    limit = arg_int("limit", 10, 1, 50)
    # Both filters are optional: "? IS NULL" switches a filter off when it is not given.
    where = "(? IS NULL OR x.season = ?) AND (? IS NULL OR x.team = ?)"
    f = (season, season, team, team)
    who = "p.display_name AS name, p.image_url, x.player_id"
    min_balls_bat = 100 if season else 500
    min_balls_bowl = 120 if season else 600

    most_runs = rows(f"""
        SELECT {who}, {BAT_AGG} FROM batting_innings x JOIN players p USING (player_id)
        WHERE {where} GROUP BY x.player_id ORDER BY runs DESC LIMIT ?""", *f, limit)
    most_wickets = rows(f"""
        SELECT {who}, {BOWL_AGG} FROM bowling_innings x JOIN players p USING (player_id)
        WHERE {where} GROUP BY x.player_id ORDER BY wickets DESC, runs LIMIT ?""", *f, limit)
    most_sixes = rows(f"""
        SELECT {who}, SUM(sixes) AS sixes, COUNT(*) AS innings FROM batting_innings x JOIN players p USING (player_id)
        WHERE {where} GROUP BY x.player_id ORDER BY sixes DESC LIMIT ?""", *f, limit)
    best_strike_rate = rows(f"""
        SELECT {who}, {BAT_AGG} FROM batting_innings x JOIN players p USING (player_id)
        WHERE {where} GROUP BY x.player_id HAVING SUM(balls) >= ?
        ORDER BY SUM(runs) * 1.0 / SUM(balls) DESC LIMIT ?""", *f, min_balls_bat, limit)
    best_economy = rows(f"""
        SELECT {who}, {BOWL_AGG} FROM bowling_innings x JOIN players p USING (player_id)
        WHERE {where} GROUP BY x.player_id HAVING SUM(balls) >= ?
        ORDER BY SUM(runs) * 1.0 / SUM(balls) LIMIT ?""", *f, min_balls_bowl, limit)
    highest_scores = rows(f"""
        SELECT {who}, x.match_id, x.season, x.opponent, x.runs, x.balls, x.is_out, x.fours, x.sixes
        FROM batting_innings x JOIN players p USING (player_id)
        WHERE {where} ORDER BY x.runs DESC, x.balls LIMIT ?""", *f, limit)
    best_bowling = rows(f"""
        SELECT {who}, x.match_id, x.season, x.opponent, x.wickets, x.runs, x.balls
        FROM bowling_innings x JOIN players p USING (player_id)
        WHERE {where} ORDER BY x.wickets DESC, x.runs LIMIT ?""", *f, limit)
    highest_totals = rows(f"""
        SELECT x.match_id, x.season, x.team, x.opponent, x.runs, x.wickets, x.balls
        FROM innings_totals x WHERE {where} AND x.super_over = 0 ORDER BY x.runs DESC LIMIT ?""", *f, limit)
    for r in highest_totals:
        r["score"] = score_str(r["runs"], r["wickets"])

    return jsonify(
        season=season, team=team,
        most_runs=[bat_rates(r) for r in most_runs],
        most_wickets=[bowl_rates(r) for r in most_wickets],
        most_sixes=most_sixes,
        best_strike_rate=[bat_rates(r) for r in best_strike_rate],
        best_economy=[bowl_rates(r) for r in best_economy],
        highest_scores=highest_scores,
        best_bowling=best_bowling,
        highest_totals=highest_totals,
    )


# ----------------------------------------------------------------------------
# Errors, caching, pages
# ----------------------------------------------------------------------------
@app.errorhandler(400)
@app.errorhandler(404)
def json_error(e):
    if request.path.startswith("/api"):
        return jsonify(error=e.description), e.code
    return render_template("not_found.html", message=e.description), e.code


@app.after_request
def cache_headers(resp):
    # The data only changes when a new ipl.sqlite is uploaded.
    if request.path.startswith("/api") and resp.status_code == 200:
        resp.headers["Cache-Control"] = "public, max-age=3600"
    return resp


# ----------------------------------------------------------------------------
# Pages. Each template loads its own JS, which fetches from the API above.
# ----------------------------------------------------------------------------
LOGO_DIR = os.path.join(BASE_DIR, "static", "images", "teams")


@app.context_processor
def page_globals():
    # Every page gets the team list (for badges/colours) and the latest season.
    teams = {}
    for t in rows("SELECT name, short, colour FROM teams"):
        t["logo"] = os.path.exists(os.path.join(LOGO_DIR, t["short"] + ".webp"))
        teams[t.pop("name")] = t
    last_season = one("SELECT MAX(season) AS s FROM seasons")["s"]
    return dict(teams=teams, last_season=last_season)


@app.get("/")
def home():
    return render_template("home.html")


@app.get("/players/<pid>")
def player_page(pid):
    p = player_or_404(pid)
    return render_template("player.html", player=p)


@app.get("/teams")
def teams_page():
    return render_template("teams.html")


@app.get("/teams/<key>")
def team_page(key):
    return render_template("team.html", team=team_or_404(key))


@app.get("/teams/<a>/vs/<b>")
def team_vs_team_page(a, b):
    return render_template("team_vs.html", team_a=team_or_404(a), team_b=team_or_404(b))


@app.get("/seasons/<int:year>")
def season_page(year):
    if not one("SELECT 1 FROM seasons WHERE season = ?", year):
        abort(404, description=f"No IPL season {year}")
    has_photo = os.path.exists(os.path.join(BASE_DIR, "static", "images", "winners", f"{year}.webp"))
    return render_template("season.html", year=year, has_photo=has_photo)


@app.get("/matches/<int:mid>")
def match_page(mid):
    m = one("SELECT * FROM matches WHERE match_id = ?", mid)
    if not m:
        abort(404, description="Match not found")
    return render_template("match.html", match=m)


@app.get("/records")
def records_page():
    return render_template("records.html")


@app.get("/compare")
def compare_page():
    return render_template("compare.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
