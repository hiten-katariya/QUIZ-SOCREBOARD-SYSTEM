# QUIZ SCOREBOARD SYSTEM

Simple Flask-based quiz scoreboard app with:

- a spectator display
- an admin control screen
- round and team management
- persistent score storage in a local JSON file

## Project files

- `/home/runner/work/QUIZ-SOCREBOARD-SYSTEM/QUIZ-SOCREBOARD-SYSTEM/app.py` - Flask server and API
- `/home/runner/work/QUIZ-SOCREBOARD-SYSTEM/QUIZ-SOCREBOARD-SYSTEM/index.html` - main frontend UI
- `/home/runner/work/QUIZ-SOCREBOARD-SYSTEM/QUIZ-SOCREBOARD-SYSTEM/appLOCK.py` - alternate server entrypoint for the locked version
- `/home/runner/work/QUIZ-SOCREBOARD-SYSTEM/QUIZ-SOCREBOARD-SYSTEM/indexLOCK.html` - alternate locked UI

## Features

- create and manage quiz rounds
- add, rename, and remove teams
- update scores from the admin console
- show live standings on the spectator screen
- reset the full game or start a new game with the same teams
- export and import game data as JSON

## Requirements

- Python 3
- Flask
- flask-cors

Install dependencies:

```bash
pip install Flask flask-cors
```

## Run locally

From `/home/runner/work/QUIZ-SOCREBOARD-SYSTEM/QUIZ-SOCREBOARD-SYSTEM`:

```bash
python app.py
```

Then open:

```text
http://localhost:5000
```

## API endpoints

- `GET /api/state` - get current game state
- `POST /api/update` - save updated game state
- `POST /api/reset` - reset the game to the default state

## Data storage

The app stores game state in `game_data.json`, which is created automatically if it does not already exist.
