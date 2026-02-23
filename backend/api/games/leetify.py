import requests
from typing import Dict, Any, Optional, List


class LeetifyAPI:
    """Leetify Public CS API integration for Counter-Strike 2."""

    BASE_URL = "https://api-public.cs-prod.leetify.com"

    def __init__(self, api_key: str, steam_id: str):
        self.api_key = api_key
        self.steam_id = steam_id
        self.headers = {"Authorization": f"Bearer {api_key}"}

    def get_profile(self) -> Optional[Dict[str, Any]]:
        """Fetch player profile from Leetify (ratings, ranks, overall stats)."""
        try:
            r = requests.get(
                f"{self.BASE_URL}/v3/profile",
                params={"steam64_id": self.steam_id},
                headers=self.headers,
                timeout=15,
            )
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            print(f"[LeetifyAPI] Error fetching profile: {e}")
            return None

    def get_match_history(self) -> Optional[List[Dict[str, Any]]]:
        """Fetch last 100 matches with detailed per-player stats."""
        try:
            r = requests.get(
                f"{self.BASE_URL}/v3/profile/matches",
                params={"steam64_id": self.steam_id},
                headers=self.headers,
                timeout=15,
            )
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            print(f"[LeetifyAPI] Error fetching match history: {e}")
            return None

    def get_match_detail(self, game_id: str) -> Optional[Dict[str, Any]]:
        """Fetch detailed match data by game ID."""
        try:
            r = requests.get(
                f"{self.BASE_URL}/v2/matches/{game_id}",
                headers=self.headers,
                timeout=15,
            )
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            print(f"[LeetifyAPI] Error fetching match {game_id}: {e}")
            return None

    def parse_profile(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse profile response into a flat dict for storage/display."""
        if not data:
            return {}

        ranks = data.get("ranks") or {}
        rating = data.get("rating") or {}
        stats = data.get("stats") or {}

        return {
            "name": data.get("name"),
            "steam64_id": data.get("steam64_id"),
            "leetify_id": data.get("id"),
            "winrate": data.get("winrate"),
            "total_matches": data.get("total_matches"),
            "first_match_date": data.get("first_match_date"),
            # Ranks
            "leetify_rating": ranks.get("leetify"),
            "premier_rank": ranks.get("premier"),
            "faceit_level": ranks.get("faceit"),
            "faceit_elo": ranks.get("faceit_elo"),
            "wingman_rank": ranks.get("wingman"),
            "competitive_ranks": ranks.get("competitive", []),
            # Leetify skill ratings
            "aim_rating": rating.get("aim"),
            "positioning_rating": rating.get("positioning"),
            "utility_rating": rating.get("utility"),
            "clutch_rating": rating.get("clutch"),
            "opening_rating": rating.get("opening"),
            "ct_leetify": rating.get("ct_leetify"),
            "t_leetify": rating.get("t_leetify"),
            # Overall averages
            "accuracy_head": stats.get("accuracy_head"),
            "accuracy_enemy_spotted": stats.get("accuracy_enemy_spotted"),
            "spray_accuracy": stats.get("spray_accuracy"),
            "reaction_time_ms": stats.get("reaction_time_ms"),
            "preaim": stats.get("preaim"),
            "counter_strafing": stats.get("counter_strafing_good_shots_ratio"),
            "flashbang_thrown": stats.get("flashbang_thrown"),
            "flashbang_leading_to_kill": stats.get("flashbang_leading_to_kill"),
            "trade_kills_pct": stats.get("trade_kills_success_percentage"),
            "opening_duel_ct": stats.get("ct_opening_duel_success_percentage"),
            "opening_duel_t": stats.get("t_opening_duel_success_percentage"),
        }

    def parse_match(self, match_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse a match from the history endpoint, extracting our player's stats."""
        if not match_data:
            return None

        # Find our stats in the match
        stats_list = match_data.get("stats", [])
        our_stats = None
        for s in stats_list:
            if s.get("steam64_id") == self.steam_id:
                our_stats = s
                break

        if not our_stats:
            return None

        # Determine score
        team_scores = match_data.get("team_scores", [])
        our_team = our_stats.get("initial_team_number")
        score_us = 0
        score_them = 0
        for ts in team_scores:
            if ts.get("team_number") == our_team:
                score_us = ts.get("score", 0)
            else:
                score_them = ts.get("score", 0)

        kills = our_stats.get("total_kills", 0)
        deaths = max(our_stats.get("total_deaths", 0), 1)
        hs_kills = our_stats.get("total_hs_kills", 0)
        rounds = max(our_stats.get("rounds_count", 1), 1)

        return {
            "game_id": match_data.get("id"),
            "finished_at": match_data.get("finished_at"),
            "data_source": match_data.get("data_source"),
            "map_name": match_data.get("map_name"),
            "outcome": match_data.get("outcome") if "outcome" in match_data else (
                "win" if score_us > score_them else "loss" if score_us < score_them else "tie"
            ),
            "score_us": score_us,
            "score_them": score_them,
            "rank": our_stats.get("rank") if "rank" in match_data else None,
            "has_banned_player": match_data.get("has_banned_player", False),
            # Core stats
            "kills": kills,
            "deaths": our_stats.get("total_deaths", 0),
            "assists": our_stats.get("total_assists", 0),
            "kd_ratio": our_stats.get("kd_ratio", round(kills / deaths, 2)),
            "adr": our_stats.get("dpr", 0),
            "hs_kills": hs_kills,
            "hs_pct": round((hs_kills / max(kills, 1)) * 100, 1),
            "mvps": our_stats.get("mvps", 0),
            "total_damage": our_stats.get("total_damage", 0),
            # Leetify ratings
            "leetify_rating": our_stats.get("leetify_rating"),
            "ct_leetify_rating": our_stats.get("ct_leetify_rating"),
            "t_leetify_rating": our_stats.get("t_leetify_rating"),
            # Accuracy
            "accuracy": our_stats.get("accuracy"),
            "accuracy_head": our_stats.get("accuracy_head"),
            "accuracy_enemy_spotted": our_stats.get("accuracy_enemy_spotted"),
            "spray_accuracy": our_stats.get("spray_accuracy"),
            # Positioning
            "preaim": our_stats.get("preaim"),
            "reaction_time": our_stats.get("reaction_time"),
            # Rounds
            "rounds_count": our_stats.get("rounds_count", 0),
            "rounds_won": our_stats.get("rounds_won", 0),
            # Multi-kills
            "multi1k": our_stats.get("multi1k", 0),
            "multi2k": our_stats.get("multi2k", 0),
            "multi3k": our_stats.get("multi3k", 0),
            "multi4k": our_stats.get("multi4k", 0),
            "multi5k": our_stats.get("multi5k", 0),
            # Utility
            "flashbang_thrown": our_stats.get("flashbang_thrown", 0),
            "he_thrown": our_stats.get("he_thrown", 0),
            "smoke_thrown": our_stats.get("smoke_thrown", 0),
            "molotov_thrown": our_stats.get("molotov_thrown", 0),
            # Trade
            "trade_kills_pct": our_stats.get("trade_kills_success_percentage"),
            "traded_deaths_pct": our_stats.get("traded_deaths_success_percentage"),
        }
