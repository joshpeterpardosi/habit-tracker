# Habit Tracker

A tiny habit-tracking HTTP API in plain Python 3 (stdlib only, no dependencies). Data is stored in a JSON file.

## Run the server
```bash
cd habit-tracker
HABIT_DATA_FILE=habits.json python src/server.py 8000
```
- `HABIT_DATA_FILE`: JSON storage path (default `./habits.json`).
- `HABIT_TODAY`: optional ISO date override for "today" (e.g. `2026-10-05`), useful for testing.

On Windows PowerShell: `$env:HABIT_DATA_FILE="habits.json"; python src\server.py 8000`

## API
| Method | Path | Result |
|---|---|---|
| POST | `/habits` | Create habit `{"name": "..."}` → 201 |
| POST | `/habits/{id}/check-in` | Check in for today → 201; **409** if already checked in today |
| GET | `/habits/{id}/streak` | Current streak + check-ins → 200 |

```bash
curl -X POST localhost:8000/habits -d '{"name":"Read"}'
curl -X POST localhost:8000/habits/<id>/check-in
curl localhost:8000/habits/<id>/streak
```

**Streak rule:** number of consecutive days ending today or yesterday; 0 if the last check-in is older than yesterday. Computed per request, never stored.

## Tests
```bash
cd habit-tracker && python -m unittest discover -s tests -v
```
Each test starts the real server as a subprocess on a free port with a temp data file and talks real HTTP.

## Verification
`docs/verify.md` describes how to run and verify the server against a live process. The tests prove:
- duplicate same-day check-in returns 409 and changes nothing (API and on disk);
- streaks reset after a missed day, count unbroken runs, and still count a run ending yesterday;
- the same rule holds through real check-ins across server restarts with different dates;
- data persists after the process is killed and restarted.

## Demo
```bash
cd habit-tracker && python demo.py
```
Starts the server on a free port with a temp data file, creates a habit, checks in, tries a duplicate check-in (409), reads the streak, then stops the server.

Real output:
```
Server started (pid 343163): READY 41639

>>> POST /habits  {"name": "Read"}
<<< 201  {"habit_id": "3e0c3a6782e04812a27b4a6398c47694", "name": "Read", "created_at": "2026-10-14", "check_ins": []}

>>> POST /habits/3e0c3a6782e04812a27b4a6398c47694/check-in
<<< 201  {"habit_id": "3e0c3a6782e04812a27b4a6398c47694", "name": "Read", "created_at": "2026-10-14", "check_ins": ["2026-10-14"]}

>>> POST /habits/3e0c3a6782e04812a27b4a6398c47694/check-in
<<< 409  {"error": "already checked in today", "habit": {"habit_id": "3e0c3a6782e04812a27b4a6398c47694", "name": "Read", "created_at": "2026-10-14", "check_ins": ["2026-10-14"]}}
    duplicate check-in rejected: True

>>> GET /habits/3e0c3a6782e04812a27b4a6398c47694/streak
<<< 200  {"habit_id": "3e0c3a6782e04812a27b4a6398c47694", "streak": 1, "check_ins": ["2026-10-14"]}

Server stopped.
```
