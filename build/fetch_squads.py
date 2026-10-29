"""
Fill build/player_names.csv with full names, photos, roles and countries from
iplt20.com squad lists, matched to Cricsheet player ids.

    python build/fetch_squads.py                 # fetch (cached) + match
    python build/fetch_squads.py --seasons 2027  # after a new season
    python build/fetch_squads.py --offline       # re-match from cache only

Run build_data.py first: matching uses data/ipl.sqlite to know which team and
season each Cricsheet player appeared in, so a name only has to be told apart
from the ~25 players in that squad.

Rows whose `source` column is "manual" are never overwritten, so hand fixes
stick. Uncertain matches are written to build/review_players.csv.
"""
import argparse
import collections
import csv
import difflib
import json
import os
import re
import sqlite3
import time
import unicodedata
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CACHE = os.path.join(HERE, "iplt20_cache")
NAMES_CSV = os.path.join(HERE, "player_names.csv")
REVIEW_CSV = os.path.join(HERE, "review_players.csv")
API = "https://www.iplt20.com/api/bff/cms/teams/{slug}?tab=squad&season={season}"

TEAM_SLUGS = {
    "Chennai Super Kings": "chennai-super-kings",
    "Delhi Capitals": "delhi-capitals",
    "Gujarat Titans": "gujarat-titans",
    "Kolkata Knight Riders": "kolkata-knight-riders",
    "Lucknow Super Giants": "lucknow-super-giants",
    "Mumbai Indians": "mumbai-indians",
    "Punjab Kings": "punjab-kings",
    "Rajasthan Royals": "rajasthan-royals",
    "Royal Challengers Bengaluru": "royal-challengers-bengaluru",
    "Sunrisers Hyderabad": "sunrisers-hyderabad",
}

FIRST_SQUAD_SEASON = 2012

ROLES = {"batsman": "Batter", "bowler": "Bowler", "allrounder": "All-Rounder"}

ACCEPT = 0.80   # match score needed to accept automatically
REVIEW = 0.55   # below this a candidate is ignored entirely

FIELDS = ["player_id", "cricsheet_name", "full_name", "image_url", "role",
          "country", "iplt20_id", "source"]


# ----------------------------------------------------------------------------
# Fetch
# ----------------------------------------------------------------------------
def fetch(slug, season, retries=3):
    """Squad list for one team-season. A season the site has no squad for is
    cached as [] so it is not asked for again; only network errors retry."""
    path = os.path.join(CACHE, f"{slug}_{season}.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    req = urllib.request.Request(API.format(slug=slug, season=season),
                                 headers={"User-Agent": "Mozilla/5.0 (ipl-analytics squad sync)"})
    players, last = None, None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                data = json.load(r).get("data", {})
            players = (data.get("squad") or {}).get("players") or []
            break
        except urllib.error.HTTPError as e:
            last = e
            if e.code == 404:
                players = []
                break
        except (urllib.error.URLError, TimeoutError, ValueError) as e:
            last = e
        time.sleep(2 * (attempt + 1))
    if players is None:
        print(f"  ! {slug} {season}: {last} (will retry next run)")
        return None
    os.makedirs(CACHE, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(players, fh)
    return players


def load_squads(db_path, seasons, offline):
    # Only ask for seasons a team actually played (no LSG in 2015, no CSK/RR
    # in 2016-17). iplt20.com has no squad lists before FIRST_SQUAD_SEASON.
    played = set(sqlite3.connect(db_path).execute(
        "SELECT DISTINCT team, season FROM appearances").fetchall())
    squads = {}
    for team, slug in TEAM_SLUGS.items():
        for season in seasons:
            if season < FIRST_SQUAD_SEASON or (team, season) not in played:
                continue
            cached = os.path.join(CACHE, f"{slug}_{season}.json")
            if offline and not os.path.exists(cached):
                continue
            was_cached = os.path.exists(cached)
            players = fetch(slug, season)
            if players:
                squads[(team, season)] = players
            if not was_cached:
                time.sleep(1.0)   # be polite to iplt20.com
    return squads


# ----------------------------------------------------------------------------
# Match
# ----------------------------------------------------------------------------
def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z ]", " ", s.lower()).split()


def similar(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio()


def score(cricsheet, known_full, candidate):
    """0..1: how likely a Cricsheet name ("V Suryavanshi") is this iplt20 name."""
    c, f = norm(cricsheet), norm(candidate)
    if not c or not f:
        return 0.0
    # Only an exact name scores 1.0, so it beats an initials match
    # ("RK Singh" fits both Rinku Singh and Ramandeep Singh).
    if c == f or (known_full and norm(known_full) == f):
        return 1.0
    whole = similar(" ".join(c), " ".join(f))
    if known_full:
        whole = max(whole, similar(" ".join(norm(known_full)), " ".join(f)))
    # Surname close to any part of the full name ("Suryavanshi" ~ "Sooryavanshi"),
    # and the same first initial.
    surname = max(similar(c[-1], t) for t in f)
    same_initial = 1.0 if c[0][0] == f[0][0] else 0.0
    by_surname = 0.6 * surname + 0.4 * same_initial if surname > 0.7 else 0.0
    return min(0.95, max(whole, by_surname))


def match(db_path, squads, existing):
    db = sqlite3.connect(db_path)
    rows = db.execute("""
        SELECT a.player_id, a.team, a.season, p.name
        FROM (SELECT DISTINCT player_id, team, season FROM appearances) a
        JOIN players p USING (player_id)
    """).fetchall()

    # Greedy one-to-one assignment inside each (team, season) squad.
    by_squad = collections.defaultdict(list)
    for pid, team, season, name in rows:
        if (team, season) in squads:
            by_squad[(team, season)].append((pid, name))

    votes = collections.defaultdict(list)       # pid -> [(score, season, player_dict)]
    for key, members in by_squad.items():
        squad = squads[key]
        pairs = []
        for pid, name in members:
            known = (existing.get(pid) or {}).get("full_name")
            for cand in squad:
                s = score(name, known, cand["name"])
                if s >= REVIEW:
                    pairs.append((s, pid, cand["externalId"], cand))
        used_p, used_c = set(), set()
        for s, pid, cid, cand in sorted(pairs, key=lambda x: -x[0]):
            if pid in used_p or cid in used_c:
                continue
            used_p.add(pid)
            used_c.add(cid)
            votes[pid].append((s, key[1], cand))

    results, review = {}, []
    names = dict(db.execute("SELECT player_id, name FROM players"))
    for pid, vs in votes.items():
        by_id = collections.defaultdict(list)
        for s, season, cand in vs:
            by_id[cand["externalId"]].append((s, season, cand))
        # The iplt20 player this Cricsheet id matched most often, best score first.
        cid, hits = max(by_id.items(), key=lambda kv: (len(kv[1]), max(h[0] for h in kv[1])))
        best = max(h[0] for h in hits)
        # This player's squad entries, most recent season first.
        cands = [h[2] for h in sorted(hits, key=lambda h: -h[1])]
        if best >= ACCEPT:
            results[pid] = cands
        else:
            review.append((pid, round(best, 2), cands))
    return results, review, names


# ----------------------------------------------------------------------------
# Photos: older seasons often only have a grey silhouette (an SVG) instead of a
# photo, so use the most recent squad entry that is a real PNG.
# ----------------------------------------------------------------------------
PHOTO_CACHE = os.path.join(CACHE, "photo_check.json")
photo_ok = {}


def is_real_photo(url):
    if url not in photo_ok:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                photo_ok[url] = r.headers.get("Content-Type", "").startswith("image/png")
        except urllib.error.URLError:
            return False   # not cached, so it is checked again next run
    return photo_ok[url]


def best_photo(cands):
    for c in cands:
        url = c.get("imageUrl") or ""
        if url and "default-headshot" not in url and is_real_photo(url):
            return url
    return ""


def to_row(pid, cs_name, cands, source):
    cand = cands[0]
    role = "WK-Batter" if cand.get("isWicketKeeper") else ROLES.get(cand.get("role"), cand.get("role"))
    return {
        "player_id": pid,
        "cricsheet_name": cs_name,
        "full_name": cand["name"],
        "image_url": best_photo(cands),
        "role": role or "",
        "country": cand.get("country", ""),
        "iplt20_id": cand.get("externalId", ""),
        "source": source,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=os.path.join(ROOT, "data", "ipl.sqlite"))
    ap.add_argument("--seasons", nargs="*", type=int, default=list(range(2008, 2027)))
    ap.add_argument("--offline", action="store_true", help="use cached squads only")
    args = ap.parse_args()

    existing = {}
    if os.path.exists(NAMES_CSV):
        with open(NAMES_CSV, encoding="utf-8") as fh:
            existing = {r["player_id"]: r for r in csv.DictReader(fh)}

    print(f"Loading squads for {len(args.seasons)} seasons ...")
    squads = load_squads(args.db, args.seasons, args.offline)
    print(f"  {len(squads)} team-season squads available")

    # Uncertain matches marked accept=y in the last review file become manual rows.
    accepted = set()
    if os.path.exists(REVIEW_CSV):
        with open(REVIEW_CSV, encoding="utf-8") as fh:
            accepted = {r["player_id"] for r in csv.DictReader(fh)
                        if (r.get("accept") or "").strip().lower() in ("y", "yes", "1")}

    results, review, cs_names = match(args.db, squads, existing)

    if os.path.exists(PHOTO_CACHE):
        with open(PHOTO_CACHE, encoding="utf-8") as fh:
            photo_ok.update(json.load(fh))
    print("Checking photos ...")

    out = dict(existing)
    updated = added = 0
    for pid, cands in results.items():
        if out.get(pid, {}).get("source") == "manual":
            # Hand-fixed rows keep their name and role; only a broken photo is refreshed.
            if not out[pid].get("image_url") or not is_real_photo(out[pid]["image_url"]):
                out[pid]["image_url"] = best_photo(cands)
            continue
        if pid in out:
            updated += 1
        else:
            added += 1
        out[pid] = to_row(pid, cs_names.get(pid, ""), cands, "iplt20")

    pending = []
    for pid, best, cands in review:
        if pid in accepted:
            out[pid] = to_row(pid, cs_names.get(pid, ""), cands, "manual")
        elif out.get(pid, {}).get("source") == "manual":
            if not out[pid].get("image_url") or not is_real_photo(out[pid]["image_url"]):
                out[pid]["image_url"] = best_photo(cands)
        else:
            pending.append((pid, cs_names.get(pid), cands[0]["name"], best, best_photo(cands), ""))


    # Old rows that iplt20 could not confirm keep their name; their photo is
    # dropped unless it still loads (the old image hosts are gone).
    for row in out.values():
        if not row.get("source"):
            row["source"] = "legacy"
        if row["source"] == "legacy" and row.get("image_url") and not is_real_photo(row["image_url"]):
            row["image_url"] = ""

    with open(PHOTO_CACHE, "w", encoding="utf-8") as fh:
        json.dump(photo_ok, fh)

    with open(NAMES_CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        for row in sorted(out.values(), key=lambda r: (r.get("full_name") or r.get("cricsheet_name") or "")):
            w.writerow({k: row.get(k, "") for k in FIELDS})

    with open(REVIEW_CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["player_id", "cricsheet_name", "best_iplt20_match", "score", "image_url", "accept"])
        w.writerows(sorted(pending, key=lambda r: -r[3]))

    print(f"Matched {len(results)} players ({added} new rows, {updated} updated)")
    if accepted:
        print(f"Applied {len(accepted)} accepted review rows as manual")
    print(f"{len(pending)} uncertain matches written to {os.path.relpath(REVIEW_CSV, ROOT)}"
          " (put y in the accept column to approve, then re-run)")
    print("Re-run build/build_data.py to apply.")


if __name__ == "__main__":
    main()
