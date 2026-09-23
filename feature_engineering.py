import sqlite3
import pandas as pd

conn = sqlite3.connect("vlr.db")

matches = pd.read_sql_query(
    "SELECT * FROM matches ORDER BY match_date",
    conn
)

matches["match_date"] = pd.to_datetime(matches["match_date"])
matches = matches.sort_values("match_date").reset_index(drop=True)
#helper functions for getting acs
def get_team_avg_acs(conn, team_id, current_match_date):
    cursor = conn.cursor()

    cursor.execute("""
        SELECT AVG(pms.acs)
        FROM Player_map_stats pms
        JOIN Matches m
            ON pms.match_id = m.match_id
        WHERE pms.team_id = ?
        AND m.match_date < ?
    """, (team_id, current_match_date.isoformat()))

    result = cursor.fetchone()

    if result[0] is None:
        return 0

    return result[0]

def get_recent_acs(conn, team_id, current_match_date):
    cursor = conn.cursor()
     
    cursor.execute("""
        SELECT match_id
        FROM Matches
        WHERE (team_a_id = ? OR team_b_id = ?)
        AND match_date < ?
        ORDER BY match_date DESC
        LIMIT 5
    """, (team_id, team_id, current_match_date.isoformat()))

    recent_matches = cursor.fetchall()

    if len(recent_matches) == 0:
        return 0

    match_ids = []

    for match in recent_matches:
        match_ids.append(match[0])

    placeholders = ",".join(["?"] * len(match_ids))

    cursor.execute(f"""
        SELECT AVG(acs)
        FROM player_map_stats pms
        WHERE team_id = ?
        AND pms.match_id IN ({placeholders})
        """,  [team_id] + match_ids)

    result = cursor.fetchone()
    
    if result[0] is None:
        return 0
    
    return result[0]


#### Features
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

    
    team_a_avg_acs = (
        get_team_avg_acs(conn, team_a_id, current_match["match_date"])
    )

    team_a_recent_acs = (
        get_recent_acs(conn,team_a_id, current_match["match_date"])
    )
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

    team_b_avg_acs = (
        get_team_avg_acs(conn, team_b_id, current_match["match_date"])
                      )

    team_b_recent_acs = (
            get_recent_acs(conn,team_b_id, current_match["match_date"])
        )

   
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

            "team_a_avg_acs": team_a_avg_acs,
            "team_b_avg_acs": team_b_avg_acs,
            "avg_acs_diff": team_a_avg_acs - team_b_avg_acs,

            "team_a_recent_acs": team_a_recent_acs,
            "team_b_recent_acs": team_b_recent_acs,
            "recent_acs_diff": team_a_recent_acs - team_b_recent_acs,
            
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