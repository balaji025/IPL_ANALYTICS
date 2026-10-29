"""
Sanity-check data/ipl.sqlite after a build.

    python build/validate_data.py            # all checks
    python build/validate_data.py --no-net   # skip the photo URL check

1. Recomputes every innings total straight from the Cricsheet JSON and
   compares it with the database (independent of build_data.py's SQL).
2. Checks the tables agree with each other (batting + extras = total,
   bowling + byes/leg-byes = total, dismissals add up, squad sizes...).
3. Prints well-known IPL records so a human can eyeball them.
4. Spot-checks that player photo URLs still load.

Exits with status 1 if any hard check fails.
"""
import argparse
import glob
import json
import os
import random
import sqlite3
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

failures = []


def check(name, bad_rows, show=5):
    if bad_rows:
        failures.append(name)
        print(f"  FAIL  {name}: {len(bad_rows)} problem(s)")
        for r in bad_rows[:show]:
            print(f"          {r}")
    else:
        print(f"  ok    {name}")


def from_json(src):
    """innings -> (runs, wickets, legal balls, byes+legbyes+penalty) from raw JSON."""
    out, unknown_fielders = {}, []
    for path in glob.glob(os.path.join(src, "*.json")):
        with open(path, encoding="utf-8") as fh:
            m = json.load(fh)
        mid = int(os.path.basename(path)[:-5])
        reg = m["info"]["registry"]["people"]
        for i, inn in enumerate(m["innings"], start=1):
            runs = wk = legal = other = 0
            for ov in inn["overs"]:
                for d in ov["deliveries"]:
                    ex = d.get("extras", {})
                    runs += d["runs"]["total"]
                    other += ex.get("byes", 0) + ex.get("legbyes", 0) + ex.get("penalty", 0)
                    if "wides" not in ex and "noballs" not in ex:
                        legal += 1
                    for w in d.get("wickets", []):
                        if w["kind"] != "retired hurt":
                            wk += 1
                        for f in w.get("fielders", []):
                            if f.get("name") and f["name"] not in reg:
                                unknown_fielders.append((mid, f["name"]))
            out[(mid, i)] = (runs, wk, legal, other, 1 if inn.get("miscounted_overs") else 0)
    return out, unknown_fielders


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=os.path.join(ROOT, "data", "ipl.sqlite"))
    ap.add_argument("--src", default=os.path.join(ROOT, "ipl_json"))
    ap.add_argument("--no-net", action="store_true")
    args = ap.parse_args()

    db = sqlite3.connect(args.db)
    q = lambda sql, *a: db.execute(sql, a).fetchall()

    print("1. Database vs raw Cricsheet JSON")
    raw, unknown_fielders = from_json(args.src)
    dbt = {(m, i): (r, w, b) for m, i, r, w, b in q(
        "SELECT match_id, innings, runs, wickets, balls FROM innings_totals")}
    check("every JSON innings is in the database", [k for k in raw if k not in dbt])
    check("innings runs / wickets / balls match JSON",
          [(k, raw[k][:3], dbt[k]) for k in raw if k in dbt and raw[k][:3] != dbt[k]])
    check("fielders all have registry ids", unknown_fielders)
    n_json = len(glob.glob(os.path.join(args.src, "*.json")))
    check("match count matches JSON files", [] if q("SELECT COUNT(*) FROM matches")[0][0] == n_json else ["mismatch"])

    print("\n2. Internal consistency (super overs excluded)")
    bat = dict(((m, i), r) for m, i, r in q(
        "SELECT match_id, innings, SUM(runs) FROM batting_innings GROUP BY 1, 2"))
    ext = dict(((m, i), (r, e)) for m, i, r, e in q(
        "SELECT match_id, innings, runs, extras FROM innings_totals WHERE super_over = 0"))
    check("batting runs + extras = innings total",
          [(k, bat.get(k, 0), e, r) for k, (r, e) in ext.items() if bat.get(k, 0) + e != r])

    bowl = dict(((m, i), r) for m, i, r in q(
        "SELECT match_id, innings, SUM(runs) FROM bowling_innings GROUP BY 1, 2"))
    check("bowler runs + byes/leg-byes/penalties = innings total",
          [(k, bowl.get(k), raw[k][3], r) for k, (r, _) in ext.items() if bowl.get(k, 0) + raw[k][3] != r])

    outs = dict(((m, i), n) for m, i, n in q(
        "SELECT match_id, innings, SUM(is_out) FROM batting_innings GROUP BY 1, 2"))
    wk = dict(((m, i), w) for m, i, w in q(
        "SELECT match_id, innings, wickets FROM innings_totals WHERE super_over = 0"))
    check("batters out = innings wickets", [(k, outs.get(k, 0), w) for k, w in wk.items() if outs.get(k, 0) != w])

    check("no innings has more than 11 batters",
          q("SELECT match_id, innings, COUNT(*) FROM batting_innings GROUP BY 1, 2 HAVING COUNT(*) > 11"))
    check("no innings has more than 10 wickets",
          q("SELECT match_id, innings, wickets FROM innings_totals WHERE wickets > 10"))
    # An umpire's miscounted over (Cricsheet flags it) can push an innings past 120.
    check("no innings over 120 legal balls",
          [r for r in q("SELECT match_id, innings, balls FROM innings_totals WHERE super_over = 0 AND balls > 120")
           if not raw[(r[0], r[1])][4]])
    # 11 players; from 2023 one impact player (12), plus any concussion substitute (13).
    check("each team lists 11 players (12-13 from 2023: impact player / concussion sub)",
          q("""SELECT a.match_id, a.team, COUNT(*) n, m.season FROM appearances a JOIN matches m USING (match_id)
               GROUP BY 1, 2 HAVING n < 11 OR n > 13 OR (n > 11 AND m.season < 2023)"""))
    check("winner is one of the two teams",
          q("SELECT match_id, winner FROM matches WHERE winner IS NOT NULL AND winner NOT IN (team1, team2)"))
    check("every match has a winner or a no-result",
          q("SELECT match_id, result FROM matches WHERE winner IS NULL AND COALESCE(result, '') <> 'no result'"))
    check("every season has a champion", q("SELECT season FROM seasons WHERE champion IS NULL"))
    check("every player in a scorecard has an appearance",
          q("""SELECT DISTINCT b.match_id, b.player_id FROM batting_innings b
               LEFT JOIN appearances a ON a.match_id = b.match_id AND a.player_id = b.player_id
               WHERE a.player_id IS NULL"""))
    check("every team is configured", q(
        "SELECT DISTINCT team FROM appearances WHERE team NOT IN (SELECT name FROM teams)"))
    check("one season per match date year",
          q("SELECT match_id FROM matches WHERE CAST(substr(date, 1, 4) AS INT) <> season"))

    dupes = q("""SELECT display_name, COUNT(*) FROM players GROUP BY 1 HAVING COUNT(*) > 1""")
    print(f"  info  players sharing a display name (UI must show team/years): {dupes}")
    print(f"  info  seasons: {q('SELECT season, matches FROM seasons')}")
    print(f"  info  results: {q("SELECT COALESCE(result, method, 'normal'), COUNT(*) FROM matches GROUP BY 1")}")

    print("\n3. Records (check by eye)")
    name = "(SELECT display_name FROM players p WHERE p.player_id = x.player_id)"
    print("  highest totals:", q("""SELECT team, runs || '/' || wickets, opponent, season FROM innings_totals
                                    WHERE super_over = 0 ORDER BY runs DESC LIMIT 5"""))
    print("  lowest completed totals:", q("""SELECT t.team, t.runs || '/' || t.wickets, t.season FROM innings_totals t
                                    JOIN matches m USING (match_id) WHERE super_over = 0 AND m.method IS NULL
                                    AND (t.wickets = 10 OR t.balls = 120) ORDER BY t.runs LIMIT 5"""))
    print("  top scores:", q(f"""SELECT {name}, runs || CASE WHEN is_out = 0 THEN '*' ELSE '' END, balls, season
                                FROM batting_innings x ORDER BY runs DESC, balls LIMIT 5"""))
    print("  best bowling:", q(f"""SELECT {name}, wickets || '/' || runs, season FROM bowling_innings x
                                  ORDER BY wickets DESC, runs LIMIT 5"""))
    print("  most runs:", q(f"""SELECT {name}, SUM(runs) FROM batting_innings x GROUP BY player_id ORDER BY 2 DESC LIMIT 5"""))
    print("  most wickets:", q(f"""SELECT {name}, SUM(wickets) FROM bowling_innings x GROUP BY player_id ORDER BY 2 DESC LIMIT 5"""))
    print("  most sixes:", q(f"""SELECT {name}, SUM(sixes) FROM batting_innings x GROUP BY player_id ORDER BY 2 DESC LIMIT 5"""))
    print("  most catches:", q(f"""SELECT {name}, SUM(catches + cb_catches) FROM fielding_innings x GROUP BY player_id ORDER BY 2 DESC LIMIT 5"""))
    print("  most matches:", q("SELECT display_name, matches FROM players ORDER BY matches DESC LIMIT 5"))

    if not args.no_net:
        print("\n4. Photo URLs (random sample of 25)")
        urls = [u for (u,) in q("SELECT image_url FROM players WHERE image_url IS NOT NULL")]
        bad = []
        for u in random.sample(urls, min(25, len(urls))):
            try:
                req = urllib.request.Request(u, method="GET", headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=15) as r:
                    # iplt20 answers missing photos with a grey silhouette SVG, so require a PNG.
                    if r.status != 200 or not r.headers.get("Content-Type", "").startswith("image/png"):
                        bad.append((u, r.status, r.headers.get("Content-Type")))
            except Exception as e:
                bad.append((u, str(e)))
        check("photo URLs load as real photos", bad)

    print(f"\n{'ALL CHECKS PASSED' if not failures else 'FAILED: ' + ', '.join(failures)}")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
