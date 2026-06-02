import atexit
import json
import logging
import os

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

import db

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))

app = Flask(__name__, static_folder='.')
CORS(app)

atexit.register(db.close_pool)

DATA_FILE = 'game_data.json'

# Default state if no game is running
DEFAULT_STATE = {
    "isGameStarted": False,
    "currentRoundIndex": 0,
    "rounds": [
        {"id": "r1", "name": "Round 1"},
        {"id": "r2", "name": "Round 2"},
        {"id": "r3", "name": "Round 3"},
        {"id": "r4", "name": "Round 4"},
        {"id": "r5", "name": "Round 5"},
        {"id": "r6", "name": "Round 6"}
    ],
    "teams": [
        {"id": "t1", "name": "Team 1", "scores": {}, "totalScore": 0},
        {"id": "t2", "name": "Team 2", "scores": {}, "totalScore": 0},
        {"id": "t3", "name": "Team 3", "scores": {}, "totalScore": 0},
        {"id": "t4", "name": "Team 4", "scores": {}, "totalScore": 0},
        {"id": "t5", "name": "Team 5", "scores": {}, "totalScore": 0},
        {"id": "t6", "name": "Team 6", "scores": {}, "totalScore": 0},
        {"id": "t7", "name": "Team 7", "scores": {}, "totalScore": 0},
        {"id": "t8", "name": "Team 8", "scores": {}, "totalScore": 0}
    ]
}

def load_data():
    if not os.path.exists(DATA_FILE):
        save_data(DEFAULT_STATE)
        return DEFAULT_STATE
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except:
        return DEFAULT_STATE

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def index():
    # Looks for index.html in the same folder
    return send_file('index.html')

@app.route('/api/state', methods=['GET'])
def get_state():
    return jsonify(load_data())

@app.route('/api/update', methods=['POST'])
def update_state():
    new_data = request.json
    save_data(new_data)
    return jsonify({"status": "success", "data": new_data})

@app.route('/api/reset', methods=['POST'])
def reset_game():
    save_data(DEFAULT_STATE)
    return jsonify({"status": "reset", "data": DEFAULT_STATE})


@app.route('/api/db-test', methods=['GET'])
def db_test():
    try:
        db.run_query("SELECT 1")
        return jsonify({"status": "ok"})
    except Exception:
        return jsonify({"status": "error", "message": "Database connection failed"}), 500

if __name__ == '__main__':
    db.health_check()
    print("-------------------------------------------------------")
    print(" QUIZ SERVER RUNNING")
    print(" Open your browser to: http://localhost:5000")
    print("-------------------------------------------------------")
    app.run(host='0.0.0.0', port=5000, debug=True)