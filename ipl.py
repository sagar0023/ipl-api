import pandas as pd
import numpy as np
import json
ipl_matches = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRy2DUdUbaKx_Co9F0FSnIlyS-8kp4aKv_I0-qzNeghiZHAI_hw94gKG22XTxNJHMFnFVKsO4xWOdIs/pub?gid=1655759976&single=true&output=csv"
matches = pd.read_csv(ipl_matches)



def teamsAPI():
    teams = list(matches['Team1'].unique())
    team_id = ["v172483766/rr_czknnb.png","v172483769/rcb_jz39ny.png",'v172483766/srh_k353jp.jpg',
          'v172483767/dc_bpj6t5.webp','v172483765/csk_zo7eq8.jpg','v172483766/gt_oj20zu.webp','v1724837267/lcg_aoxac6.jpg','v172483767/kkr_imyk7p.webp','v172483768/pk_hdzfml.webp','v172483767/mi_th59xu.jpg',
          'v172483768/kxip_zyxvor.png','v1724840479/dd_riqoio.jpg','v1724837266/rps_yh8yoo.jpg','v1724840667/gl_miygl7.png','v1724837266/rps_yh8yoo.jpg',
          'v1724837267/pwi_rgfb0d.png','v1724837265/deccan_jcwwaj.jpg','v1724837266/ktk_ib6du5.png']
    
    # Create a dictionary with a tree-like structure
    team_tree = {"teams": []}

    # Populate the tree with team data
    for team, id in zip(teams, team_id):
        team_tree["teams"].append({
            "name": team,
            "team_id": id
        })

    # Convert the dictionary to a JSON object
    return json.dumps(team_tree)

def teamVteamAPI(team1,team2):

    valid_teams = list(set(list(matches['Team1']) + list(matches['Team2'])))

    if team1 in valid_teams and team2 in valid_teams:

        temp_df = matches[(matches['Team1'] == team1) & (matches['Team2'] == team2) | (matches['Team1'] == team2) & (matches['Team2'] == team1)]
        total_matches = temp_df.shape[0]

        matches_won_team1 = temp_df['WinningTeam'].value_counts()[team1]
        matches_won_team2 = temp_df['WinningTeam'].value_counts()[team2]

        draws = total_matches - (matches_won_team1 + matches_won_team2)

        response = {
              'total_matches': str(total_matches),
              team1: str(matches_won_team1),
              team2: str(matches_won_team2),
              'draws': str(draws)
          }

        return response
    else:
        return {'message':'invalid team name'}
