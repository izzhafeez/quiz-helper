from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_cors import CORS
import os
import sys
import socket

app = Flask(__name__)
CORS(app)
MONGO_PASSWORD = os.environ.get('MONGO_PASSWORD')

@app.route("/")
def hello_world():
    version = sys.version_info
    res = (
        "<h1>Hello my friends</h1>"
        f"<h2>{os.getenv('ENV')}</h2></br>"
        f"Running Python: {version.major}.{version.minor}.{version.micro}<br>"
        f"Hostname: {socket.gethostname()}"
    )
    return res

@app.route('/api/<string:quiz_type>/<string:quiz_name>', methods=['POST'])
def map_quiz(quiz_type, quiz_name):
  if request.method != 'POST':
    return 'Invalid request method', 405
  connection = f"mongodb+srv://admin:{MONGO_PASSWORD}@cluster0.1jxisbd.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0&tlsCAFile=isrgrootx1.pem"
  client = MongoClient(connection)
  name = request.json['name']
  score = request.json['score']

  quiz = client.quiz[quiz_type].find_one({ 'quiz_name': quiz_name })
  if not quiz:
    client.quiz[quiz_type].insert_one({
      'quiz_name': quiz_name,
      'players': [],
      'plays': 0
    })
    quiz = client.quiz[quiz_type].find_one({ 'quiz_name': quiz_name })

  if not name:
    client.quiz[quiz_type].update_one({
      'quiz_name': quiz_name
    }, {
      '$set': {
        'plays': quiz['plays'] + 1
      }
    })

  players = quiz['players']
  # save only the top 10 players
  player_data = {
    'name': name,
    'score': score,
  }

  player_found = False
  for player in players:
    if player['name'] == name:
      if player['score'] < score:
        player['score'] = score
        players.sort(key=lambda x: (x['score']))
      player_found = True

  if len(players) < 10 and not player_found:
    players.append(player_data)
    players.sort(key=lambda x: (x['score']))
  else:
    players.append(player_data)
    players.sort(key=lambda x: (x['score']))
    players.pop()
  
  client.quiz[quiz_type].update_one({
    'quiz_name': quiz_name
  }, {
    '$set': {
      'players': players,
      'plays': quiz['plays'] + 1
    }
  })
  return jsonify({
    'players': players,
    'plays': quiz['plays'] + 1
  })

@app.route('/api/<string:quiz_type>/<string:quiz_name>', methods=['GET'])
def get_map_quiz(quiz_type, quiz_name):
  if request.method != 'GET':
    return 'Invalid request method', 405
  connection = f"mongodb+srv://admin:{MONGO_PASSWORD}@cluster0.1jxisbd.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0&tlsCAFile=isrgrootx1.pem"
  client = MongoClient(connection)
  result = client.quiz[quiz_type].find_one({
    'quiz_name': quiz_name
  }, {"_id": 0})
  if not result:
    client.quiz[quiz_type].insert_one({
      'quiz_name': quiz_name,
      'players': [],
      'plays': 0
    })
    return {
      'quiz_name': quiz_name,
      'players': [],
      'plays': 0
    }
  return jsonify(result)