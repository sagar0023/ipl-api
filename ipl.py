import pandas as pd
import numpy as np
import json

# Loading matches data from the source
ipl_matches = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRy2DUdUbaKx_Co9F0FSnIlyS-8kp4aKv_I0-qzNeghiZHAI_hw94gKG22XTxNJHMFnFVKsO4xWOdIs/pub?gid=1655759976&single=true&output=csv"
matches = pd.read_csv(ipl_matches)

# Optimized teamsAPI function for speed
def teamsAPI():
    teams = matches['Team1'].unique()  # Use unique directly on Team1 (avoids need to recompute teams)
    
    team_id = ["v172483766/rr_czknnb.png", "v172483769/rcb_jz39ny.png", 'v172483766/srh_k353jp.jpg',
               'v172483767/dc_bpj6t5.webp', 'v172483765/csk_zo7eq8.jpg', 'v172483766/gt_oj20zu.webp',
               'v1724837267/lcg_aoxac6.jpg', 'v172483767/kkr_imyk7p.webp', 'v172483768/pk_hdzfml.webp',
               'v172483767/mi_th59xu.jpg', 'v172483768/kxip_zyxvor.png', 'v1724840479/dd_riqoio.jpg',
               'v1724837266/rps_yh8yoo.jpg', 'v1724840667/gl_miygl7.png', 'v1724837266/rps_yh8yoo.jpg',
               'v1724837267/pwi_rgfb0d.png', 'v1724837265/deccan_jcwwaj.jpg', 'v1724837266/ktk_ib6du5.png']

    # Zip the teams and team_ids directly in list comprehension (faster)
    teams_data = [{"name": team, "team_id": team_id} for team, team_id in zip(teams, team_id)]
    
    # Constructing the tree as JSON directly
    return json.dumps({"teams": teams_data})

# Optimized teamVteamAPI function for better performance
def teamVteamAPI(team1, team2):
    # Combine the unique team names from both columns in one step
    valid_teams = pd.unique(matches[['Team1', 'Team2']].values.ravel())
    
    if team1 in valid_teams and team2 in valid_teams:
        # Use boolean indexing with vectorized logical conditions
        temp_df = matches[((matches['Team1'] == team1) & (matches['Team2'] == team2)) |
                          ((matches['Team1'] == team2) & (matches['Team2'] == team1))]
        
        total_matches = len(temp_df)
        
        # Using get to avoid KeyError if a team has never won a match
        matches_won_team1 = temp_df['WinningTeam'].value_counts().get(team1, 0)
        matches_won_team2 = temp_df['WinningTeam'].value_counts().get(team2, 0)
        
        draws = total_matches - (matches_won_team1 + matches_won_team2)
        
        # Convert response to a dictionary
        response = {
            'total_matches': total_matches,
            team1: matches_won_team1,
            team2: matches_won_team2,
            'draws': draws
        }
        return response
    
    return {'message': 'invalid team name'}
