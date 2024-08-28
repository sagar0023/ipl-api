from flask import Flask,jsonify,request
import ipl
import jugaad

app = Flask(__name__)

@app.route('/')
def home():
    return "hello world"

@app.route('/api/teams')
def teams():
    response = ipl.teamsAPI()
    return response

@app.route('/api/teamvteam')
def teamvteam():
    team1 = request.args.get('team1')
    team2 = request.args.get('team2')

    response = ipl.teamVteamAPI(team1,team2)
    
    return jsonify(response)

@app.route('/api/team-record')
def team_record():
    team_name = request.args.get('team')
    response = jugaad.teamAPI(team_name)
    return response

if __name__ == '__main__':
    app.run(debug=True)
