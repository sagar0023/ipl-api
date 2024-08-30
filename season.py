import numpy as np
import pandas as pd
ipl = pd.read_csv("https://docs.google.com/spreadsheets/d/e/2PACX-1vRy2DUdUbaKx_Co9F0FSnIlyS-8kp4aKv_I0-qzNeghiZHAI_hw94gKG22XTxNJHMFnFVKsO4xWOdIs/pub?gid=1655759976&single=true&output=csv")

def matches_played(csdf,team):
    return ((csdf.Team1 == team) | (csdf.Team2 == team)).sum()

def matches_won(csdf,team):
    return (csdf.WinningTeam == team).sum()

def match_no_result(csdf,team):
    return (((csdf.Team1 == team) | (csdf.Team2 == team)) & csdf.WinningTeam.isna()).sum()

def point_table(season):
    csdf = ipl[ipl.Season == season].copy()
    csdf['LoosingTeam'] = csdf[csdf.WinningTeam == csdf.Team1]['Team2'].combine_first(csdf[csdf.WinningTeam == csdf.Team2]['Team1'])

    fmdf = csdf[csdf['MatchNumber'] == 'Final']
    winning_team_str = fmdf.WinningTeam.values[0]
    runner_str = fmdf.LoosingTeam.values[0]
    
    
    

    table_df = pd.DataFrame()
    table_df['TeamName'] = csdf.Team1.unique()
    table_df['MatchesPlayed'] = table_df['TeamName'].apply(lambda x : matches_played(csdf,x))
    table_df['MatchesWon'] = table_df['TeamName'].apply(lambda x : matches_won(csdf,x))
    table_df['NoResult'] = table_df['TeamName'].apply(lambda x : match_no_result(csdf,x))
    table_df['Points'] = table_df['MatchesWon']*2+table_df['NoResult']

    table_df['SeasonPosition'] = table_df.Points.rank(ascending = False,method='first').astype('object')
    table_df.set_index('TeamName',inplace=True)
    table_df.sort_values('Points',ascending=False,inplace=True)
    table_df.loc[winning_team_str,'SeasonPosition'] = 'Winner'
    table_df.at[runner_str,'SeasonPosition'] = 'Runner'

    table_df.reset_index(inplace=True)

    return table_df.to_json(orient='columns')


