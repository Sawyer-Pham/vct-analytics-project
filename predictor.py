"""Train the matchup model and construct features from stored match history."""

from pathlib import Path
import sqlite3

import pandas as pd
from sklearn.linear_model import LogisticRegression


FEATURE_COLUMNS = [
    "avg_acs_diff", "recent_acs_diff", "h2h_a_win_rate",
    "win_rate_diff", "recent_win_rate_diff",
]
PROJECT_PATH = Path(__file__).resolve().parent


class MatchPredictor:
    def __init__(self, database_path=PROJECT_PATH / "vlr.db",
                 features_path=PROJECT_PATH / "features.csv"):
        self.database_path = database_path
        training = pd.read_csv(features_path)
        if training.empty or training["team_a_won"].nunique() < 2:
            raise ValueError("Training data must include wins for both sides.")
        # Fit all available historical examples for future matchup predictions.
        # train_model.py retains its chronological holdout for evaluation.
        self.model = LogisticRegression(max_iter=1000)
        self.model.fit(training[FEATURE_COLUMNS], training["team_a_won"])

    def predict(self, team_a_id, team_b_id):
        if team_a_id == team_b_id:
            raise ValueError("Choose two different teams.")
        with sqlite3.connect(self.database_path.as_uri() + "?mode=ro", uri=True) as conn:
            matches = pd.read_sql_query(
                "SELECT match_id, team_a_id, team_b_id, winner_id FROM matches "
                "WHERE winner_id IN (team_a_id, team_b_id) "
                "ORDER BY julianday(match_date), match_id", conn,
            )
            stats = []
            for team_id in (team_a_id, team_b_id):
                history = matches[
                    (matches.team_a_id == team_id) | (matches.team_b_id == team_id)
                ]
                if history.empty:
                    raise ValueError("One of the selected teams has no completed matches in the dataset.")
                match_ids = history.match_id.tolist()
                def average_acs(ids):
                    placeholders = ",".join("?" for _ in ids)
                    return conn.execute(
                        f"SELECT COALESCE(AVG(acs), 0) FROM player_map_stats "
                        f"WHERE team_id = ? AND match_id IN ({placeholders})",
                        [int(team_id)] + [int(value) for value in ids],
                    ).fetchone()[0]
                stats.append({
                    "win_rate": (history.winner_id == team_id).mean(),
                    "recent_win_rate": (history.tail(5).winner_id == team_id).mean(),
                    "avg_acs": average_acs(match_ids),
                    "recent_acs": average_acs(match_ids[-5:]),
                })
            h2h = matches[
                ((matches.team_a_id == team_a_id) & (matches.team_b_id == team_b_id))
                | ((matches.team_a_id == team_b_id) & (matches.team_b_id == team_a_id))
            ]
        a, b = stats
        features = {
            "avg_acs_diff": a["avg_acs"] - b["avg_acs"],
            "recent_acs_diff": a["recent_acs"] - b["recent_acs"],
            "h2h_a_win_rate": (h2h.winner_id == team_a_id).mean() if len(h2h) else 0.5,
            "win_rate_diff": a["win_rate"] - b["win_rate"],
            "recent_win_rate_diff": a["recent_win_rate"] - b["recent_win_rate"],
        }
        probabilities = self.model.predict_proba(pd.DataFrame([features], columns=FEATURE_COLUMNS))[0]
        return float(probabilities[list(self.model.classes_).index(1)])
