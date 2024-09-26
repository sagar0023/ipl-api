import numpy as np
import pandas as pd

# Load the IPL dataset
ipl = pd.read_csv("https://docs.google.com/spreadsheets/d/e/2PACX-1vRy2DUdUbaKx_Co9F0FSnIlyS-8kp4aKv_I0-qzNeghiZHAI_hw94gKG22XTxNJHMFnFVKsO4xWOdIs/pub?gid=1655759976&single=true&output=csv")

# Optimized matches_played function with vectorization
def matches_played(csdf, team):
    return (csdf['Team1'].eq(team) | csdf['Team2'].eq(team)).sum()

# Optimized matches_won function with vectorization
def matches_won(csdf, team):
    return csdf['WinningTeam'].eq(team).sum()

# Optimized match_no_result function with vectorization
def match_no_result(csdf, team):
    return ((csdf['Team1'].eq(team) | csdf['Team2'].eq(team)) & csdf['WinningTeam'].isna()).sum()

# Optimized point_table function
def point_table(season):
    # Filter for the current season
    csdf = ipl[ipl['Season'] == season]

    # Vectorized calculation of the LoosingTeam column using np.where
    csdf['LoosingTeam'] = np.where(csdf['WinningTeam'] == csdf['Team1'], csdf['Team2'], csdf['Team1'])
    
    # Get the final match data
    final_match = csdf.loc[csdf['MatchNumber'] == 'Final'].iloc[0]
    winning_team_str = final_match['WinningTeam']
    runner_str = final_match['LoosingTeam']
    
    # Get unique teams for the current season
    teams = csdf['Team1'].unique()

    # Calculate the number of matches played, won, and no results for each team in vectorized form
    matches_played_count = {team: matches_played(csdf, team) for team in teams}
    matches_won_count = {team: matches_won(csdf, team) for team in teams}
    no_result_count = {team: match_no_result(csdf, team) for team in teams}

    # Create a DataFrame for the points table
    table_df = pd.DataFrame({
        'TeamName': teams,
        'MatchesPlayed': [matches_played_count[team] for team in teams],
        'MatchesWon': [matches_won_count[team] for team in teams],
        'NoResult': [no_result_count[team] for team in teams]
    })

    # Calculate points: 2 points for each win, 1 point for each no result
    table_df['Points'] = table_df['MatchesWon'] * 2 + table_df['NoResult']

    # Rank teams based on points
    table_df['SeasonPosition'] = table_df['Points'].rank(ascending=False, method='first').astype('object')

    # Set 'Winner' and 'Runner' labels for the final match
    table_df.loc[table_df['TeamName'] == winning_team_str, 'SeasonPosition'] = 'Winner'
    table_df.loc[table_df['TeamName'] == runner_str, 'SeasonPosition'] = 'Runner'

    # Sort the table by points and reset the index
    table_df.sort_values('Points', ascending=False, inplace=True)
    table_df.reset_index(drop=True, inplace=True)

    # Return the points table as JSON
    return table_df.to_json(orient='columns')
