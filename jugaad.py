import pandas as pd
import numpy as np
import json

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

# Load data (assumes pre-downloaded for better performance in real scenarios)
ipl_matches = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRy2DUdUbaKx_Co9F0FSnIlyS-8kp4aKv_I0-qzNeghiZHAI_hw94gKG22XTxNJHMFnFVKsO4xWOdIs/pub?gid=1655759976&single=true&output=csv"
matches = pd.read_csv(ipl_matches)

# Efficient team name cleanup with vectorization
def clean_team_names(df):
    for col in ['Team1', 'Team2', 'WinningTeam']:
        df[col] = df[col].str.replace(" ", "_", regex=False)
    return df

matches = clean_team_names(matches)

# Pre-load and preprocess ball data efficiently
ipl_ball = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRu6cb6Pj8C9elJc5ubswjVTObommsITlNsFy5X0EiBY7S-lsHEUqx3g_M16r50Ytjc0XQCdGDyzE_Y/pub?output=csv"
balls = pd.read_csv(ipl_ball)

# Merge data with pre-filtering for faster performance
ball_withmatch = balls.merge(matches[['ID', 'Team1', 'Team2', 'WinningTeam', 'Player_of_Match']], on='ID', how='inner')

# Vectorized Bowling Team creation
ball_withmatch['BowlingTeam'] = ball_withmatch['Team1'] + ball_withmatch['Team2']
ball_withmatch['BowlingTeam'] = np.where(ball_withmatch['BowlingTeam'].str.contains(ball_withmatch['BattingTeam']), 
                                         ball_withmatch['BowlingTeam'].str.replace(ball_withmatch['BattingTeam'], '', regex=False), 
                                         ball_withmatch['BowlingTeam'])

# Batter data filtering and structure
batter_data = ball_withmatch[list(balls.columns.values) + ['BowlingTeam', 'Player_of_Match']]

# Optimized team match stats retrieval
def team1vsteam2(team, team2):
    df = matches[((matches['Team1'] == team) & (matches['Team2'] == team2)) | 
                 ((matches['Team2'] == team) & (matches['Team1'] == team2))]
    mp = len(df)
    won = (df['WinningTeam'] == team).sum()
    nr = df['WinningTeam'].isnull().sum()
    loss = mp - won - nr
    return {'matchesplayed': mp, 'won': won, 'loss': loss, 'noResult': nr}

# Generalized and optimized record retrieval
def allRecord(team):
    df = matches[(matches['Team1'] == team) | (matches['Team2'] == team)]
    mp = len(df)
    won = (df['WinningTeam'] == team).sum()
    nr = df['WinningTeam'].isnull().sum()
    loss = mp - won - nr
    nt = ((df['MatchNumber'] == 'Final') & (df['WinningTeam'] == team)).sum()
    
    return {'matchesplayed': mp, 'won': won, 'loss': loss, 'noResult': nr, 'title': nt}

# Efficient Team API generation using list comprehension
def teamAPI(team, matches=matches):
    self_record = allRecord(team)
    Teams = [t for t in matches['Team1'].unique() if t != team]
    against = {team2: team1vsteam2(team, team2) for team2 in Teams}
    
    data = {team: {'overall': self_record, 'against': against}}
    return json.dumps(data, cls=NpEncoder)

# Highly optimized batsman record generation
def batsmanRecord(batsman, df):
    if df.empty:
        return np.nan
    
    out = (df['player_out'] == batsman).sum()
    df = df[df['batter'] == batsman]
    inngs = df['ID'].nunique()
    runs = df['batsman_run'].sum()
    fours = ((df['batsman_run'] == 4) & (df['non_boundary'] == 0)).sum()
    sixes = ((df['batsman_run'] == 6) & (df['non_boundary'] == 0)).sum()
    avg = runs / out if out else np.inf
    nballs = (~df['extra_type'].eq('wides')).sum()
    strike_rate = (runs / nballs * 100) if nballs else 0

    # Group by innings in a single operation
    gb = df.groupby('ID').agg({'batsman_run': 'sum'})
    fifties = ((gb['batsman_run'] >= 50) & (gb['batsman_run'] < 100)).sum()
    hundreds = (gb['batsman_run'] >= 100).sum()
    
    highest_score = gb['batsman_run'].max()
    hsindex = gb['batsman_run'].idxmax() if out else np.nan
    highest_score = str(highest_score) + '*' if not df[df['ID'] == hsindex]['player_out'].any() else str(highest_score)
    
    not_out = inngs - out
    mom = df['Player_of_Match'].eq(batsman).drop_duplicates('ID').sum()
    
    return {'innings': inngs, 'runs': runs, 'fours': fours, 'sixes': sixes, 'avg': avg, 'strikeRate': strike_rate,
            'fifties': fifties, 'hundreds': hundreds, 'highestScore': highest_score, 'notOut': not_out, 'mom': mom}

# Filter and optimize batting record against teams
def batsmanVsTeam(batsman, team, df):
    return batsmanRecord(batsman, df[df['BowlingTeam'] == team])

def batsmanAPI(batsman, balls=batter_data):
    df = balls[balls['innings'].isin([1, 2])]
    self_record = batsmanRecord(batsman, df)
    TEAMS = matches['Team1'].unique()
    against = {team: batsmanVsTeam(batsman, team, df) for team in TEAMS}
    
    data = {batsman: {'all': self_record, 'against': against}}
    return json.dumps(data, cls=NpEncoder)

# Bowler data preparation
def prepare_bowler_data(df):
    df['bowler_run'] = np.where(df['extra_type'].isin(['penalty', 'legbyes', 'byes']), 0, df['total_run'])
    df['isBowlerWicket'] = np.where(df['kind'].isin(['caught', 'caught and bowled', 'bowled', 'stumped', 'lbw', 'hit wicket']), 
                                    df['isWicketDelivery'], 0)
    return df

bowler_data = prepare_bowler_data(batter_data)

# Optimized bowler record generation
def bowlerRecord(bowler, df):
    df = df[df['bowler'] == bowler]
    inngs = df['ID'].nunique()
    nballs = (~df['extra_type'].isin(['wides', 'noballs'])).sum()
    runs = df['bowler_run'].sum()
    eco = (runs / nballs * 6) if nballs else 0
    wicket = df['isBowlerWicket'].sum()
    avg = runs / wicket if wicket else np.inf
    strike_rate = (nballs / wicket * 100) if wicket else np.nan

    gb = df.groupby('ID').agg({'isBowlerWicket': 'sum', 'bowler_run': 'sum'})
    w3 = (gb['isBowlerWicket'] >= 3).sum()

    best_wicket = gb[['isBowlerWicket', 'bowler_run']].sort_values(['isBowlerWicket', 'bowler_run'], ascending=[False, True]).head(1)
    best_figure = f"{best_wicket['isBowlerWicket'].values[0]}/{best_wicket['bowler_run'].values[0]}" if not best_wicket.empty else np.nan
    mom = df['Player_of_Match'].eq(bowler).drop_duplicates('ID').sum()

    return {'innings': inngs, 'wicket': wicket, 'economy': eco, 'average': avg, 'strikeRate': strike_rate,
            'fours': ((df['batsman_run'] == 4) & (df['non_boundary'] == 0)).sum(), 
            'sixes': ((df['batsman_run'] == 6) & (df['non_boundary'] == 0)).sum(),
            'best_figure': best_figure, '3+W': w3, 'mom': mom}

# Optimized API generation for bowler records
def bowlerVsTeam(bowler, team, df):
    return bowlerRecord(bowler, df[df['BattingTeam'] == team])

def bowlerAPI(bowler, balls=bowler_data):
    df = balls[balls['innings'].isin([1, 2])]
    self_record = bowlerRecord(bowler, df)
    TEAMS = matches['Team1'].unique()
    against = {team: bowlerVsTeam(bowler, team, df) for team in TEAMS}
    
    data = {bowler: {'all': self_record, 'against': against}}
    return json.dumps(data, cls=NpEncoder)

