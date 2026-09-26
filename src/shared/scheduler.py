# src/common/scheduler.py
from datetime import datetime
import pendulum
import os

# Read timezone from .env, assume Central time if missing 
TZ_NAME = os.getenv("SCHEDULE_TIMEZONE", "America/Chicago") 
LOCAL_TZ = pendulum.timezone(TZ_NAME)

def parse_game_window(game):
    """Parse game date and times into timezone-aware datetimes using Pendulum."""
    naive_start = datetime.strptime(f"{game['date']} {game['start_time']}", "%Y-%m-%d %H:%M")
    naive_end = datetime.strptime(f"{game['date']} {game['end_time']}", "%Y-%m-%d %H:%M")

    # Safely attach local timezone context
    start_dt = LOCAL_TZ.datetime(
        naive_start.year, naive_start.month, naive_start.day,
        naive_start.hour, naive_start.minute
    )
    end_dt = LOCAL_TZ.datetime(
        naive_end.year, naive_end.month, naive_end.day,
        naive_end.hour, naive_end.minute
    )

    return start_dt, end_dt

def get_live_games(game_schedule, now=None):
    """Generic function to return any games from a schedule that are live at the given time."""
    if now is None:
        now = pendulum.now(LOCAL_TZ)
    else:
        now = now.in_timezone(LOCAL_TZ)

    live = []
    for game in game_schedule:
        start_dt, end_dt = parse_game_window(game)
        if start_dt <= now <= end_dt:
            live.append(game)

    return live