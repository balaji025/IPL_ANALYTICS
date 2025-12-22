import os
import csv
import pickle as pkl
import json
import pandas as pd
import numpy as np

import matplotlib
matplotlib.use("Agg")  # IMPORTANT for PythonAnywhere
import matplotlib.pyplot as plt

import io
import base64

from flask import Flask, render_template, url_for, redirect, request, jsonify

# ----------------------------
# File paths (PythonAnywhere)
# ----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def data_path(filename: str) -> str:
    return os.path.join(BASE_DIR, filename)

# ----------------------------
# Load data (from same folder as app.py)
# ----------------------------
with open(data_path('final_players.pkl'), 'rb') as f:
    a = pkl.load(f)
    ba = a[(a['work'] == 'Batter') | (a['work'] == 'WK Keeper - Batter')]['name'].unique()
    bo = a[a['work'] == 'Bowler']['name'].unique()
    ar = a[a['work'] == 'All-Rounder']['name'].unique()
    a['name'] = a['name'].str.replace('\xa0', ' ')
    sp = a['name'].unique()

    #t = a['team'].str.replace('-', ' ').str.title().str.strip().unique()
    t = a['team'].fillna("").astype(str).str.replace('-', ' ').str.title().str.strip()
    t = sorted([x for x in t.unique() if x])

    a['new_team'] = a['team'].str.replace('-', ' ').str.title().str.strip()

w = pd.read_pickle(data_path("winners.pkl"))
f4 = pd.read_pickle(data_path("final4.pkl"))
t4 = pd.read_pickle(data_path("t4.pkl"))
cc = pd.read_pickle(data_path("cc.pkl"))

oandp = pd.read_pickle(data_path("oandp.pkl"))
orange = oandp['orange']
purple = oandp['purple']

maxs = pd.read_pickle(data_path("max_score.pkl"))
maxs['Max_score'] = maxs['Max_score'].map(int)

mins = pd.read_pickle(data_path("min_score.pkl"))
teamcomp = pd.read_pickle(data_path("teamcomp.pkl"))
points_nrr = pd.read_pickle(data_path("points_nrr.pkl"))
dept = pd.read_pickle(data_path("dept.pkl"))
comp = pd.read_pickle(data_path("tvalllabel.pkl"))

tl = pd.read_pickle(data_path("team_late.pkl"))
tl['wickets'] = tl['wickets'].astype(np.int16)

d = pd.read_pickle(data_path("deliveries.pkl"))
mp = pd.read_pickle(data_path("matches_played.pkl"))

# ----------------------------
# Flask app
# ----------------------------
app = Flask(__name__, template_folder="templates", static_folder="static")

@app.route('/')
def hello():
    return render_template('index.html', msg=list(t))

@app.route('/player-vs-player')
def hi1():
    return render_template('player-vs-player.html', msg=list(sp))

@app.route('/index')
def hi6():
    return render_template('index.html')

@app.route('/s-i-n-g-l-e-p-l-a-y-e-r')
def hi7():
    # Your old redirect('/test') did nothing. This endpoint should just render the page.
    return render_template('s-i-n-g-l-e-p-l-a-y-e-r.html', msg=list(sp))

@app.route('/s-p-bowling')
def hi8():
    return render_template('s-p-bowling.html')

@app.route('/s-p-batting')
def hi9():
    return render_template('s-p-batting.html')

@app.route('/team-vs-team')
def hi10():
    return render_template('team-vs-team.html', msg=list(t))

@app.route('/team')
def hi11():
    return render_template('team.html', msg=list(t))

@app.route('/team-vs-all')
def hi12():
    return render_template('team-vs-all.html', msg=list(t))

@app.route('/bestteams')
def bestteams():
    return render_template('best-teams.html')

'''
@app.route('/playervsplayer', methods=['POST'])
def playervsplayer():
    # IMPORTANT: removed loading D:/IPL/deliveries.pkl
    player1 = request.form.get('player1')
    player2 = request.form.get('player2')

    msgg1 = (a[a['name'] == player1].sort_values(by='year', ascending=False).head(1)['data'].values[0][0])
    msgg2 = (a[a['name'] == player2].sort_values(by='year', ascending=False).head(1)['data'].values[0][0])

    bdf1 = d[d['batter'] == player1]
    bdf2 = d[d['batter'] == player2]

    # batting
    if bdf1.shape[0] == 0:
        runs1 = avg1 = sr1 = fours1 = sixes1 = ' - '
    else:
        runs1 = str(bdf1['batter_runs'].sum())
        outs1 = bdf1[bdf1['player_out'] == player1].shape[0]
        avg1 = runs1 if outs1 == 0 else str(round(int(runs1) / outs1, 2))
        balls1 = bdf1[~(bdf1['extra_type'] == 'wides')].shape[0]
        sr1 = str(round((int(runs1) / balls1) * 100, 2)) if balls1 else '0'
        fours1 = str(bdf1[bdf1['batter_runs'] == 4].shape[0])
        sixes1 = str(bdf1[bdf1['batter_runs'] == 6].shape[0])

    if bdf2.shape[0] == 0:
        runs2 = avg2 = sr2 = fours2 = sixes2 = ' - '
    else:
        runs2 = str(bdf2['batter_runs'].sum())
        outs2 = bdf2[bdf2['player_out'] == player2].shape[0]
        avg2 = runs2 if outs2 == 0 else str(round(int(runs2) / outs2, 2))
        balls2 = bdf2[~(bdf2['extra_type'] == 'wides')].shape[0]
        sr2 = str(round((int(runs2) / balls2) * 100, 2)) if balls2 else '0'
        fours2 = str(bdf2[bdf2['batter_runs'] == 4].shape[0])
        sixes2 = str(bdf2[bdf2['batter_runs'] == 6].shape[0])

    # bowling
    bodf1 = d[d['bowler'] == player1]
    bodf2 = d[d['bowler'] == player2]

    def bowling_stats(bodf):
        if bodf.shape[0] == 0:
            return (' - ', ' - ', ' - ', ' - ', ' - ')
        finaldf = bodf[bodf['extra_type'].isin([np.nan, 'byes', 'legbyes', 'penalty'])]
        finaldf2 = bodf[bodf['extra_type'].isin([np.nan, 'byes', 'legbyes', 'penalty', 'wides', 'noballs'])]
        haulsdf = finaldf[finaldf['type_of_dismissal'].isin(
            ['stumped', 'caught', 'lbw', 'bowled', 'caught and bowled', 'hit wicket'])]

        overs = int(finaldf.shape[0] / 6)
        balls = finaldf.shape[0] - (overs * 6)
        overs_str = f"{overs}.{balls}"
        wickets = str(int(haulsdf['wickets'].sum()))

        if float(overs_str) < 1.0:
            economy = str(round((finaldf2['total_runs'].sum() * 6 / float(balls)), 2)) if balls else '0'
        else:
            economy = str(round((finaldf2['total_runs'].sum() / float(overs_str)), 2))

        try:
            srt = str(round((float(overs_str) * 6) / int(wickets), 2))
        except ZeroDivisionError:
            srt = 'inf'

        wicket3 = str((haulsdf.groupby(['season', 'match_no'])['wickets'].sum() >= 3).values.sum())
        return (overs_str, wickets, economy, srt, wicket3)

    overs1, wickets1, economy1, srt1, wicket31 = bowling_stats(bodf1)
    overs2, wickets2, economy2, srt2, wicket32 = bowling_stats(bodf2)

    # fielding
    def fielding_stats(player):
        fdf = d[(d['fielder1'] == player) | (d['fielder2'] == player) | (d['fielder3'] == player)]
        vc = fdf[fdf['type_of_dismissal'].isin(['caught', 'caught and bowled', 'run out', 'stumped'])]['type_of_dismissal'].value_counts()
        runout = str(vc.get('run out', 0))
        stumped = str(vc.get('stumped', 0))
        catch1 = int(vc.get('caught', 0))
        catch2 = len(d[(d['type_of_dismissal'] == 'caught and bowled') & (d['bowler'] == player)])
        return runout, stumped, str(catch1 + catch2)

    runout1, stumped1, catch1 = fielding_stats(player1)
    runout2, stumped2, catch2 = fielding_stats(player2)

    # Matchups
    l = ['stumped', 'caught', 'lbw', 'bowled', 'caught and bowled', 'hit wicket']

    mdf1 = d[(d['batter'] == player1) & (d['bowler'] == player2)]
    runs_m1 = mdf1['batter_runs'].sum()
    balls_m1 = mdf1[~(mdf1['extra_type'] == 'wides') | (mdf1['extra_type'] == 'noballs')].shape[0]
    sr_m1 = round((runs_m1 / balls_m1) * 100, 2) if balls_m1 else 0
    d1 = mdf1[mdf1['type_of_dismissal'].isin(l)]
    avg_m1 = round((runs_m1 / d1.shape[0]), 2) if d1.shape[0] else runs_m1
    dismissed_m1 = d1.shape[0]
    economy_m1 = round((runs_m1 * 6 / balls_m1), 2) if balls_m1 else 0
    bpb_m1 = round((balls_m1 / mdf1[mdf1['batter_runs'].isin([4, 6])].shape[0]), 2) if mdf1[mdf1['batter_runs'].isin([4, 6])].shape[0] else 0

    mdf2 = d[(d['batter'] == player2) & (d['bowler'] == player1)]
    runs_m2 = mdf2['batter_runs'].sum()
    balls_m2 = mdf2[~(mdf2['extra_type'] == 'wides') | (mdf2['extra_type'] == 'noballs')].shape[0]
    sr_m2 = round((runs_m2 / balls_m2) * 100, 2) if balls_m2 else 0
    d2 = mdf2[mdf2['type_of_dismissal'].isin(l)]
    avg_m2 = round((runs_m2 / d2.shape[0]), 2) if d2.shape[0] else runs_m2
    dismissed_m2 = d2.shape[0]
    economy_m2 = round((runs_m2 * 6 / balls_m2), 2) if balls_m2 else 0
    bpb_m2 = round((balls_m2 / mdf2[mdf2['batter_runs'].isin([4, 6])].shape[0]), 2) if mdf2[mdf2['batter_runs'].isin([4, 6])].shape[0] else 0

    mat_played1 = str(mp[mp['players'] == player1]['matches'].values[0])
    mat_played2 = str(mp[mp['players'] == player2]['matches'].values[0])

    return jsonify(
        result1=msgg1, result2=msgg2,
        runs1=runs1, avg1=avg1, sr1=sr1, fours1=fours1, sixes1=sixes1,
        runs2=runs2, avg2=avg2, sr2=sr2, fours2=fours2, sixes2=sixes2,
        overs1=overs1, wickets1=wickets1, economy1=economy1, srt1=srt1, wicket31=wicket31,
        overs2=overs2, wickets2=wickets2, economy2=economy2, srt2=srt2, wicket32=wicket32,
        runout1=runout1, stumped1=stumped1, catch1=catch1,
        runout2=runout2, stumped2=stumped2, catch2=catch2,
        runs_m1=str(runs_m1), balls_m1=str(balls_m1), sr_m1=str(sr_m1), avg_m1=str(avg_m1),
        dismissed_m1=str(dismissed_m1), economy_m1=str(economy_m1), balls_per_boundary_m1=str(bpb_m1),
        runs_m2=str(runs_m2), balls_m2=str(balls_m2), sr_m2=str(sr_m2), avg_m2=str(avg_m2),
        dismissed_m2=str(dismissed_m2), economy_m2=str(economy_m2), balls_per_boundary_m2=str(bpb_m2),
        mat_played1=mat_played1, mat_played2=mat_played2
    )
'''


@app.route('/playervsplayer', methods=['POST'])
def playervsplayer():
    player1 = (request.form.get('player1') or '').strip()
    player2 = (request.form.get('player2') or '').strip()

    # basic validation
    if not player1 or not player2 or player1 == "Select Player" or player2 == "Select Player":
        return jsonify(error="Select both players"), 400

    def safe_headshot(player):
        try:
            s = a.loc[a['name'] == player].sort_values('year', ascending=False).head(1)
            if len(s) and isinstance(s['data'].values[0], (list, tuple)) and len(s['data'].values[0]) > 0:
                return s['data'].values[0][0]
        except Exception:
            pass
        return "https://www.iplt20.com/assets/images/default-headshot.png"

    msgg1 = safe_headshot(player1)
    msgg2 = safe_headshot(player2)

    # ---------- batting ----------
    def batting_stats(player):
        bdf = d[d['batter'] == player]
        if bdf.empty:
            return (' - ', ' - ', ' - ', ' - ', ' - ')
        runs_int = int(bdf['batter_runs'].sum())
        outs = int((bdf['player_out'] == player).sum())
        balls = int((bdf['extra_type'] != 'wides').sum())
        avg = str(runs_int) if outs == 0 else str(round(runs_int / outs, 2))
        sr = str(round((runs_int / balls) * 100, 2)) if balls else '0'
        fours = str(int((bdf['batter_runs'] == 4).sum()))
        sixes = str(int((bdf['batter_runs'] == 6).sum()))
        return (str(runs_int), avg, sr, fours, sixes)

    runs1, avg1, sr1, fours1, sixes1 = batting_stats(player1)
    runs2, avg2, sr2, fours2, sixes2 = batting_stats(player2)

    # ---------- bowling ----------
    def bowling_stats(player):
        bodf = d[d['bowler'] == player]
        if bodf.empty:
            return (' - ', ' - ', ' - ', ' - ', ' - ')
        finaldf = bodf[bodf['extra_type'].isin([np.nan, 'byes', 'legbyes', 'penalty'])]
        finaldf2 = bodf[bodf['extra_type'].isin([np.nan, 'byes', 'legbyes', 'penalty', 'wides', 'noballs'])]
        haulsdf = finaldf[finaldf['type_of_dismissal'].isin(
            ['stumped', 'caught', 'lbw', 'bowled', 'caught and bowled', 'hit wicket']
        )]
        overs = int(finaldf.shape[0] / 6)
        balls = int(finaldf.shape[0] - (overs * 6))
        overs_str = f"{overs}.{balls}"
        wk = int(haulsdf['wickets'].sum())
        wickets = str(wk)

        # economy safe
        if overs == 0 and balls > 0:
            economy = str(round((finaldf2['total_runs'].sum() * 6 / balls), 2))
        else:
            economy = str(round((finaldf2['total_runs'].sum() / float(overs_str)), 2)) if float(overs_str) > 0 else '0'

        srt = str(round((float(overs_str) * 6) / wk, 2)) if wk else 'inf'
        wicket3 = str(int((haulsdf.groupby(['season', 'match_no'])['wickets'].sum() >= 3).sum()))
        return (overs_str, wickets, economy, srt, wicket3)

    overs1, wickets1, economy1, srt1, wicket31 = bowling_stats(player1)
    overs2, wickets2, economy2, srt2, wicket32 = bowling_stats(player2)

    # ---------- fielding ----------
    def fielding_stats(player):
        try:
            fdf = d[(d['fielder1'] == player) | (d['fielder2'] == player) | (d['fielder3'] == player)]
            vc = fdf[fdf['type_of_dismissal'].isin(['caught', 'caught and bowled', 'run out', 'stumped'])]['type_of_dismissal'].value_counts()
            runout = str(int(vc.get('run out', 0)))
            stumped = str(int(vc.get('stumped', 0)))
            catch1 = int(vc.get('caught', 0))
            catch2 = int(((d['type_of_dismissal'] == 'caught and bowled') & (d['bowler'] == player)).sum())
            return runout, stumped, str(catch1 + catch2)
        except Exception:
            return "0", "0", "0"

    runout1, stumped1, catch1 = fielding_stats(player1)
    runout2, stumped2, catch2 = fielding_stats(player2)

    # ---------- matches played ----------
    def safe_matches(player):
        try:
            s = mp.loc[mp['players'] == player, 'matches']
            return str(s.values[0]) if len(s) else ' - '
        except Exception:
            return ' - '

    mat_played1 = safe_matches(player1)
    mat_played2 = safe_matches(player2)

    # ---------- matchup ----------
    # keep your keys, but make it uncrashable
    l = ['stumped', 'caught', 'lbw', 'bowled', 'caught and bowled', 'hit wicket']

    def matchup(batter, bowler):
        mdf = d[(d['batter'] == batter) & (d['bowler'] == bowler)]
        runs_m = int(mdf['batter_runs'].sum()) if not mdf.empty else 0
        balls_m = int(mdf[(mdf['extra_type'] != 'wides') | (mdf['extra_type'] == 'noballs')].shape[0]) if not mdf.empty else 0
        sr_m = round((runs_m / balls_m) * 100, 2) if balls_m else 0
        dmiss = mdf[mdf['type_of_dismissal'].isin(l)]
        dismissed = int(dmiss.shape[0])
        avg_m = round((runs_m / dismissed), 2) if dismissed else runs_m
        economy_m = round((runs_m * 6 / balls_m), 2) if balls_m else 0
        boundary_ct = int(mdf[mdf['batter_runs'].isin([4, 6])].shape[0]) if not mdf.empty else 0
        bpb = round((balls_m / boundary_ct), 2) if boundary_ct else 0
        return runs_m, balls_m, sr_m, avg_m, dismissed, economy_m, bpb

    runs_m1, balls_m1, sr_m1, avg_m1, dismissed_m1, economy_m1, bpb_m1 = matchup(player1, player2)
    runs_m2, balls_m2, sr_m2, avg_m2, dismissed_m2, economy_m2, bpb_m2 = matchup(player2, player1)

    return jsonify(
        result1=msgg1, result2=msgg2,
        runs1=runs1, avg1=avg1, sr1=sr1, fours1=fours1, sixes1=sixes1,
        runs2=runs2, avg2=avg2, sr2=sr2, fours2=fours2, sixes2=sixes2,
        overs1=overs1, wickets1=wickets1, economy1=economy1, srt1=srt1, wicket31=wicket31,
        overs2=overs2, wickets2=wickets2, economy2=economy2, srt2=srt2, wicket32=wicket32,
        runout1=runout1, stumped1=stumped1, catch1=catch1,
        runout2=runout2, stumped2=stumped2, catch2=catch2,
        runs_m1=str(runs_m1), balls_m1=str(balls_m1), sr_m1=str(sr_m1), avg_m1=str(avg_m1),
        dismissed_m1=str(dismissed_m1), economy_m1=str(economy_m1), balls_per_boundary_m1=str(bpb_m1),
        runs_m2=str(runs_m2), balls_m2=str(balls_m2), sr_m2=str(sr_m2), avg_m2=str(avg_m2),
        dismissed_m2=str(dismissed_m2), economy_m2=str(economy_m2), balls_per_boundary_m2=str(bpb_m2),
        mat_played1=mat_played1, mat_played2=mat_played2
    )



# ----------------------------
# Test (POST) - Single Player endpoint (FULL)
# ----------------------------
@app.route('/test', methods=['POST'])
def test():
    from datetime import datetime

    player = request.form.get('player')
    dt = datetime.now()

    # Optional logging (won't break if check.csv missing)
    try:
        df = pd.read_csv(data_path('check.csv'))
        df['player'] = player
        df['time'] = dt
        # df.to_csv(data_path('check.csv'), index=False)
    except Exception:
        pass

    # ----------------------------
    # Player headshot / image url
    # ----------------------------
    try:
        msgg = (
            a[a['name'] == player]
            .sort_values(by='year', ascending=False)
            .head(1)['data'].values[0][0]
        )
    except Exception:
        msgg = "https://www.iplt20.com/assets/images/default-headshot.png"

    # ----------------------------
    # Batting stats
    # ----------------------------
    bdf = d[d['batter'] == player]

    if bdf.shape[0] == 0:
        runs = avg = sr = ' - '
        plus30 = plus100 = ' - '
        fours = sixes = ' - '
        image_base64 = "nodata"
        p1 = ' - '
        mat_played = ' - '
        tpf = ' - '
    else:
        runs_int = int(bdf['batter_runs'].sum())
        runs = str(runs_int)

        outs = bdf[bdf['player_out'] == player].shape[0]
        avg = runs if outs == 0 else str(round(runs_int / outs, 2))

        balls = bdf[~(bdf['extra_type'] == 'wides')].shape[0]
        sr = str(round((runs_int / balls) * 100, 2)) if balls else '0'

        arr = (bdf.groupby(['season', 'match_no'])['batter_runs'].sum()).values
        plus30 = str(int((arr >= 30).sum()))
        plus100 = str(int((arr >= 100).sum()))

        fours = str(int((bdf['batter_runs'] == 4).sum()))
        sixes = str(int((bdf['batter_runs'] == 6).sum()))

        # Matches played
        try:
            mat_played = str(mp[mp['players'] == player]['matches'].values[0])
        except Exception:
            mat_played = ' - '

        # Teams played for
        try:
            teams = (
                a[a['name'] == player]
                .sort_values(by='year')['new_team']
                .dropna()
                .unique()
            )
            tpf = "  ,  ".join([str(x) for x in teams]) if len(teams) else ' - '
        except Exception:
            tpf = ' - '

        # Batting best performance (p1)
        try:
            vk = d[d['batter'] == player]
            g_bat = vk.groupby(['season', 'match_no', 'innings'])
            group_list = [vk.loc[idx] for _, idx in g_bat.groups.items()]

            bat_rows = []
            for i in group_list:
                match_no_1 = i['match_no'].unique()[0]
                season_1 = i['season'].values[0]
                opponent_1 = i['bowling_team'].unique()[0]
                runs_1 = int(i['batter_runs'].sum())
                balls_1 = int(i[~(i['extra_type'] == 'wides')].shape[0])
                sr_1 = round((runs_1 / balls_1) * 100, 2) if balls_1 else np.nan
                bat_rows.append((season_1, match_no_1, runs_1, sr_1, balls_1, opponent_1))

            batdf = pd.DataFrame(bat_rows, columns=['season', 'match_no', 'runs', 'sr', 'balls', 'opponent'])
            f = batdf.sort_values(by=['runs', 'sr'], ascending=[False, False]).head(1)
            if f.shape[0] == 0:
                p1 = ' - '
            else:
                p1 = f"{f['runs'].values[0]}({f['balls'].values[0]}) in {f['season'].values[0]} VS {f['opponent'].values[0]}."
        except Exception:
            p1 = ' - '

        # Batting graph (runs by season)
        try:
            x = np.array(vk.groupby('season')['batter_runs'].sum().index)
            y = np.array(vk.groupby('season')['batter_runs'].sum().values)

            if len(x) == 0 or len(y) == 0:
                image_base64 = "nodata"
            else:
                fig, ax = plt.subplots()

                if len(x) == 1:
                    ax.bar(x, y)
                else:
                    ax.plot(x, y, linewidth=3)

                ax.patch.set_alpha(0)
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['bottom'].set_visible(False)
                ax.spines['left'].set_visible(False)
                ax.tick_params(axis="x", labelsize=12, labelcolor='white')
                ax.tick_params(axis="y", labelsize=12, labelcolor='white')

                buf = io.BytesIO()
                plt.savefig(buf, format='png', transparent=True, bbox_inches="tight")
                plt.close(fig)
                buf.seek(0)
                image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        except Exception:
            image_base64 = "nodata"

    # ----------------------------
    # Bowling stats + graph
    # ----------------------------
    bodf = d[d['bowler'] == player]

    if bodf.shape[0] == 0:
        overs = wickets = economy = aveg = srt = wicket3 = wicket5 = ' - '
        image_base641 = "nodata"
        p2 = ' - '
    else:
        finaldf = bodf[bodf['extra_type'].isin([np.nan, 'byes', 'legbyes', 'penalty'])]
        finaldf2 = bodf[bodf['extra_type'].isin([np.nan, 'byes', 'legbyes', 'penalty', 'wides', 'noballs'])]

        haulsdf = finaldf[finaldf['type_of_dismissal'].isin(
            ['stumped', 'caught', 'lbw', 'bowled', 'caught and bowled', 'hit wicket']
        )]

        ovs = int(finaldf.shape[0] / 6)
        balls_rem = int(finaldf.shape[0] - (ovs * 6))
        overs = f"{ovs}.{balls_rem}"

        wickets_int = int(haulsdf['wickets'].sum())
        wickets = str(wickets_int)

        # economy
        if ovs == 0 and balls_rem > 0:
            economy = str(round((finaldf2['total_runs'].sum() * 6 / balls_rem), 2))
        else:
            economy = str(round((finaldf2['total_runs'].sum() / float(overs)), 2)) if float(overs) > 0 else '0'

        # average + strike rate
        aveg = str(round((finaldf2['total_runs'].sum() / wickets_int), 2)) if wickets_int else 'inf'
        srt = str(round(((float(overs) * 6) / wickets_int), 2)) if wickets_int else 'inf'

        wicket3 = str(int((haulsdf.groupby(['season', 'match_no'])['wickets'].sum() >= 3).sum()))
        wicket5 = str(int((haulsdf.groupby(['season', 'match_no'])['wickets'].sum() >= 5).sum()))

        # Bowling best performance (p2)
        try:
            jb = d[d['bowler'] == player]
            g_bowl = jb.groupby(['season', 'match_no', 'innings'])
            group_list1 = [jb.loc[idx] for _, idx in g_bowl.groups.items()]

            bowl_rows = []
            for i in group_list1:
                season_2 = i['season'].unique()[0]
                opponent_2 = i['batting_team'].unique()[0]
                match_no_2 = i['match_no'].unique()[0]

                fdf_2 = i[i['extra_type'].isin([np.nan, 'byes', 'legbyes', 'penalty'])]
                fdf2_2 = i[i['extra_type'].isin([np.nan, 'byes', 'legbyes', 'penalty', 'wides', 'noballs'])]

                hdf_2 = fdf_2[fdf_2['type_of_dismissal'].isin(
                    ['stumped', 'caught', 'lbw', 'bowled', 'caught and bowled', 'hit wicket']
                )]

                ovs2 = int(fdf_2.shape[0] / 6)
                balls2 = int(fdf_2.shape[0] - (ovs2 * 6))
                overs_2 = f"{ovs2}.{balls2}"

                wk2 = int(hdf_2['wickets'].sum())
                runs_2 = int(fdf2_2['total_runs'].sum())

                econ2 = round((runs_2 / float(overs_2)), 2) if float(overs_2) > 0 else np.nan
                srt2 = round(((float(overs_2) * 6) / wk2), 2) if wk2 else np.nan

                bowl_rows.append((season_2, opponent_2, match_no_2, overs_2, wk2, runs_2, econ2, srt2))

            bowldf = pd.DataFrame(bowl_rows, columns=['season', 'opponent', 'match_no', 'overs', 'wickets', 'runs', 'economy', 'srt'])
            f1 = bowldf.sort_values(by=['wickets', 'economy', 'srt'], ascending=[False, True, True]).head(1)

            if f1.shape[0] == 0:
                p2 = ' - '
            else:
                p2 = f"{f1['wickets'].values[0]}/{f1['runs'].values[0]} in {f1['overs'].values[0]} overs VS {f1['opponent'].values[0]} in {f1['season'].values[0]}."
        except Exception:
            p2 = ' - '

        # Bowling graph (wickets by season)
        try:
            e = d[(d['bowler'] == player) & (d['type_of_dismissal'].isin(
                ['stumped', 'caught', 'lbw', 'bowled', 'caught and bowled', 'hit wicket']
            ))]

            x1 = np.array(e.groupby('season')['wickets'].sum().index)
            y1 = np.array(e.groupby('season')['wickets'].sum().values)

            if len(x1) == 0 or len(y1) == 0:
                image_base641 = "nodata"
            else:
                fig1, ax1 = plt.subplots()

                if len(x1) == 1:
                    ax1.bar(x1, y1)
                else:
                    ax1.plot(x1, y1, linewidth=3)

                ax1.patch.set_alpha(0)
                ax1.spines['top'].set_visible(False)
                ax1.spines['right'].set_visible(False)
                ax1.spines['bottom'].set_visible(False)
                ax1.spines['left'].set_visible(False)
                ax1.tick_params(axis="x", labelsize=12, labelcolor='white')
                ax1.tick_params(axis="y", labelsize=12, labelcolor='white')

                buf1 = io.BytesIO()
                plt.savefig(buf1, format='png', transparent=True, bbox_inches="tight")
                plt.close(fig1)
                buf1.seek(0)
                image_base641 = base64.b64encode(buf1.getvalue()).decode('utf-8')
        except Exception:
            image_base641 = "nodata"

    # ----------------------------
    # Fielding stats
    # ----------------------------
    try:
        fdf = d[(d['fielder1'] == player) | (d['fielder2'] == player) | (d['fielder3'] == player)]
        vc = fdf[fdf['type_of_dismissal'].isin(['caught', 'caught and bowled', 'run out', 'stumped'])]['type_of_dismissal'].value_counts()
        runout = str(int(vc.get('run out', 0)))
        stumped = str(int(vc.get('stumped', 0)))

        catch1 = int(vc.get('caught', 0))
        catch2 = int(((d['type_of_dismissal'] == 'caught and bowled') & (d['bowler'] == player)).sum())
        catch = str(catch1 + catch2)
    except Exception:
        runout = stumped = catch = '0'

    return jsonify(
        result=msgg,
        player=player,

        # batting
        runs=runs, avg=avg, sr=sr,
        plus30=plus30, plus100=plus100,
        fours=fours, sixes=sixes,

        # bowling
        overs=overs, wickets=wickets,
        economy=economy, aveg=aveg, srt=srt,
        wicket3=wicket3, wicket5=wicket5,

        # fielding
        runout=runout, stumped=stumped, catch=catch,

        # graphs + extras
        image=image_base64, image1=image_base641,
        p1=p1, p2=p2,
        tpf=tpf,
        mat_played=mat_played
    )


'''
@app.route('/teamlabel',methods=['POST'])
def teamlabel():
    team=request.form.get('team')
    if team not in w.keys():
        msg='No Trophies Yet'
    else:
        msg=w[team].lstrip()
    matches_played = str(f4[f4['Teams']==team]['Matches_played'].values[0])
    matches_won = str(f4[f4['Teams'] == team]['Matches_won'].values[0])
    matches_lost = str(f4[f4['Teams'] == team]['Matches_lost'].values[0])
    matches_no_result = str(f4[f4['Teams'] == team]['No result'].values[0])
    top4=str(t4[t4['index']==team]['Team'].values[0])
    cap=str(cc[cc['team']==team]['name'].values[0])
    maxscoredf=maxs[maxs['Team2']==team]
    maxvalue=maxscoredf['Max_score'].max()
    maxscoreyear=maxscoredf[maxscoredf['Max_score']==maxvalue]['Year'].values[0]
    minscoredf=mins[mins['Team1']==team]
    minvalue=minscoredf['Score'].min()
    minscoreyear=minscoredf[minscoredf['Score']==minvalue]['20Date'].values
    if len(minscoreyear)==1:
        min_score=str(minvalue)+'  in  '+str(minscoreyear[0])
    else:
        s=''
        for i in minscoreyear:
            s+=str(i)+'  ,  '
        s=s[:-3]
        min_score = str(minvalue) + '  in  ' + s
    hrs=str((tl[tl['Team']==team]['Top scorer'].values[0]))+'  ( '+str((tl[tl['Team']==team]['runs'].values[0]))+' )'
    hwt=str((tl[tl['Team']==team]['Top wicket taker'].values[0]))+'  ( '+str((tl[tl['Team']==team]['wickets'].values[0]))+' )'
    max_score=str(maxvalue)+'  in  '+str(maxscoreyear)
    if team not in orange.keys():
        or_cap='No one yet'
    else:
        or_cap=orange[team]+'   '
    if team not in purple.keys():
        pr_cap = 'No one yet'
    else:
        pr_cap = purple[team]+'   '

    return jsonify(hrs=hrs,hwt=hwt,trophies=msg,played=matches_played,won=matches_won,lost=matches_lost,nr=matches_no_result,top4=top4,captain=cap,or_cap=or_cap,pr_cap=pr_cap,max_score=max_score,min_score=min_score)
'''

@app.route('/teamlabel', methods=['POST'])
def teamlabel():
    team = (request.form.get('team') or '').strip()

    if not team or team == 'Select Team':
        return jsonify(error="Please select a team"), 400

    def safe_one(df, mask, col, default='0'):
        s = df.loc[mask, col]
        return str(s.values[0]) if len(s) else str(default)

    trophies = w.get(team, '').lstrip()
    msg = trophies if trophies else 'No Trophies Yet'

    matches_played = safe_one(f4, (f4['Teams'] == team), 'Matches_played', '0')
    matches_won = safe_one(f4, (f4['Teams'] == team), 'Matches_won', '0')
    matches_lost = safe_one(f4, (f4['Teams'] == team), 'Matches_lost', '0')
    matches_no_result = safe_one(f4, (f4['Teams'] == team), 'No result', '0')

    top4 = safe_one(t4, (t4['index'] == team), 'Team', '0/0')
    captain = safe_one(cc, (cc['team'] == team), 'name', '-')

    # Max score
    maxscoredf = maxs[maxs['Team2'] == team]
    if maxscoredf.empty:
        max_score = '-'
    else:
        maxvalue = int(maxscoredf['Max_score'].max())
        maxscoreyear = safe_one(maxscoredf, (maxscoredf['Max_score'] == maxvalue), 'Year', '-')
        max_score = f"{maxvalue}  in  {maxscoreyear}"

    # Min score
    minscoredf = mins[mins['Team1'] == team]
    if minscoredf.empty:
        min_score = '-'
    else:
        minvalue = minscoredf['Score'].min()
        dates = minscoredf.loc[minscoredf['Score'] == minvalue, '20Date'].values
        if len(dates) == 0:
            min_score = '-'
        elif len(dates) == 1:
            min_score = f"{minvalue}  in  {dates[0]}"
        else:
            min_score = f"{minvalue}  in  " + "  ,  ".join([str(x) for x in dates])

    # Top scorer / wicket taker
    top_scorer = safe_one(tl, (tl['Team'] == team), 'Top scorer', '-')
    top_runs = safe_one(tl, (tl['Team'] == team), 'runs', '0')
    hrs = f"{top_scorer}  ( {top_runs} )"

    top_wt = safe_one(tl, (tl['Team'] == team), 'Top wicket taker', '-')
    top_wickets = safe_one(tl, (tl['Team'] == team), 'wickets', '0')
    hwt = f"{top_wt}  ( {top_wickets} )"

    or_cap = (orange.get(team, 'No one yet') + '   ') if team in orange else 'No one yet'
    pr_cap = (purple.get(team, 'No one yet') + '   ') if team in purple else 'No one yet'

    return jsonify(
        hrs=hrs, hwt=hwt,
        trophies=msg,
        played=matches_played, won=matches_won, lost=matches_lost, nr=matches_no_result,
        top4=top4, captain=captain,
        or_cap=or_cap, pr_cap=pr_cap,
        max_score=max_score, min_score=min_score
    )


@app.route('/teamvsteamlabel', methods=['POST'])
def teamvsteamlabel():
    team1 = (request.form.get('team1') or '').strip()
    team2 = (request.form.get('team2') or '').strip()

    # Basic validation
    if not team1 or not team2 or team1 == 'Select Team' or team2 == 'Select Team':
        return jsonify(error="Please select both teams"), 400
    if team1 == team2:
        return jsonify(error="Please select two different teams"), 400

    # Helper: safe lookup in dataframe
    def safe_df_value(df_, mask, col, default='0'):
        s = df_.loc[mask, col]
        return str(s.values[0]) if len(s) else str(default)

    # 1) Head-to-head matches
    # Make sure we only match rows where the (team1, team2) pair is exactly these two teams in any order
    df = teamcomp[
        (teamcomp['team1'].isin([team1, team2])) &
        (teamcomp['team2'].isin([team1, team2]))
    ].copy()

    total_matches_int = int(df.shape[0])
    total_matches = str(total_matches_int)

    # wins / no-result (never crash)
    if total_matches_int == 0:
        t1won_int = 0
        t2won_int = 0
        nr_int = 0
    else:
        vc = df['winning_team'].value_counts()
        t1won_int = int(vc.get(team1, 0))
        t2won_int = int(vc.get(team2, 0))
        nr_int = int(df[df['winning_team'] == 'No result'].shape[0])

    t1won = str(t1won_int)
    t2won = str(t2won_int)
    nr = str(nr_int)

    # win% (avoid division by zero)
    if total_matches_int == 0:
        t1winper = "0 %"
        t2winper = "0 %"
    else:
        t1winper = f"{round((t1won_int / total_matches_int) * 100, 2)}  %"
        t2winper = f"{round((t2won_int / total_matches_int) * 100, 2)}  %"

    # 2) Trophies / Top4 appearances text (msg1/msg2) and m1/m2
    # t4 table lookups can crash if team string mismatches -> make safe
    t4_team1 = safe_df_value(t4, (t4['index'] == team1), 'Team', default="0/0")
    t4_team2 = safe_df_value(t4, (t4['index'] == team2), 'Team', default="0/0")

    # msg = "trophies / finals(or top4 etc)" -> keep your original split logic safely
    def build_msg(team, t4_val):
        denom = "0"
        try:
            denom = str(str(t4_val).split('/')[1])
        except Exception:
            denom = "0"

        if team not in w.keys():
            num = "0"
        else:
            # count trophies (based on your stored string)
            try:
                num = str(len(w[team].strip().split()))
            except Exception:
                num = "0"
        return f"{num}  / {denom}"

    msg1 = build_msg(team1, t4_team1)
    msg2 = build_msg(team2, t4_team2)

    m1 = str(t4_team1)
    m2 = str(t4_team2)

    # 3) Orange / Purple cap counts (safe)
    def cap_count(dct, team):
        if team not in dct.keys():
            return "0"
        try:
            return str(len(str(dct[team]).split('     ')))
        except Exception:
            return "0"

    or_cap1 = cap_count(orange, team1)
    or_cap2 = cap_count(orange, team2)
    pur_cap1 = cap_count(purple, team1)
    pur_cap2 = cap_count(purple, team2)

    # 4) NRR means (safe)
    try:
        nrr1_val = points_nrr.loc[points_nrr['name'] == team1, 'nrr'].mean()
        nrr1 = str(round(float(nrr1_val), 2)) if pd.notna(nrr1_val) else "0"
    except Exception:
        nrr1 = "0"

    try:
        nrr2_val = points_nrr.loc[points_nrr['name'] == team2, 'nrr'].mean()
        nrr2 = str(round(float(nrr2_val), 2)) if pd.notna(nrr2_val) else "0"
    except Exception:
        nrr2 = "0"

    # 5) Dept better in (safe)
    d1_series = dept.loc[dept['Team1'] == team1, 'dept']
    d2_series = dept.loc[dept['Team1'] == team2, 'dept']
    d1 = str(d1_series.values[0]) if len(d1_series) else "-"
    d2 = str(d2_series.values[0]) if len(d2_series) else "-"

    return jsonify(
        total_matches=total_matches,
        t1won=t1won,
        t2won=t2won,
        no_result=nr,
        t1winper=t1winper,
        t2winper=t2winper,
        msg1=msg1,
        msg2=msg2,
        m1=m1,
        m2=m2,
        or_cap1=or_cap1,
        or_cap2=or_cap2,
        pur_cap1=pur_cap1,
        pur_cap2=pur_cap2,
        nrr1=nrr1,
        nrr2=nrr2,
        d1=d1,
        d2=d2
    )


@app.route('/teamvsalllabel',methods=['POST'])
def teamvsalllabel():
    team=request.form.get('team')
    team_df=comp[comp['Team1']==team]
    try:
        l1 = str(team_df[team_df['Team2']=='Sunrisers Hyderabad']['Matches_played'].values[0])
        l2 = str(team_df[team_df['Team2'] == 'Sunrisers Hyderabad']['Team1won'].values[0])
        l3 = str(team_df[team_df['Team2'] == 'Sunrisers Hyderabad']['Team2won'].values[0])
        l4 = str(team_df[team_df['Team2'] == 'Sunrisers Hyderabad']['Team1Tro'].values[0])
        l5 = str(team_df[team_df['Team2'] == 'Sunrisers Hyderabad']['Team2Tro'].values[0])
    except IndexError:
        l1 = str(team_df[team_df['Team2'] == 'Chennai Super Kings']['Matches_played'].values[0])
        l2 = str(team_df[team_df['Team2'] == 'Chennai Super Kings']['Team1won'].values[0])
        l3 = str(team_df[team_df['Team2'] == 'Chennai Super Kings']['Team2won'].values[0])
        l4 = str(team_df[team_df['Team2'] == 'Chennai Super Kings']['Team1Tro'].values[0])
        l5 = str(team_df[team_df['Team2'] == 'Chennai Super Kings']['Team2Tro'].values[0])
    try:
        l6 = str(team_df[team_df['Team2'] == 'Delhi Capitals']['Matches_played'].values[0])
        l7 = str(team_df[team_df['Team2'] == 'Delhi Capitals']['Team1won'].values[0])
        l8 = str(team_df[team_df['Team2'] == 'Delhi Capitals']['Team2won'].values[0])
        l9 = str(team_df[team_df['Team2'] == 'Delhi Capitals']['Team1Tro'].values[0])
        l10 = str(team_df[team_df['Team2'] == 'Delhi Capitals']['Team2Tro'].values[0])
    except IndexError:
        l6 = str(team_df[team_df['Team2'] == 'Sunrisers Hyderabad']['Matches_played'].values[0])
        l7 = str(team_df[team_df['Team2'] == 'Sunrisers Hyderabad']['Team1won'].values[0])
        l8 = str(team_df[team_df['Team2'] == 'Sunrisers Hyderabad']['Team2won'].values[0])
        l9 = str(team_df[team_df['Team2'] == 'Sunrisers Hyderabad']['Team1Tro'].values[0])
        l10 = str(team_df[team_df['Team2'] == 'Sunrisers Hyderabad']['Team2Tro'].values[0])
        l1 = str(team_df[team_df['Team2'] == 'Chennai Super Kings']['Matches_played'].values[0])
        l2 = str(team_df[team_df['Team2'] == 'Chennai Super Kings']['Team1won'].values[0])
        l3 = str(team_df[team_df['Team2'] == 'Chennai Super Kings']['Team2won'].values[0])
        l4 = str(team_df[team_df['Team2'] == 'Chennai Super Kings']['Team1Tro'].values[0])
        l5 = str(team_df[team_df['Team2'] == 'Chennai Super Kings']['Team2Tro'].values[0])
    try:
        l11 = str(team_df[team_df['Team2'] == 'Gujarat Titans']['Matches_played'].values[0])
        l12 = str(team_df[team_df['Team2'] == 'Gujarat Titans']['Team1won'].values[0])
        l13 = str(team_df[team_df['Team2'] == 'Gujarat Titans']['Team2won'].values[0])
        l14 = str(team_df[team_df['Team2'] == 'Gujarat Titans']['Team1Tro'].values[0])
        l15 = str(team_df[team_df['Team2'] == 'Gujarat Titans']['Team2Tro'].values[0])
    except IndexError:
        l11 = str(team_df[team_df['Team2'] == 'Sunrisers Hyderabad']['Matches_played'].values[0])
        l12 = str(team_df[team_df['Team2'] == 'Sunrisers Hyderabad']['Team1won'].values[0])
        l13 = str(team_df[team_df['Team2'] == 'Sunrisers Hyderabad']['Team2won'].values[0])
        l14 = str(team_df[team_df['Team2'] == 'Sunrisers Hyderabad']['Team1Tro'].values[0])
        l15 = str(team_df[team_df['Team2'] == 'Sunrisers Hyderabad']['Team2Tro'].values[0])
        l1 = str(team_df[team_df['Team2'] == 'Chennai Super Kings']['Matches_played'].values[0])
        l2 = str(team_df[team_df['Team2'] == 'Chennai Super Kings']['Team1won'].values[0])
        l3 = str(team_df[team_df['Team2'] == 'Chennai Super Kings']['Team2won'].values[0])
        l4 = str(team_df[team_df['Team2'] == 'Chennai Super Kings']['Team1Tro'].values[0])
        l5 = str(team_df[team_df['Team2'] == 'Chennai Super Kings']['Team2Tro'].values[0])
    try:
        l16 = str(team_df[team_df['Team2'] == 'Kolkata Knight Riders']['Matches_played'].values[0])
        l17 = str(team_df[team_df['Team2'] == 'Kolkata Knight Riders']['Team1won'].values[0])
        l18 = str(team_df[team_df['Team2'] == 'Kolkata Knight Riders']['Team2won'].values[0])
        l19 = str(team_df[team_df['Team2'] == 'Kolkata Knight Riders']['Team1Tro'].values[0])
        l20 = str(team_df[team_df['Team2'] == 'Kolkata Knight Riders']['Team2Tro'].values[0])
    except IndexError:
        l16 = str(team_df[team_df['Team2'] == 'Sunrisers Hyderabad']['Matches_played'].values[0])
        l17 = str(team_df[team_df['Team2'] == 'Sunrisers Hyderabad']['Team1won'].values[0])
        l18 = str(team_df[team_df['Team2'] == 'Sunrisers Hyderabad']['Team2won'].values[0])
        l19 = str(team_df[team_df['Team2'] == 'Sunrisers Hyderabad']['Team1Tro'].values[0])
        l20 = str(team_df[team_df['Team2'] == 'Sunrisers Hyderabad']['Team2Tro'].values[0])
        l1 = str(team_df[team_df['Team2'] == 'Chennai Super Kings']['Matches_played'].values[0])
        l2 = str(team_df[team_df['Team2'] == 'Chennai Super Kings']['Team1won'].values[0])
        l3 = str(team_df[team_df['Team2'] == 'Chennai Super Kings']['Team2won'].values[0])
        l4 = str(team_df[team_df['Team2'] == 'Chennai Super Kings']['Team1Tro'].values[0])
        l5 = str(team_df[team_df['Team2'] == 'Chennai Super Kings']['Team2Tro'].values[0])
    try:
        l21 = str(team_df[team_df['Team2'] == 'Lucknow Super Giants']['Matches_played'].values[0])
        l22 = str(team_df[team_df['Team2'] == 'Lucknow Super Giants']['Team1won'].values[0])
        l23 = str(team_df[team_df['Team2'] == 'Lucknow Super Giants']['Team2won'].values[0])
        l24 = str(team_df[team_df['Team2'] == 'Lucknow Super Giants']['Team1Tro'].values[0])
        l25 = str(team_df[team_df['Team2'] == 'Lucknow Super Giants']['Team2Tro'].values[0])
    except IndexError:
        l21 = str(team_df[team_df['Team2'] == 'Sunrisers Hyderabad']['Matches_played'].values[0])
        l22 = str(team_df[team_df['Team2'] == 'Sunrisers Hyderabad']['Team1won'].values[0])
        l23 = str(team_df[team_df['Team2'] == 'Sunrisers Hyderabad']['Team2won'].values[0])
        l24 = str(team_df[team_df['Team2'] == 'Sunrisers Hyderabad']['Team1Tro'].values[0])
        l25 = str(team_df[team_df['Team2'] == 'Sunrisers Hyderabad']['Team2Tro'].values[0])
        l1 = str(team_df[team_df['Team2'] == 'Chennai Super Kings']['Matches_played'].values[0])
        l2 = str(team_df[team_df['Team2'] == 'Chennai Super Kings']['Team1won'].values[0])
        l3 = str(team_df[team_df['Team2'] == 'Chennai Super Kings']['Team2won'].values[0])
        l4 = str(team_df[team_df['Team2'] == 'Chennai Super Kings']['Team1Tro'].values[0])
        l5 = str(team_df[team_df['Team2'] == 'Chennai Super Kings']['Team2Tro'].values[0])
    try:
        l26 = str(team_df[team_df['Team2'] == 'Mumbai Indians']['Matches_played'].values[0])
        l27 = str(team_df[team_df['Team2'] == 'Mumbai Indians']['Team1won'].values[0])
        l28 = str(team_df[team_df['Team2'] == 'Mumbai Indians']['Team2won'].values[0])
        l29 = str(team_df[team_df['Team2'] == 'Mumbai Indians']['Team1Tro'].values[0])
        l30 = str(team_df[team_df['Team2'] == 'Mumbai Indians']['Team2Tro'].values[0])
    except IndexError:
        l26 = str(team_df[team_df['Team2'] == 'Sunrisers Hyderabad']['Matches_played'].values[0])
        l27 = str(team_df[team_df['Team2'] == 'Sunrisers Hyderabad']['Team1won'].values[0])
        l28 = str(team_df[team_df['Team2'] == 'Sunrisers Hyderabad']['Team2won'].values[0])
        l29 = str(team_df[team_df['Team2'] == 'Sunrisers Hyderabad']['Team1Tro'].values[0])
        l30 = str(team_df[team_df['Team2'] == 'Sunrisers Hyderabad']['Team2Tro'].values[0])
        l1 = str(team_df[team_df['Team2'] == 'Chennai Super Kings']['Matches_played'].values[0])
        l2 = str(team_df[team_df['Team2'] == 'Chennai Super Kings']['Team1won'].values[0])
        l3 = str(team_df[team_df['Team2'] == 'Chennai Super Kings']['Team2won'].values[0])
        l4 = str(team_df[team_df['Team2'] == 'Chennai Super Kings']['Team1Tro'].values[0])
        l5 = str(team_df[team_df['Team2'] == 'Chennai Super Kings']['Team2Tro'].values[0])
    try:
        l31 = str(team_df[team_df['Team2'] == 'Punjab Kings']['Matches_played'].values[0])
        l32 = str(team_df[team_df['Team2'] == 'Punjab Kings']['Team1won'].values[0])
        l33 = str(team_df[team_df['Team2'] == 'Punjab Kings']['Team2won'].values[0])
        l34 = str(team_df[team_df['Team2'] == 'Punjab Kings']['Team1Tro'].values[0])
        l35 = str(team_df[team_df['Team2'] == 'Punjab Kings']['Team2Tro'].values[0])
    except IndexError:
        l31 = str(team_df[team_df['Team2'] == 'Sunrisers Hyderabad']['Matches_played'].values[0])
        l32 = str(team_df[team_df['Team2'] == 'Sunrisers Hyderabad']['Team1won'].values[0])
        l33 = str(team_df[team_df['Team2'] == 'Sunrisers Hyderabad']['Team2won'].values[0])
        l34 = str(team_df[team_df['Team2'] == 'Sunrisers Hyderabad']['Team1Tro'].values[0])
        l35 = str(team_df[team_df['Team2'] == 'Sunrisers Hyderabad']['Team2Tro'].values[0])
        l1 = str(team_df[team_df['Team2'] == 'Chennai Super Kings']['Matches_played'].values[0])
        l2 = str(team_df[team_df['Team2'] == 'Chennai Super Kings']['Team1won'].values[0])
        l3 = str(team_df[team_df['Team2'] == 'Chennai Super Kings']['Team2won'].values[0])
        l4 = str(team_df[team_df['Team2'] == 'Chennai Super Kings']['Team1Tro'].values[0])
        l5 = str(team_df[team_df['Team2'] == 'Chennai Super Kings']['Team2Tro'].values[0])

    try:
        l36 = str(team_df[team_df['Team2'] == 'Royal Challengers Bangalore']['Matches_played'].values[0])
        l37 = str(team_df[team_df['Team2'] == 'Royal Challengers Bangalore']['Team1won'].values[0])
        l38 = str(team_df[team_df['Team2'] == 'Royal Challengers Bangalore']['Team2won'].values[0])
        l39 = str(team_df[team_df['Team2'] == 'Royal Challengers Bangalore']['Team1Tro'].values[0])
        l40 = str(team_df[team_df['Team2'] == 'Royal Challengers Bangalore']['Team2Tro'].values[0])
    except IndexError:
        l36 = str(team_df[team_df['Team2'] == 'Sunrisers Hyderabad']['Matches_played'].values[0])
        l37 = str(team_df[team_df['Team2'] == 'Sunrisers Hyderabad']['Team1won'].values[0])
        l38 = str(team_df[team_df['Team2'] == 'Sunrisers Hyderabad']['Team2won'].values[0])
        l39 = str(team_df[team_df['Team2'] == 'Sunrisers Hyderabad']['Team1Tro'].values[0])
        l40 = str(team_df[team_df['Team2'] == 'Sunrisers Hyderabad']['Team2Tro'].values[0])
        l1 = str(team_df[team_df['Team2'] == 'Chennai Super Kings']['Matches_played'].values[0])
        l2 = str(team_df[team_df['Team2'] == 'Chennai Super Kings']['Team1won'].values[0])
        l3 = str(team_df[team_df['Team2'] == 'Chennai Super Kings']['Team2won'].values[0])
        l4 = str(team_df[team_df['Team2'] == 'Chennai Super Kings']['Team1Tro'].values[0])
        l5 = str(team_df[team_df['Team2'] == 'Chennai Super Kings']['Team2Tro'].values[0])
    try:
        l41 = str(team_df[team_df['Team2'] == 'Rajasthan Royals']['Matches_played'].values[0])
        l42 = str(team_df[team_df['Team2'] == 'Rajasthan Royals']['Team1won'].values[0])
        l43 = str(team_df[team_df['Team2'] == 'Rajasthan Royals']['Team2won'].values[0])
        l44 = str(team_df[team_df['Team2'] == 'Rajasthan Royals']['Team1Tro'].values[0])
        l45 = str(team_df[team_df['Team2'] == 'Rajasthan Royals']['Team2Tro'].values[0])
    except IndexError:
        l41 = str(team_df[team_df['Team2'] == 'Sunrisers Hyderabad']['Matches_played'].values[0])
        l42 = str(team_df[team_df['Team2'] == 'Sunrisers Hyderabad']['Team1won'].values[0])
        l43 = str(team_df[team_df['Team2'] == 'Sunrisers Hyderabad']['Team2won'].values[0])
        l44 = str(team_df[team_df['Team2'] == 'Sunrisers Hyderabad']['Team1Tro'].values[0])
        l45 = str(team_df[team_df['Team2'] == 'Sunrisers Hyderabad']['Team2Tro'].values[0])
        l1 = str(team_df[team_df['Team2'] == 'Chennai Super Kings']['Matches_played'].values[0])
        l2 = str(team_df[team_df['Team2'] == 'Chennai Super Kings']['Team1won'].values[0])
        l3 = str(team_df[team_df['Team2'] == 'Chennai Super Kings']['Team2won'].values[0])
        l4 = str(team_df[team_df['Team2'] == 'Chennai Super Kings']['Team1Tro'].values[0])
        l5 = str(team_df[team_df['Team2'] == 'Chennai Super Kings']['Team2Tro'].values[0])

    try:
        l46 = str(team_df[team_df['Team2'] == 'Chennai Super Kings']['Matches_played'].values[0])
        l47 = str(team_df[team_df['Team2'] == 'Chennai Super Kings']['Team1won'].values[0])
        l48 = str(team_df[team_df['Team2'] == 'Chennai Super Kings']['Team2won'].values[0])
        l49 = str(team_df[team_df['Team2'] == 'Chennai Super Kings']['Team1Tro'].values[0])
        l50 = str(team_df[team_df['Team2'] == 'Chennai Super Kings']['Team2Tro'].values[0])
    except IndexError:
        pass


    return jsonify(l1=l1,l2=l2,l3=l3,l4=l4,l5=l5,l6=l6,l7=l7,l8=l8,l9=l9,l10=l10,l11=l11,l12=l12,l13=l13,l14=l14,l15=l15,l16=l16,l17=l17,l18=l18,l19=l19,l20=l20,l21=l21,l22=l22,l23=l23,l24=l24,l25=l25,l26=l26,l27=l27,l28=l28,l29=l29,l30=l30,l31=l31,l32=l32,l33=l33,l34=l34,l35=l35,l36=l36,l37=l37,l38=l38,l39=l39,l40=l40,l41=l41,l42=l42,l43=l43,l44=l44,l45=l45)


'''

@app.route('/teamvsalllabel', methods=['POST'])
def teamvsalllabel():
    team = (request.form.get('team') or '').strip()

    if not team or team == 'Select Team':
        return jsonify(error="Please select a team"), 400

    team_df = comp[comp['Team1'] == team].copy()

    # Helper: safely fetch a single value (as string) from team_df for a given opponent + column
    def get_val(opponent: str, col: str, default: str = "0") -> str:
        s = team_df.loc[team_df['Team2'] == opponent, col]
        return str(s.values[0]) if len(s) else str(default)

    # Order MUST match the IDs your frontend expects (your current code expects 9 opponents = 45 values)
    opponents = [
        "Sunrisers Hyderabad",          # l1-l5
        "Delhi Capitals",               # l6-l10
        "Gujarat Titans",               # l11-l15
        "Kolkata Knight Riders",        # l16-l20
        "Lucknow Super Giants",         # l21-l25
        "Mumbai Indians",               # l26-l30
        "Punjab Kings",                 # l31-l35
        "Royal Challengers Bangalore",  # l36-l40
        "Rajasthan Royals",             # l41-l45
    ]

    cols = ["Matches_played", "Team1won", "Team2won", "Team1Tro", "Team2Tro"]

    # Build l1..l45
    out = {}
    idx = 1
    for opp in opponents:
        for col in cols:
            out[f"l{idx}"] = get_val(opp, col, default="0")
            idx += 1

    # IMPORTANT:
    # Your old code had l46..l50 but you never returned them.
    # If your HTML/JS expects Chennai Super Kings too, either:
    #  (A) add it to the opponents list AND update your template IDs to include a 10th row, OR
    #  (B) keep returning l46..l50 as extras (below).
    #
    # If you want to also return CSK as l46..l50 (optional, harmless if unused):
    out["l46"] = get_val("Chennai Super Kings", "Matches_played", default="0")
    out["l47"] = get_val("Chennai Super Kings", "Team1won", default="0")
    out["l48"] = get_val("Chennai Super Kings", "Team2won", default="0")
    out["l49"] = get_val("Chennai Super Kings", "Team1Tro", default="0")
    out["l50"] = get_val("Chennai Super Kings", "Team2Tro", default="0")

    return jsonify(**out)
'''

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 4000)))

