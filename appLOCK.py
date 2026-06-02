import atexit
import logging
import os

import bcrypt
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from psycopg.types.json import Json

import db

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='.')
CORS(app)

atexit.register(db.close_pool)

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


SCHEMA_SQL = [
    """
    CREATE TABLE IF NOT EXISTS users (
        id BIGSERIAL PRIMARY KEY,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT now()
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS game_state (
        id SMALLINT PRIMARY KEY DEFAULT 1,
        state JSONB NOT NULL,
        updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
    );
    """
]


INIT_STATE_SQL = """
INSERT INTO game_state (id, state)
VALUES (1, %s)
ON CONFLICT (id)
DO NOTHING;
"""


def init_db():
    try:
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                for stmt in SCHEMA_SQL:
                    cur.execute(stmt)
                cur.execute(INIT_STATE_SQL, (Json(DEFAULT_STATE),))
        logger.info("Database initialized")
    except Exception:
        logger.exception("Database initialization failed")
        raise


def _get_state_from_db():
    try:
        rows = db.run_query("SELECT state FROM game_state WHERE id = %s", (1,))
        if rows:
            return rows[0][0]
        return DEFAULT_STATE
    except Exception:
        logger.exception("Failed to read game state")
        raise


def _save_state_to_db(state):
    try:
        db.run_query(
            """
            INSERT INTO game_state (id, state, updated_at)
            VALUES (1, %s, now())
            ON CONFLICT (id)
            DO UPDATE SET state = EXCLUDED.state, updated_at = now();
            """,
            (Json(state),)
        )
    except Exception:
        logger.exception("Failed to write game state")
        raise


def _hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")


def _verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


@app.route('/')
def index():
    return send_file('indexLOCK.html')


@app.route('/api/register', methods=['POST'])
def register():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"status": "error", "message": "Username and password are required"}), 400

    try:
        password_hash = _hash_password(password)
        db.run_query(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            (username, password_hash)
        )
        return jsonify({"status": "success", "message": "User registered"})
    except Exception as exc:
        logger.exception("Registration failed")
        message = "Registration failed"
        if "duplicate key" in str(exc).lower():
            message = "Username already exists"
            return jsonify({"status": "error", "message": message}), 409
        return jsonify({"status": "error", "message": message}), 500


@app.route('/api/login', methods=['POST'])
def login():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"status": "error", "message": "Username and password are required"}), 400

    try:
        rows = db.run_query(
            "SELECT password_hash FROM users WHERE username = %s",
            (username,)
        )
        if not rows:
            return jsonify({"status": "error", "message": "Invalid credentials"}), 401

        password_hash = rows[0][0]
        if _verify_password(password, password_hash):
            return jsonify({"status": "success", "message": "Authenticated"})

        return jsonify({"status": "error", "message": "Invalid credentials"}), 401
    except Exception:
        logger.exception("Login failed")
        return jsonify({"status": "error", "message": "Login failed"}), 500


@app.route('/api/state', methods=['GET'])
def get_state():
    try:
        return jsonify(_get_state_from_db())
    except Exception:
        return jsonify({"status": "error", "message": "Failed to load state"}), 500


@app.route('/api/update', methods=['POST'])
def update_state():
    new_data = request.json or {}
    try:
        _save_state_to_db(new_data)
        return jsonify({"status": "success", "data": new_data})
    except Exception:
        return jsonify({"status": "error", "message": "Failed to update state"}), 500


@app.route('/api/reset', methods=['POST'])
def reset_game():
    try:
        _save_state_to_db(DEFAULT_STATE)
        return jsonify({"status": "reset", "data": DEFAULT_STATE})
    except Exception:
        return jsonify({"status": "error", "message": "Failed to reset state"}), 500


@app.route('/api/db-test', methods=['GET'])
def db_test():
    try:
        db.run_query("SELECT 1")
        return jsonify({"status": "ok"})
    except Exception:
        return jsonify({"status": "error", "message": "Database connection failed"}), 500


if __name__ == '__main__':
    db.health_check()
    init_db()
    print("-------------------------------------------------------")
    print(" QUIZ SERVER RUNNING")
    print(" Open your browser to: http://localhost:5000")
    print("-------------------------------------------------------")
    app.run(host='0.0.0.0', port=5000, debug=True)
