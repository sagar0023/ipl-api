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

ipl_matches = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRy2DUdUbaKx_Co9F0FSnIlyS-8kp4aKv_I0-qzNeghiZHAI_hw94gKG22XTxNJHMFnFVKsO4xWOdIs/pub?gid=1655759976&single=true&output=csv"
matches = pd.read_csv(ipl_matches)

teams_arr = matches['Team1'].unique()

def add_(teams_arr, ipl):
    for col in ['Team1', 'Team2', 'WinningTeam']:
        ipl[col] = ipl[col].str.replace(" ", "_")

ipl_ball = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRu6cb6Pj8C9elJc5ubswjVTObommsITlNsFy5X0EiBY7S-lsHEUqx3g_M16r50Ytjc0XQCdGDyzE_Y/pub?output=csv"
balls = pd.read_csv(ipl_ball)

ball_withmatch = balls.merge(matches, on='ID', how='inner')
ball_withmatch['BowlingTeam'] = ball_withmatch['Team1'] + ball_withmatch['Team2']
ball_withmatch['BowlingTeam'] = ball_withmatch.apply(
    lambda x: x['BowlingTeam'].replace(x['BattingTeam'], ''), axis=1
)

batter_data = ball_withmatch[list(balls.columns.values) + ['BowlingTeam', 'Player_of_Match']]

def team1vsteam2(team, team2):
    df = matches[((matches['Team1'] == team) & (matches['Team2'] == team2)) | 
                 ((matches['Team2'] == team) & (matches['Team1'] == team2))]
    mp = len(df)
    won = len(df[df.WinningTeam == team])
    nr = len(df[df.WinningTeam.isnull()])
    loss = mp - won - nr

    return {'matchesplayed': mp, 'won': won, 'loss': loss, 'noResult': nr}

def allRecord(team):
    df = matches[(matches['Team1'] == team) | (matches['Team2'] == team)]
    mp = len(df)
    won = len(df[df.WinningTeam == team])
    nr = len(df[df.WinningTeam.isnull()])
    loss = mp - won - nr
    nt = len(df[(df.MatchNumber == 'Final') & (df.WinningTeam == team)])
    
    return {'matchesplayed': mp, 'won': won, 'loss': loss, 'noResult': nr, 'title': nt}

def teamAPI(team, matches=matches):
    self_record = allRecord(team)
    Teams = matches.Team1.unique()
    Teams = [t for t in Teams if t != team]
    against = {team2: team1vsteam2(team, team2) for team2 in Teams}
    
    data = {team: {'overall': self_record, 'against': against}}
    return json.dumps(data, cls=NpEncoder)

def batsmanRecord(batsman, df):
    if df.empty:
        return np.nan
    
    out = df[df.player_out == batsman].shape[0]
    df = df[df['batter'] == batsman]
    inngs = df['ID'].nunique()
    runs = df['batsman_run'].sum()
    fours = df[(df['batsman_run'] == 4) & (df['non_boundary'] == 0)].shape[0]
    sixes = df[(df['batsman_run'] == 6) & (df['non_boundary'] == 0)].shape[0]
    avg = runs / out if out else np.inf
    nballs = df[~(df['extra_type'] == 'wides')].shape[0]
    strike_rate = (runs / nballs * 100) if nballs else 0
    
    gb = df.groupby('ID').sum()
    fifties = len(gb[(gb.batsman_run >= 50) & (gb.batsman_run < 100)])
    hundreds = len(gb[gb.batsman_run >= 100])
    
    highest_score = gb['batsman_run'].max()
    if out:
        hsindex = gb['batsman_run'].idxmax()
        highest_score = str(highest_score) + '*' if not (df[df.ID == hsindex].player_out == batsman).any() else str(highest_score)
    
    not_out = inngs - out
    mom = df[df.Player_of_Match == batsman].drop_duplicates('ID', keep='first').shape[0]
    
    return {'innings': inngs, 'runs': runs, 'fours': fours, 'sixes': sixes, 'avg': avg, 'strikeRate': strike_rate,
            'fifties': fifties, 'hundreds': hundreds, 'highestScore': highest_score, 'notOut': not_out, 'mom': mom}

def batsmanVsTeam(batsman, team, df):
    return batsmanRecord(batsman, df[df.BowlingTeam == team])

def batsmanAPI(batsman, balls=batter_data):
    df = balls[balls.innings.isin([1, 2])]
    self_record = batsmanRecord(batsman, df)
    TEAMS = matches.Team1.unique()
    against = {team: batsmanVsTeam(batsman, team, df) for team in TEAMS}
    
    data = {batsman: {'all': self_record, 'against': against}}
    return json.dumps(data, cls=NpEncoder)

bowler_data = batter_data.copy()

def bowlerRun(row):
    return 0 if row['extra_type'] in ['penalty', 'legbyes', 'byes'] else row['total_run']

bowler_data['bowler_run'] = bowler_data.apply(bowlerRun, axis=1)

def bowlerWicket(row):
    return row['isWicketDelivery'] if row['kind'] in ['caught', 'caught and bowled', 'bowled', 'stumped', 'lbw', 'hit wicket'] else 0

bowler_data['isBowlerWicket'] = bowler_data.apply(bowlerWicket, axis=1)

def bowlerRecord(bowler, df):
    df = df[df['bowler'] == bowler]
    inngs = df['ID'].nunique()
    nballs = df[~df['extra_type'].isin(['wides', 'noballs'])].shape[0]
    runs = df['bowler_run'].sum()
    eco = (runs / nballs * 6) if nballs else 0
    wicket = df['isBowlerWicket'].sum()
    avg = runs / wicket if wicket else np.inf
    strike_rate = (nballs / wicket * 100) if wicket else np.nan
    gb = df.groupby('ID').sum()
    w3 = len(gb[gb.isBowlerWicket >= 3])
    
    best_wicket = gb[['isBowlerWicket', 'bowler_run']].sort_values(['isBowlerWicket', 'bowler_run'], ascending=[False, True]).head(1)
    best_figure = f"{best_wicket['isBowlerWicket'].values[0]}/{best_wicket['bowler_run'].values[0]}" if not best_wicket.empty else np.nan
    mom = df[df.Player_of_Match == bowler].drop_duplicates('ID', keep='first').shape[0]
    
    return {'innings': inngs, 'wicket': wicket, 'economy': eco, 'average': avg, 'strikeRate': strike_rate,
            'fours': len(df[(df['batsman_run'] == 4) & (df['non_boundary'] == 0)]), 'sixes': len(df[(df['batsman_run'] == 6) & (df['non_boundary'] == 0)]),
            'best_figure': best_figure, '3+W': w3, 'mom': mom}

def bowlerVsTeam(bowler, team, df):
    return bowlerRecord(bowler, df[df.BattingTeam == team])

def bowlerAPI(bowler, balls=bowler_data):
    df = balls[balls.innings.isin([1, 2])]
    self_record = bowlerRecord(bowler, df)
    TEAMS = matches.Team1.unique()
    against = {team: bowlerVsTeam(bowler, team, df) for team in TEAMS}
    
    data = {bowler: {'all': self_record, 'against': against}}
    return json.dumps(data, cls=NpEncoder)
