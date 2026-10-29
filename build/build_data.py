"""
Build data/<league>.sqlite from Cricsheet JSON match files.

Runs on your own machine (not on PythonAnywhere). The output SQLite file holds
only pre-aggregated tables, so the web app needs nothing but Flask + sqlite3.

    python build/build_data.py                      # IPL, default paths
    python build/build_data.py --src ipl_json --out data/ipl.sqlite

Full player names and headshots come from build/player_names.csv.
"""
import argparse
import glob
import json
import os
import sqlite3
import sys
import time

import duckdb
import pandas as pd

# ----------------------------------------------------------------------------
# League-specific normalisation (IPL). Add a block like this per league later.
# ----------------------------------------------------------------------------
TEAM_ALIASES = {
    "Delhi Daredevils": "Delhi Capitals",
    "Kings XI Punjab": "Punjab Kings",
    "Royal Challengers Bangalore": "Royal Challengers Bengaluru",
    "Rising Pune Supergiants": "Rising Pune Supergiant",
}

TEAMS = {
    # name: (short code, primary colour, active)
    "Chennai Super Kings": ("CSK", "#F9CD05", 1),
    "Delhi Capitals": ("DC", "#17479E", 1),
    "Gujarat Titans": ("GT", "#1B2133", 1),
    "Kolkata Knight Riders": ("KKR", "#3A225D", 1),
    "Lucknow Super Giants": ("LSG", "#0057E2", 1),
    "Mumbai Indians": ("MI", "#004BA0", 1),
    "Punjab Kings": ("PBKS", "#DD1F2D", 1),
    "Rajasthan Royals": ("RR", "#EA1A85", 1),
    "Royal Challengers Bengaluru": ("RCB", "#EC1C24", 1),
    "Sunrisers Hyderabad": ("SRH", "#FF822A", 1),
    "Deccan Chargers": ("DCH", "#D9E3EF", 0),
    "Gujarat Lions": ("GL", "#E04F16", 0),
    "Kochi Tuskers Kerala": ("KTK", "#6B2C91", 0),
    "Pune Warriors": ("PWI", "#2F9BE3", 0),
    "Rising Pune Supergiant": ("RPS", "#6F61AC", 0),
}

VENUE_ALIASES = {
    "Feroz Shah Kotla": "Arun Jaitley Stadium",
    "M.Chinnaswamy Stadium": "M Chinnaswamy Stadium",
    "Sardar Patel Stadium": "Narendra Modi Stadium",
    "Sheikh Zayed Stadium": "Zayed Cricket Stadium",
    "Punjab Cricket Association Stadium": "Punjab Cricket Association IS Bindra Stadium",
    "Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium": "Dr YS Rajasekhara Reddy ACA-VDCA Cricket Stadium",
}

CITY_ALIASES = {"Bangalore": "Bengaluru", "Chandigarh": "Mohali", "Navi Mumbai": "Mumbai"}

# Dismissals credited to the bowler.
BOWLER_WICKETS = ("bowled", "caught", "caught and bowled", "lbw", "stumped", "hit wicket")
# Dismissals that do not count as an innings-ending "out" for batting average.
NOT_OUT_KINDS = ("retired hurt",)


def team(name):
    return TEAM_ALIASES.get(name, name)


def venue(name):
    base = name.split(",")[0].strip()
    return VENUE_ALIASES.get(base, base)


def phase(over0):
    return "powerplay" if over0 < 6 else ("middle" if over0 < 15 else "death")


# ----------------------------------------------------------------------------
# 1. Parse JSON into flat frames
# ----------------------------------------------------------------------------
def parse(src):
    files = sorted(glob.glob(os.path.join(src, "*.json")))
    if not files:
        sys.exit(f"No JSON files found in {src}")

    matches, balls, appearances, people = [], [], [], {}

    for path in files:
        with open(path, encoding="utf-8") as fh:
            m = json.load(fh)
        info = m["info"]
        mid = int(os.path.splitext(os.path.basename(path))[0])
        reg = info["registry"]["people"]
        for name, pid in reg.items():
            people.setdefault(pid, set()).add(name)

        date = info["dates"][0]
        season = int(date[:4])
        ev = info.get("event", {})
        out = info.get("outcome", {})
        by = out.get("by", {})
        raw_venue = info.get("venue", "")
        city = info.get("city") or (raw_venue.split(",")[-1].strip() if "," in raw_venue else None)
        t1, t2 = (team(t) for t in info["teams"])
        winner = out.get("winner") or out.get("eliminator")
        target = next((i.get("target") for i in m["innings"] if i.get("target") and not i.get("super_over")), {}) or {}

        matches.append(dict(
            match_id=mid, season=season, date=date,
            stage=ev.get("stage") or "League",
            match_number=ev.get("match_number"),
            venue=venue(raw_venue), city=CITY_ALIASES.get(city, city),
            team1=t1, team2=t2,
            toss_winner=team(info["toss"]["winner"]), toss_decision=info["toss"]["decision"],
            winner=team(winner) if winner else None,
            result=out.get("result"),            # 'tie' / 'no result' / None
            won_by_runs=by.get("runs"), won_by_wickets=by.get("wickets"),
            method=out.get("method"),            # 'D/L' etc.
            target_runs=target.get("runs"), target_overs=target.get("overs"),
            player_of_match=reg.get((info.get("player_of_match") or [None])[0]),
        ))

        for tname, plist in info["players"].items():
            for p in plist:
                appearances.append((mid, season, team(tname), reg[p]))

        for inn_no, inn in enumerate(m["innings"], start=1):
            bat = team(inn["team"])
            bowl = t2 if bat == t1 else t1
            so = 1 if inn.get("super_over") else 0
            seq = 0
            for ov in inn["overs"]:
                o = ov["over"]
                for d in ov["deliveries"]:
                    seq += 1
                    ex = d.get("extras", {})
                    r = d["runs"]
                    w = (d.get("wickets") or [None])[0]
                    w2 = d["wickets"][1] if len(d.get("wickets", [])) > 1 else None
                    fielders = [f.get("name") for f in (w or {}).get("fielders", []) if f.get("name")]
                    balls.append((
                        mid, season, inn_no, so, bat, bowl, o, seq,
                        reg[d["batter"]], reg[d["bowler"]], reg[d["non_striker"]],
                        r["batter"], r["extras"], r["total"],
                        ex.get("wides", 0), ex.get("noballs", 0), ex.get("byes", 0),
                        ex.get("legbyes", 0), ex.get("penalty", 0),
                        1 if r.get("non_boundary") else 0,
                        reg[w["player_out"]] if w else None, w["kind"] if w else None,
                        reg.get(fielders[0]) if fielders else None,
                        reg.get(fielders[1]) if len(fielders) > 1 else None,
                        reg[w2["player_out"]] if w2 else None, w2["kind"] if w2 else None,
                    ))

    balls = pd.DataFrame(balls, columns=[
        "match_id", "season", "innings", "super_over", "batting_team", "bowling_team",
        "over0", "seq", "batter", "bowler", "non_striker",
        "batter_runs", "extras", "total_runs", "wides", "noballs", "byes", "legbyes", "penalty",
        "non_boundary", "player_out", "wicket_kind", "fielder1", "fielder2",
        "player_out2", "wicket_kind2",
    ])
    balls["phase"] = balls["over0"].map(phase)
    return (pd.DataFrame(matches), balls,
            pd.DataFrame(appearances, columns=["match_id", "season", "team", "player_id"]),
            people)


# ----------------------------------------------------------------------------
# 2. Full names / headshots (build/player_names.csv, editable by hand)
# ----------------------------------------------------------------------------
def player_names(path):
    """Cricsheet only has short names ("V Kohli"). This CSV maps registry ids to
    full names, iplt20.com headshots, roles and countries. It is filled by
    fetch_squads.py; set source=manual on a row to fix a player by hand."""
    cols = ["player_id", "full_name", "image_url", "role", "country"]
    if not os.path.exists(path):
        print(f"  {path} not found, using Cricsheet names")
        return pd.DataFrame(columns=cols)
    df = pd.read_csv(path, dtype=str).drop_duplicates("player_id", keep="last")
    # iplt20 hands out a (broken) placeholder when it has no photo.
    df.loc[df["image_url"].fillna("").str.contains("default-headshot"), "image_url"] = None
    return df.reindex(columns=cols)


# ----------------------------------------------------------------------------
# 3. Aggregate with DuckDB
# ----------------------------------------------------------------------------
SQL = {
# --- per innings scorecard rows ------------------------------------------------
"batting_innings": f"""
WITH faced AS (
    SELECT match_id, innings, batting_team AS team, bowling_team AS opponent, batter AS player_id,
           MIN(seq) AS first_seq,
           SUM(batter_runs) AS runs,
           SUM(CASE WHEN wides = 0 THEN 1 ELSE 0 END) AS balls,
           SUM(CASE WHEN batter_runs = 4 AND non_boundary = 0 THEN 1 ELSE 0 END) AS fours,
           SUM(CASE WHEN batter_runs = 6 AND non_boundary = 0 THEN 1 ELSE 0 END) AS sixes,
           SUM(CASE WHEN batter_runs = 0 AND wides = 0 THEN 1 ELSE 0 END) AS dots
    FROM balls WHERE super_over = 0 GROUP BY ALL
),
at_crease AS (   -- non-strikers who never faced still batted
    -- +0.5 so the striker ranks ahead of the non-striker when both arrive on the same ball
    SELECT match_id, innings, batting_team AS team, bowling_team AS opponent, non_striker AS player_id,
           MIN(seq) + 0.5 AS first_seq, 0 AS runs, 0 AS balls, 0 AS fours, 0 AS sixes, 0 AS dots
    FROM balls WHERE super_over = 0 GROUP BY ALL
),
outs AS (
    SELECT match_id, innings, player_out AS player_id, wicket_kind AS how_out, bowler AS out_bowler, fielder1 AS out_fielder
    FROM balls WHERE super_over = 0 AND player_out IS NOT NULL
    UNION ALL
    SELECT match_id, innings, player_out2, wicket_kind2, bowler, NULL
    FROM balls WHERE super_over = 0 AND player_out2 IS NOT NULL
),
merged AS (
    SELECT match_id, innings, team, opponent, player_id, MIN(first_seq) AS first_seq,
           SUM(runs) AS runs, SUM(balls) AS balls, SUM(fours) AS fours, SUM(sixes) AS sixes, SUM(dots) AS dots
    FROM (SELECT * FROM faced UNION ALL SELECT * FROM at_crease) GROUP BY ALL
)
SELECT m.match_id, x.season, m.innings, m.team, m.opponent, m.player_id,
       ROW_NUMBER() OVER (PARTITION BY m.match_id, m.innings ORDER BY m.first_seq, m.player_id) AS position,
       m.runs, m.balls, m.fours, m.sixes, m.dots,
       CASE WHEN o.how_out IS NOT NULL AND o.how_out NOT IN {NOT_OUT_KINDS} THEN 1 ELSE 0 END AS is_out,
       o.how_out, o.out_bowler, o.out_fielder
FROM merged m
JOIN matches x USING (match_id)
LEFT JOIN (SELECT DISTINCT ON (match_id, innings, player_id) * FROM outs) o
       ON o.match_id = m.match_id AND o.innings = m.innings AND o.player_id = m.player_id
""",

"bowling_innings": f"""
WITH per_over AS (
    SELECT match_id, innings, bowler, over0,
           SUM(CASE WHEN wides = 0 AND noballs = 0 THEN 1 ELSE 0 END) AS legal,
           SUM(batter_runs + wides + noballs) AS conceded
    FROM balls WHERE super_over = 0 GROUP BY ALL
)
SELECT b.match_id, x.season, b.innings, b.bowling_team AS team, b.batting_team AS opponent, b.bowler AS player_id,
       SUM(CASE WHEN wides = 0 AND noballs = 0 THEN 1 ELSE 0 END) AS balls,
       SUM(batter_runs + wides + noballs) AS runs,
       SUM(CASE WHEN wicket_kind IN {BOWLER_WICKETS} THEN 1 ELSE 0 END) AS wickets,
       SUM(CASE WHEN total_runs = 0 THEN 1 ELSE 0 END) AS dots,
       SUM(CASE WHEN batter_runs = 4 AND non_boundary = 0 THEN 1 ELSE 0 END) AS fours,
       SUM(CASE WHEN batter_runs = 6 AND non_boundary = 0 THEN 1 ELSE 0 END) AS sixes,
       SUM(CASE WHEN wides > 0 THEN wides ELSE 0 END) AS wides,
       SUM(CASE WHEN noballs > 0 THEN 1 ELSE 0 END) AS noballs,
       (SELECT COUNT(*) FROM per_over p WHERE p.match_id = b.match_id AND p.innings = b.innings
            AND p.bowler = b.bowler AND p.legal >= 6 AND p.conceded = 0) AS maidens
FROM balls b JOIN matches x USING (match_id)
WHERE super_over = 0
GROUP BY b.match_id, x.season, b.innings, b.bowling_team, b.batting_team, b.bowler
""",

"fielding_innings": """
SELECT match_id, season, player_id,
       SUM(CASE WHEN kind = 'caught' THEN 1 ELSE 0 END) AS catches,
       SUM(CASE WHEN kind = 'caught and bowled' THEN 1 ELSE 0 END) AS cb_catches,
       SUM(CASE WHEN kind = 'stumped' THEN 1 ELSE 0 END) AS stumpings,
       SUM(CASE WHEN kind = 'run out' THEN 1 ELSE 0 END) AS run_outs
FROM (
    SELECT match_id, season, wicket_kind AS kind, fielder1 AS player_id FROM balls
        WHERE super_over = 0 AND wicket_kind IN ('caught', 'stumped', 'run out') AND fielder1 IS NOT NULL
    UNION ALL
    SELECT match_id, season, wicket_kind, fielder2 FROM balls
        WHERE super_over = 0 AND wicket_kind = 'run out' AND fielder2 IS NOT NULL
    UNION ALL
    SELECT match_id, season, wicket_kind, bowler FROM balls
        WHERE super_over = 0 AND wicket_kind = 'caught and bowled'
)
GROUP BY ALL
""",

# --- phase splits per player per season ----------------------------------------
"batting_phase": """
SELECT batter AS player_id, season, phase,
       SUM(batter_runs) AS runs,
       SUM(CASE WHEN wides = 0 THEN 1 ELSE 0 END) AS balls,
       SUM(CASE WHEN player_out = batter AND wicket_kind <> 'retired hurt' THEN 1 ELSE 0 END) AS outs,
       SUM(CASE WHEN batter_runs IN (4, 6) AND non_boundary = 0 THEN 1 ELSE 0 END) AS boundaries,
       SUM(CASE WHEN batter_runs = 0 AND wides = 0 THEN 1 ELSE 0 END) AS dots
FROM balls WHERE super_over = 0 GROUP BY ALL
""",

"bowling_phase": f"""
SELECT bowler AS player_id, season, phase,
       SUM(CASE WHEN wides = 0 AND noballs = 0 THEN 1 ELSE 0 END) AS balls,
       SUM(batter_runs + wides + noballs) AS runs,
       SUM(CASE WHEN wicket_kind IN {BOWLER_WICKETS} THEN 1 ELSE 0 END) AS wickets,
       SUM(CASE WHEN total_runs = 0 THEN 1 ELSE 0 END) AS dots
FROM balls WHERE super_over = 0 GROUP BY ALL
""",

# --- batter vs bowler -----------------------------------------------------------
"matchups": f"""
SELECT batter AS batter_id, bowler AS bowler_id,
       COUNT(DISTINCT match_id) AS matches,
       SUM(CASE WHEN wides = 0 THEN 1 ELSE 0 END) AS balls,
       SUM(batter_runs) AS runs,
       SUM(CASE WHEN player_out = batter AND wicket_kind IN {BOWLER_WICKETS} THEN 1 ELSE 0 END) AS dismissals,
       SUM(CASE WHEN batter_runs = 4 AND non_boundary = 0 THEN 1 ELSE 0 END) AS fours,
       SUM(CASE WHEN batter_runs = 6 AND non_boundary = 0 THEN 1 ELSE 0 END) AS sixes,
       SUM(CASE WHEN batter_runs = 0 AND wides = 0 THEN 1 ELSE 0 END) AS dots
FROM balls WHERE super_over = 0 GROUP BY ALL
""",

# --- team / match level ---------------------------------------------------------
"innings_totals": """
SELECT match_id, season, innings, super_over, batting_team AS team, bowling_team AS opponent,
       SUM(total_runs) AS runs,
       COUNT(player_out) + COUNT(player_out2)
         - SUM(CASE WHEN wicket_kind = 'retired hurt' THEN 1 ELSE 0 END) AS wickets,
       SUM(CASE WHEN wides = 0 AND noballs = 0 THEN 1 ELSE 0 END) AS balls,
       SUM(CASE WHEN phase = 'powerplay' THEN total_runs ELSE 0 END) AS pp_runs,
       SUM(CASE WHEN phase = 'death' THEN total_runs ELSE 0 END) AS death_runs,
       SUM(extras) AS extras
FROM balls GROUP BY ALL
""",

"over_summary": """
SELECT match_id, innings, over0 + 1 AS over_no, bowler AS bowler_id,
       SUM(total_runs) AS runs,
       COUNT(player_out) + COUNT(player_out2) AS wickets
FROM balls WHERE super_over = 0 GROUP BY ALL
""",
}


def points_table(matches, innings):
    """League-stage standings with net run rate, per season.

    NRR follows the IPL rules: a side bowled out is charged its full quota of
    overs; in a D/L-revised chase the side batting first is credited with
    (target - 1) off the revised overs. No-results do not count towards NRR.
    Games washed out before a ball (missing from Cricsheet) are inferred: a
    team with fewer recorded league games than the most any team played lost
    the difference to washouts, each worth one point.
    """
    lg = matches[matches["stage"] == "League"]
    inn = innings[innings["super_over"] == 0].set_index(["match_id", "innings"])
    rows = []
    for m in lg.itertuples():
        for t in (m.team1, m.team2):
            won = m.winner == t
            nr = m.result == "no result"
            rows.append(dict(season=m.season, team=t, played=1, won=int(won),
                             lost=int(not won and not nr), no_result=int(nr),
                             rf=0.0, bf=0, ra=0.0, bb=0))
        if m.result == "no result":
            continue
        try:
            i1, i2 = inn.loc[(m.match_id, 1)], inn.loc[(m.match_id, 2)]
        except KeyError:
            continue
        quota = int(m.target_overs * 6) if pd.notna(m.target_overs) else 120
        b1 = quota if i1.wickets >= 10 else i1.balls
        r1 = i1.runs
        if pd.notna(m.method) and pd.notna(m.target_runs):
            r1, b1 = m.target_runs - 1, quota
        b2 = quota if i2.wickets >= 10 else i2.balls
        for side, rf, bf, ra, bb in ((i1.team, r1, b1, i2.runs, b2), (i2.team, i2.runs, b2, r1, b1)):
            rows.append(dict(season=m.season, team=side, played=0, won=0, lost=0, no_result=0,
                             rf=float(rf), bf=int(bf), ra=float(ra), bb=int(bb)))
    df = pd.DataFrame(rows).groupby(["season", "team"], as_index=False).sum()
    most = df.groupby("season")["played"].transform("max")
    df["washed_out"] = most - df["played"]
    df["played"] = most
    df["no_result"] += df["washed_out"]
    df["points"] = 2 * df["won"] + df["no_result"]
    df["nrr"] = (df["rf"] * 6 / df["bf"] - df["ra"] * 6 / df["bb"]).round(3)
    df = df.sort_values(["season", "points", "nrr"], ascending=[True, False, False])
    df["position"] = df.groupby("season").cumcount() + 1
    return df[["season", "position", "team", "played", "won", "lost", "no_result", "points", "nrr",
               "rf", "bf", "ra", "bb"]].rename(columns={
        "rf": "runs_for", "bf": "balls_faced", "ra": "runs_against", "bb": "balls_bowled"})


def season_awards(con):
    """Champion, runner-up, orange and purple cap per season."""
    return con.execute("""
    WITH finals AS (
        SELECT season, winner AS champion,
               CASE WHEN winner = team1 THEN team2 ELSE team1 END AS runner_up
        FROM matches WHERE stage = 'Final'
    ),
    orange AS (
        SELECT season, player_id, SUM(runs) AS runs,
               ROW_NUMBER() OVER (PARTITION BY season ORDER BY SUM(runs) DESC, SUM(balls)) AS rk
        FROM batting_innings GROUP BY season, player_id
    ),
    purple AS (
        SELECT season, player_id, SUM(wickets) AS wickets,
               ROW_NUMBER() OVER (PARTITION BY season ORDER BY SUM(wickets) DESC, SUM(runs)) AS rk
        FROM bowling_innings GROUP BY season, player_id
    ),
    counts AS (SELECT season, COUNT(*) AS matches FROM matches GROUP BY season)
    SELECT c.season, c.matches, f.champion, f.runner_up,
           o.player_id AS orange_cap_id, o.runs AS orange_cap_runs,
           p.player_id AS purple_cap_id, p.wickets AS purple_cap_wickets
    FROM counts c
    LEFT JOIN finals f USING (season)
    LEFT JOIN orange o ON o.season = c.season AND o.rk = 1
    LEFT JOIN purple p ON p.season = c.season AND p.rk = 1
    ORDER BY c.season
    """).df()


def players_table(con, people, names):
    df = con.execute("""
        SELECT player_id, COUNT(DISTINCT match_id) AS matches,
               MIN(season) AS first_season, MAX(season) AS last_season,
               arg_max(team, season) AS last_team
        FROM appearances GROUP BY player_id
    """).df()
    # Cricsheet name for this registry id (ids almost always have one name).
    df["name"] = df["player_id"].map(lambda p: sorted(people.get(p, {p}))[0])
    df = df.merge(names, on="player_id", how="left")
    df["display_name"] = df["full_name"].fillna(df["name"])
    teams = con.execute("""
        SELECT player_id, string_agg(team, '|' ORDER BY first) AS teams FROM (
            SELECT player_id, team, MIN(season) AS first FROM appearances GROUP BY ALL
        ) GROUP BY player_id
    """).df()
    return df.merge(teams, on="player_id", how="left")[[
        "player_id", "name", "display_name", "full_name", "image_url", "role", "country",
        "matches", "first_season", "last_season", "last_team", "teams",
    ]]


# ----------------------------------------------------------------------------
# 4. Write SQLite
# ----------------------------------------------------------------------------
INDEXES = [
    "CREATE INDEX ix_bat_player ON batting_innings(player_id, season)",
    "CREATE INDEX ix_bat_match ON batting_innings(match_id)",
    "CREATE INDEX ix_bowl_player ON bowling_innings(player_id, season)",
    "CREATE INDEX ix_bowl_match ON bowling_innings(match_id)",
    "CREATE INDEX ix_field_player ON fielding_innings(player_id)",
    "CREATE INDEX ix_batph_player ON batting_phase(player_id)",
    "CREATE INDEX ix_bowlph_player ON bowling_phase(player_id)",
    "CREATE INDEX ix_mu_batter ON matchups(batter_id, bowler_id)",
    "CREATE INDEX ix_mu_bowler ON matchups(bowler_id)",
    "CREATE INDEX ix_app_player ON appearances(player_id)",
    "CREATE INDEX ix_app_match ON appearances(match_id)",
    "CREATE INDEX ix_inn_match ON innings_totals(match_id)",
    "CREATE INDEX ix_inn_team ON innings_totals(team, season)",
    "CREATE INDEX ix_over_match ON over_summary(match_id, innings)",
    "CREATE INDEX ix_match_season ON matches(season)",
    "CREATE INDEX ix_match_teams ON matches(team1, team2)",
    "CREATE INDEX ix_players_name ON players(display_name)",
    "CREATE INDEX ix_points_season ON points_table(season)",
]


def write_sqlite(path, tables):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = path + ".tmp"
    if os.path.exists(tmp):
        os.remove(tmp)
    db = sqlite3.connect(tmp)
    for name, df in tables.items():
        for col in df.columns:   # whole-number floats (from NaN-able columns) -> INTEGER
            if df[col].dtype.kind == "f" and (df[col].dropna() % 1 == 0).all():
                df[col] = df[col].astype("Int64")
        df = df.astype(object).where(pd.notna(df), None)
        df.to_sql(name, db, index=False)
    for stmt in INDEXES:
        db.execute(stmt)
    db.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT)")
    db.executemany("INSERT INTO meta VALUES (?, ?)", [
        ("built_at", time.strftime("%Y-%m-%d %H:%M:%S")),
        ("source", "cricsheet.org"),
        ("first_season", str(tables["matches"]["season"].min())),
        ("last_season", str(tables["matches"]["season"].max())),
        ("matches", str(len(tables["matches"]))),
        ("players", str(len(tables["players"]))),
        ("runs", str(int(tables["innings_totals"]["runs"].sum()))),
        ("balls", str(int(tables["innings_totals"]["balls"].sum()))),
        ("sixes", str(int(tables["batting_innings"]["sixes"].sum()))),
    ])
    db.commit()
    db.execute("VACUUM")
    db.close()
    os.replace(tmp, path)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(here)
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=os.path.join(root, "ipl_json"))
    ap.add_argument("--out", default=os.path.join(root, "data", "ipl.sqlite"))
    ap.add_argument("--names", default=os.path.join(here, "player_names.csv"))
    args = ap.parse_args()

    t0 = time.time()
    print("Parsing JSON ...")
    matches, balls, appearances, people = parse(args.src)
    print(f"  {len(matches)} matches, {len(balls)} deliveries")

    names = player_names(args.names)
    print(f"  {len(names)} players with full names / headshots")

    con = duckdb.connect()
    for name, df in (("matches", matches), ("balls", balls), ("appearances", appearances)):
        con.register(name, df)

    print("Aggregating ...")
    tables = {"matches": matches}
    for name, sql in SQL.items():
        tables[name] = con.execute(sql).df()
        con.register(name, tables[name])
    tables["seasons"] = season_awards(con)
    tables["points_table"] = points_table(matches, tables["innings_totals"])
    tables["appearances"] = appearances
    tables["players"] = players_table(con, people, names)
    tables["teams"] = pd.DataFrame(
        [(n, c, col, a) for n, (c, col, a) in TEAMS.items()],
        columns=["name", "short", "colour", "active"],
    )
    unknown = (set(matches.team1) | set(matches.team2)) - set(TEAMS)
    if unknown:
        print(f"  WARNING: teams missing from TEAMS config: {sorted(unknown)}")

    print(f"Writing {args.out} ...")
    write_sqlite(args.out, tables)
    size = os.path.getsize(args.out) / 1e6
    print(f"Done in {time.time() - t0:.1f}s -> {size:.1f} MB")
    for k, v in tables.items():
        print(f"  {k:18s} {len(v):>7,} rows")


if __name__ == "__main__":
    main()
