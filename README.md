# IPL Analytics

Stats for every Indian Premier League season from 2008 to 2026: players, teams, head-to-heads, points tables, scorecards and records.

**Live site:** [balajiramesh2003.pythonanywhere.com](https://balajiramesh2003.pythonanywhere.com/)

- **1,243 matches**, ball by ball, from [Cricsheet](https://cricsheet.org)
- **Full names, photos and roles** for current players, from iplt20.com
- **Small and fast:** one 12 MB SQLite file, a Flask API with no other dependencies, and a plain HTML/CSS/JS frontend with no build step. It runs on PythonAnywhere's free tier.

---

## Features

| Page | What you get |
|---|---|
| **Home** | Latest champion and caps, every season's winner, record highlights |
| **Player** | Career numbers, runs or wickets per season, powerplay / middle / death splits, best and recent innings, toughest opponents |
| **Compare** | Two players side by side, and how they did against each other |
| **Team** | Titles, finishing position every season, record against every opponent, top players |
| **Head to head** | Wins each, recent form, top performers on both sides, every meeting |
| **Season** | Champions, Orange and Purple Cap, points table with NRR, playoffs, every match |
| **Match** | Full scorecard, run-rate worm and runs-per-over charts |
| **Records** | All-time leaderboards, filterable by season and team |

Works on desktop and mobile.

---

## Quick start

```bash
pip install -r requirements.txt     # just Flask
python app.py
```

Open http://127.0.0.1:5000.

---

## How it works

```
Cricsheet JSON  ─►  build/build_data.py    ─►  data/ipl.sqlite  ─►  app.py (Flask)  ─►  browser
iplt20.com      ─►  build/fetch_squads.py  ─►  build/player_names.csv  ──┘
```

All the heavy lifting runs **once, offline** with DuckDB. The server only looks up pre-computed tables: about 45 MB of memory, start-up under a second, most requests under 40 ms.

### Project structure

```
app.py                    Flask app: JSON API + page routes
requirements.txt          Server dependencies (Flask only)
data/
  ipl.sqlite              Pre-built database; the only data the server needs
templates/
  base.html               Shared layout (nav, search, footer)
  <page>.html             One template per page
static/
  css/style.css           The whole design; colours and timing are set at the top
  js/app.js               Shared helpers: API calls, search, badges, smooth scroll
  js/<page>.js            One small script per page
  images/teams/           Team logos (WebP, named by short code)
  images/winners/         Champions' photos by year
build/                    Offline tools (not needed on the server)
  build_data.py           Cricsheet JSON → data/ipl.sqlite
  fetch_squads.py         iplt20.com squads → player_names.csv
  validate_data.py        Checks the database against the raw data and known records
  player_names.csv        Full names, photos, roles (editable)
  requirements.txt        DuckDB + pandas, for the build tools
tests/
  test_api.py             API and page tests against official IPL figures
```

---

## Updating after a new season

Run these on your own machine, not on the server:

```bash
pip install -r build/requirements.txt

# 1. Download https://cricsheet.org/downloads/ipl_json.zip and unzip it into ipl_json/
python build/build_data.py                    # build the database
python build/fetch_squads.py --seasons 2027   # names and photos for new players
python build/build_data.py                    # rebuild with the new names
python build/validate_data.py                 # must end with ALL CHECKS PASSED
python -m unittest discover tests
```

`fetch_squads.py` writes any matches it isn't sure about to `build/review_players.csv`. Put `y` in the `accept` column for the correct ones and run it again. To fix a player by hand, edit their row in `build/player_names.csv` and set `source` to `manual`.

Then upload `data/ipl.sqlite` to PythonAnywhere and reload the web app.

---

## Deploying to PythonAnywhere (free tier)

1. Clone the repo into your home folder.
2. **Web** tab → *Add a new web app* → *Manual configuration* → Python 3.10+.
3. Edit the WSGI file:
   ```python
   import sys
   sys.path.insert(0, "/home/<username>/IPL_ANALYTICS")
   from app import app as application
   ```
4. Under **Static files**, map `/static/` to `/home/<username>/IPL_ANALYTICS/static/`.
5. Reload. Flask is preinstalled; if not, run `pip install --user -r requirements.txt`.

Free web apps must be renewed every 3 months: click *Run until 3 months from today* on the Web tab.

---

## API

All endpoints are `GET` and return JSON. Teams use short codes (`CSK`, `MI`, `RCB`…); players use their Cricsheet ID (find it with `/api/players?q=`).

<details>
<summary>All endpoints</summary>

| Endpoint | Returns |
|---|---|
| `/api` | Build info and the list of endpoints |
| `/api/seasons` | Every season: champion, runner-up, Orange / Purple Cap |
| `/api/seasons/<year>` | Points table with NRR, playoffs, top run-scorers and wicket-takers |
| `/api/teams` | All franchises with overall record and titles |
| `/api/teams/<team>` | Season-by-season finishes, top players, highest / lowest totals |
| `/api/teams/<team>/vs-all` | Record against every opponent |
| `/api/teams/<a>/vs/<b>` | Head-to-head results, top performers, every meeting |
| `/api/players?q=&team=&limit=` | Player search |
| `/api/players/<id>` | Career, by season, by phase, best innings, recent form |
| `/api/players/<id>/matchups` | Bowlers faced most / batters bowled to most |
| `/api/players/<a>/vs/<b>` | Two careers side by side, plus their direct battle |
| `/api/matches?season=&team=&opponent=&venue=` | Match list with scores and results |
| `/api/matches/<id>` | Full scorecard and over-by-over runs and wickets |
| `/api/records?season=&team=` | Leaderboards: runs, wickets, sixes, strike rate, economy, top scores, best figures, highest totals |

</details>

---

## Data notes

- Super overs are left out of player and team totals, as in official records.
- Matches washed out before a ball was bowled aren't in Cricsheet. The points table works them out from games played, so points match the official tables.
- Net run rate uses current IPL rules. A few rain-affected seasons from 2008–2010 were calculated differently at the time, so some NRRs from those years differ slightly from the published ones.
- Players who retired before 2012, or only played for teams that no longer exist, have no photo on iplt20.com. They show initials instead.

## Credits

Ball-by-ball data from [Cricsheet](https://cricsheet.org); please credit them if you reuse it. Player photos and squad details from [iplt20.com](https://www.iplt20.com). Charts by [Apache ECharts](https://echarts.apache.org), smooth scrolling by [Lenis](https://lenis.darkroom.engineering).
