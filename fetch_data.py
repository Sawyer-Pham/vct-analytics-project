import vlrdevapi as vlr
import pandas as pd
import numpy as np
import sqlite3
import requests

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from vlrdevapi import VLRClient

client = VLRClient()

import plotly.express as px
import joblib

conn = sqlite3.connect("vlr.db")

cursor = conn.cursor()

cursor.execute("""
    CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_veto
    ON map_vetoes(match_id, veto_order)
""")

vct_event_ids = [
   
    2977,
    2776,
    2976,
    2978

]

completed_matches = []
#Grabbing data for teams table
for event_id in vct_event_ids:
    event_matches = vlr.event.matches(event_id=event_id)
    for m in event_matches.matches:
        

        if m.status.value == "completed":

            region = ""
            

            if event_id == 2977:
                region = "AMERICAS"
            elif event_id == 2776:
                region = "PACIFIC"
            elif event_id == 2976:
                region = "EMEA"
            elif event_id == 2978:
                region = "CHINA"
            for team in m.teams:

                cursor.execute(
                    """
                    INSERT OR IGNORE INTO teams (team_id, team_name, region)
                    VALUES (?, ?, ?)
                    """,
                    (team.id, team.name.upper(), region)
                )

           


#Grabbing data for players table
for event_id in vct_event_ids:
    event_teams = vlr.event.teams(event_id=event_id)
    for stage in event_teams.stages:
        for team in stage.teams:

            for player in team.players:


                cursor.execute(
                    """
                    INSERT OR IGNORE INTO players (plr_id, plr_name, team_id)
                    VALUES(?,?,?)
                    """,
                    (player.id,player.name,team.id)
                )


#Grabbing data for Player Map stats

for event_id in vct_event_ids:

    event_matches = vlr.event.matches(
        event_id=event_id,
        state="completed"
    )

    for m in event_matches.matches:

        match_id = m.match_id

        series_info = vlr.series.info(
            series_id=match_id
        )

        
        for game in series_info.games:

            if not game.played:
                continue

            map_number = game.order

            stats = vlr.series.players(
                series_id=match_id,
                game_id=map_number
            )

            for team in [stats.team1, stats.team2]:

                for player in team.players:

                    s = player.stats.overall

                    agent_name = player.agents[0] if player.agents else None

                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO player_map_stats
                        (
                            player_id,
                            match_id,
                            map_number,
                            team_id,
                            agent_name,
                            kills,
                            deaths,
                            assists,
                            acs,
                            adr,
                            kast,
                            first_kills,
                            first_deaths
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            player.player_id,
                            match_id,
                            map_number,
                            team.team_id,
                            agent_name,
                            s.kills,
                            s.deaths,
                            s.assists,
                            s.acs,
                            s.adr,
                            s.kast,
                            s.first_kills,
                            s.first_deaths
                        )
                    )
#Match and map veto data
for event_id in vct_event_ids:
    event_matches = vlr.event.matches(
        event_id=event_id,
        state="completed"
    )

    for m in event_matches.matches:

        match_id = m.match_id

        series_info = vlr.series.info(
            series_id=match_id
        )

        team_a = m.teams[0]
        team_b = m.teams[1]
        winner_id = 0
        loser_id = 0
        if team_a.winner:
            winner_id = team_a.id
            loser_id = team_b.id
        else:
            winner_id = team_b.id
            loser_id = team_a.id
        
        #matches
        cursor.execute(
            """
            INSERT OR IGNORE INTO matches(match_id, match_date, team_a_id, team_b_id, winner_id, team_a_maps_won, team_b_maps_won, best_of, loser_id)
            values(?,?,?,?,?,?,?,?,?)
            """,
            (match_id, series_info.datetime.isoformat(), team_a.id,team_b.id, winner_id, series_info.score1, series_info.score2, series_info.best_of, loser_id)


        )
        #vetoes 

        veto_order = 0
        for s in series_info.veto:
            veto_order += 1

            if s.team == series_info.team1.tag:
                veto_team_id = series_info.team1.id
            elif s.team == series_info.team2.tag:
                veto_team_id = series_info.team2.id
            else:
                veto_team_id = None

            cursor.execute(
                """
                INSERT OR IGNORE INTO map_vetoes
                (match_id, veto_order, team_id, map_name, action)
                VALUES (?, ?, ?, ?, ?)
                """,
                (match_id, veto_order, veto_team_id, s.map_name, s.veto_type)
            )
        
#map result data
for event_id in vct_event_ids:
    event_matches = vlr.event.matches(
        event_id=event_id,
        state="completed"
    )
    for m in event_matches.matches:

        match_id = m.match_id
        series_info = vlr.series.info(series_id=match_id)

        for game in series_info.games:
            winner_id = 0
            loser_id = 0

            if (not game.played or game.team1_score is None or game.team2_score is None):
                continue
            
            if game.team1_score > game.team2_score:
                winner_id = series_info.team1.id
                loser_id = series_info.team2.id
            else:
                winner_id = series_info.team2.id
                loser_id = series_info.team1.id


            cursor.execute(
                """
                INSERT OR IGNORE INTO map_results
                (match_id, map_number, map_name, team_a_score, team_b_score, winner_id, team_a_attack_rounds, team_b_attack_rounds, team_a_defense_rounds, team_b_defense_rounds, loser_id)
                VALUES(?,?,?,?,?,?,?,?,?,?,?)
                """,      
                (  match_id, game.order, game.map_name, game.team1_score, game.team2_score, winner_id ,game.team1_attack_rounds,
                  game.team2_attack_rounds,game.team1_defense_rounds,
                  game.team2_defense_rounds, loser_id)
            )


conn.commit()
conn.close()     
print("done")
