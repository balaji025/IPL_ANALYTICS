"""
API tests against the real data/ipl.sqlite. Expected values are official IPL
figures, so a bad rebuild shows up here.

    python -m unittest discover tests
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app  # noqa: E402

KOHLI = None


class ApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        global KOHLI
        cls.c = app.test_client()
        KOHLI = cls.c.get("/api/players?q=Virat Kohli").get_json()[0]["player_id"]

    def get(self, url, status=200):
        r = self.c.get(url)
        self.assertEqual(r.status_code, status, f"{url}: {r.get_data(as_text=True)[:200]}")
        return r.get_json()

    def test_index_lists_endpoints(self):
        d = self.get("/api")
        self.assertEqual(d["meta"]["last_season"], "2026")
        self.assertIn("/api/players/<pid>", d["endpoints"])

    def test_seasons(self):
        s = {x["season"]: x for x in self.get("/api/seasons")}
        self.assertEqual(len(s), 19)
        self.assertEqual(s[2024]["champion"], "Kolkata Knight Riders")
        self.assertEqual(s[2026]["champion"], "Royal Challengers Bengaluru")
        self.assertEqual((s[2016]["orange_cap"], s[2016]["orange_cap_runs"]), ("Virat Kohli", 973))
        self.assertEqual(s[2026]["purple_cap"], "Kagiso Rabada")

    def test_season_points_table(self):
        d = self.get("/api/seasons/2024")
        top = d["points_table"][0]
        self.assertEqual((top["short"], top["points"], top["nrr"]), ("KKR", 20, 1.428))
        self.assertEqual(len(d["points_table"]), 10)
        self.assertEqual(d["playoffs"][-1]["stage"], "Final")
        self.get("/api/seasons/1999", 404)

    def test_player_profile(self):
        d = self.get(f"/api/players/{KOHLI}")
        self.assertEqual(d["player"]["name"], "Virat Kohli")
        self.assertEqual(d["batting"]["runs"], 9336)
        self.assertEqual(d["batting"]["high_score"], "113*")
        season_2016 = next(s for s in d["seasons"] if s["season"] == 2016)
        self.assertEqual(season_2016["batting"]["runs"], 973)
        self.assertEqual({p["phase"] for p in d["phases"]["batting"]}, {"powerplay", "middle", "death"})
        self.assertEqual(len(d["recent_matches"]), 10)
        self.get("/api/players/nope", 404)

    def test_player_search_and_matchups(self):
        res = self.get("/api/players?q=Sooryavanshi")
        self.assertEqual(res[0]["name"], "Vaibhav Sooryavanshi")
        m = self.get(f"/api/players/{KOHLI}/matchups?limit=5")
        self.assertEqual(len(m["as_batter"]), 5)

    def test_player_vs_player(self):
        bumrah = self.get("/api/players?q=Jasprit Bumrah")[0]["player_id"]
        d = self.get(f"/api/players/{KOHLI}/vs/{bumrah}")
        self.assertGreater(d["a_batting_vs_b"]["balls"], 0)
        self.assertEqual(d["b"]["player"]["name"], "Jasprit Bumrah")

    def test_teams(self):
        t = {x["short"]: x for x in self.get("/api/teams")}
        self.assertEqual(t["CSK"]["titles"], [2010, 2011, 2018, 2021, 2023])
        self.assertEqual(t["MI"]["titles"], [2013, 2015, 2017, 2019, 2020])
        d = self.get("/api/teams/rcb")
        self.assertEqual(d["titles"], [2025, 2026])
        self.assertEqual(d["lowest_totals"][0]["runs"], 49)
        self.get("/api/teams/XYZ", 404)

    def test_team_vs(self):
        d = self.get("/api/teams/CSK/vs/MI")
        self.assertEqual(d["played"], len(d["matches"]))
        self.assertEqual(sum(d["wins"].values()) + d["no_result"], d["played"])
        self.get("/api/teams/CSK/vs/CSK", 400)
        va = self.get("/api/teams/GT/vs-all")
        self.assertTrue(all(o["played"] > 0 for o in va["opponents"]))

    def test_match_scorecard(self):
        final = self.get("/api/matches?season=2026&limit=1")[0]
        self.assertEqual(final["stage"], "Final")
        d = self.get(f"/api/matches/{final['match_id']}")
        self.assertEqual(d["match"]["winner"], "Royal Challengers Bengaluru")
        first = d["innings"][0]
        self.assertEqual(sum(b["runs"] for b in first["batting"]) + first["extras"], first["runs"])
        self.assertTrue(all(b["dismissal"] for b in first["batting"]))
        self.get("/api/matches/1", 404)

    def test_records(self):
        d = self.get("/api/records")
        self.assertEqual(d["highest_totals"][0]["score"], "287/3")
        self.assertEqual((d["highest_scores"][0]["name"], d["highest_scores"][0]["runs"]), ("Chris Gayle", 175))
        self.assertEqual(d["best_bowling"][0]["name"], "Alzarri Joseph")
        s = self.get("/api/records?season=2016")
        self.assertEqual(s["most_runs"][0]["runs"], 973)

    def test_pages(self):
        final = self.c.get("/api/matches?season=2026&limit=1").get_json()[0]["match_id"]
        for url in ["/", "/teams", "/teams/CSK", "/teams/DCH", "/teams/CSK/vs/MI", "/seasons/2024",
                    f"/matches/{final}", "/records", "/compare", f"/players/{KOHLI}"]:
            r = self.c.get(url)
            self.assertEqual(r.status_code, 200, url)
            self.assertIn(b"IPL", r.data, url)
        for url in ["/players/nope", "/teams/XYZ", "/seasons/1999", "/matches/1"]:
            r = self.c.get(url)
            self.assertEqual(r.status_code, 404, url)
            self.assertIn(b"Nothing here", r.data, url)


if __name__ == "__main__":
    unittest.main()
