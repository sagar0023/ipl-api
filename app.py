from flask import Flask, jsonify, request
from flask_cors import CORS  # Import CORS
import ipl, season
import jugaad

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes by default

@app.route('/')
def home():
    return "Hey this is Sagar's API. Keep Hustling :)"

@app.route('/api/teams')
def teams():
    response = ipl.teamsAPI()
    return response

@app.route('/api/teamvteam')
def teamvteam():
    team1 = request.args.get('team1')
    team2 = request.args.get('team2')

    response = ipl.teamVteamAPI(team1, team2)
    
    return jsonify(response)

@app.route('/api/team-record')
def team_record():
    team_name = request.args.get('team')
    response = jugaad.teamAPI(team_name)
    return response

@app.route('/api/season')
def season_record():
    current_year = request.args.get('year')
    if (int(current_year) < 2008) or (int(current_year) > 2022):
        msg = {'message': 'Data not available or invalid year'}
        return jsonify(msg)
    
    if current_year == '2020':
        current_year = '2020/21'
    
    defected_year = ['2010', '2008']  # 2008 -> 2007/08 2010 -> 2009/10 2020 -> 2020/21
    if current_year in defected_year:
        current_year = str(int(current_year) - 1) + '/' + current_year[-2:]

    response = season.point_table(current_year)
    return response

@app.route('/api/batting-record')
def batting_record():
    batsman_name = request.args.get('batsman')
    response = jugaad.batsmanAPI(batsman_name)
    return response

@app.route('/api/bowling-record')
def bowling_record():
    bowler_name = request.args.get('bowler')
    response = jugaad.bowlerAPI(bowler_name)
    return response

if __name__ == '__main__':
    app.run(debug=True)
