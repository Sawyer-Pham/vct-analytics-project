import sqlite3
import pandas as pd

conn = sqlite3.connect("vlr.db")

matches = pd.read_sql_query(
    "SELECT * FROM matches ORDER BY match_date",
    conn
)

matches["match_date"] = pd.to_datetime(matches["match_date"])
matches = matches.sort_values("match_date").reset_index(drop=True)

features = []

for index, current_match in matches.iterrows():

    previous_matches = matches[
        matches["match_date"] < current_match["match_date"]
    ]

    team_a_id = current_match["team_a_id"]
    team_b_id = current_match["team_b_id"]

    #team a

    team_a_matches = previous_matches[
        (previous_matches["team_a_id"] == team_a_id) |
        (previous_matches["team_b_id"] == team_a_id)
    ]

    team_a_win_rate = (
        (team_a_matches["winner_id"] == team_a_id).mean()
        if len(team_a_matches) > 0
        else 0.5
    )

    team_a_recent = team_a_matches.tail(5)

    team_a_recent_win_rate = (
        (team_a_recent["winner_id"] == team_a_id).mean()
        if len(team_a_recent) > 0
        else 0.5
    )

    team_a_matches_played = len(team_a_matches)


  
    # team b


    team_b_matches = previous_matches[
        (previous_matches["team_a_id"] == team_b_id) |
        (previous_matches["team_b_id"] == team_b_id)
    ]

    team_b_win_rate = (
        (team_b_matches["winner_id"] == team_b_id).mean()
        if len(team_b_matches) > 0
        else 0.5
    )

    team_b_recent = team_b_matches.tail(5)

    team_b_recent_win_rate = (
        (team_b_recent["winner_id"] == team_b_id).mean()
        if len(team_b_recent) > 0
        else 0.5
    )

    team_b_matches_played = len(team_b_matches)


   
    # Head to head data
   

    head_to_head = previous_matches[
        (
            (previous_matches["team_a_id"] == team_a_id) &
            (previous_matches["team_b_id"] == team_b_id)
        )
        |
        (
            (previous_matches["team_a_id"] == team_b_id) &
            (previous_matches["team_b_id"] == team_a_id)
        )
    ]

    h2h_a_win_rate = (
        (head_to_head["winner_id"] == team_a_id).mean()
        if len(head_to_head) > 0
        else 0.5
    )


    row = {
        
            "match_id": current_match["match_id"],
            "team_a_id": team_a_id,
            "team_b_id": team_b_id,

            "team_a_win_rate": team_a_win_rate,
            "team_b_win_rate": team_b_win_rate,

            "team_a_recent_win_rate": team_a_recent_win_rate,
            "team_b_recent_win_rate": team_b_recent_win_rate,

            "team_a_matches_played": team_a_matches_played,
            "team_b_matches_played": team_b_matches_played,

            "h2h_a_win_rate": h2h_a_win_rate,

            "win_rate_diff": team_a_win_rate - team_b_win_rate,

            "recent_win_rate_diff": team_a_recent_win_rate - team_b_recent_win_rate,

            "team_a_won":   1 if current_match["winner_id"] == team_a_id else 0
            
    }

    features.append(row)

feature_df = pd.DataFrame(features)

print(feature_df.head())
print(feature_df.shape)
print(feature_df.isnull().sum())

feature_df.to_csv("features.csv", index=False)

conn.close()