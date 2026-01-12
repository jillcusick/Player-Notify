from datetime import datetime, time
import pendulum
import os 

# UPDATE GAME SCHEDULE WITH GAMES OF INTEREST AS NEEDED
GAME_SCHEDULE = [
    {"date": "2025-12-28", "start_time": "16:00", "end_time": "18:30", "event_id": "401825613"},
    {"date": "2026-01-07", "start_time": "18:30", "end_time": "21:00", "event_id": "401825629"},
    {"date": "2026-01-11", "start_time": "13:00", "end_time": "15:30", "event_id": "401825635"},
    {"date": "2026-01-15", "start_time": "18:00", "end_time": "20:30", "event_id": "401825641"},
    {"date": "2026-01-19", "start_time": "16:00", "end_time": "18:30", "event_id": "401817390"},
    {"date": "2026-01-22", "start_time": "18:30", "end_time": "21:00", "event_id": "401825651"},
    {"date": "2026-01-25", "start_time": "11:00", "end_time": "13:30", "event_id": "401825654"},  # UConn

    {"date": "2026-01-11", "start_time": "14:00", "end_time": "16:30", "event_id": "401825265"},
    {"date": "2026-01-15", "start_time": "19:00", "end_time": "21:30", "event_id": "401825276"},
    {"date": "2026-01-18", "start_time": "14:00", "end_time": "16:30", "event_id": "401825281"},
    {"date": "2026-01-25", "start_time": "15:00", "end_time": "17:30", "event_id": "401825298"},
    {"date": "2026-02-05", "start_time": "20:00", "end_time": "22:30", "event_id": "401825326"},  # Northwestern

    # test game
    {"date": "2026-01-11", "start_time": "19:00", "end_time": "20:30", "event_id": "401825267"},
]

# Set time zone to time used in schedule

# Read timezone from .env, assume CST if missing 
TZ_NAME = os.getenv("SCHEDULE_TIMEZONE", "America/Chicago") 
LOCAL_TZ = pendulum.timezone(TZ_NAME)

def parse_game_window(game):
    """Parse game date and times into timezone-aware datetimes."""
    # Build naive datetime 
    naive_start = datetime.strptime(f"{game['date']} {game['start_time']}", "%Y-%m-%d %H:%M")
    naive_end = datetime.strptime(f"{game['date']} {game['end_time']}", "%Y-%m-%d %H:%M")

    # Attach chosen timezone 
    start_dt = LOCAL_TZ.convert(naive_start.replace(tzinfo=LOCAL_TZ))
    end_dt = LOCAL_TZ.convert(naive_end.replace(tzinfo=LOCAL_TZ))

    return start_dt, end_dt

def get_live_games(now):
    """Return all games live at the given time."""
    now_local = now.in_timezone(LOCAL_TZ)

    live = []
    for game in GAME_SCHEDULE:
        start_dt, end_dt = parse_game_window(game)
        if start_dt <= now_local <= end_dt:
            live.append(game)

    return live

