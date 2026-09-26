from datetime import datetime
import pendulum
import os 
from src.shared.scheduler import get_live_games as check_live

# TEAMS / PLAYERS OF INTEREST (Update these as needed without touching Docker or .env)
TEAMS_OF_INTEREST = ["UConn", "Northwestern", "UCLA"]
PLAYERS_OF_INTEREST = []  # Leave empty to track all players for the teams above, or add specific names

# UPDATE GAME SCHEDULE WITH GAMES OF INTEREST AS NEEDED
GAME_SCHEDULE = [
    {"date": "2025-12-28", "start_time": "16:00", "end_time": "18:30", "event_id": "401825613", "teams": "UConn"},
    {"date": "2026-01-07", "start_time": "18:30", "end_time": "21:00", "event_id": "401825629", "teams": "UConn"},
    {"date": "2026-01-11", "start_time": "13:00", "end_time": "15:30", "event_id": "401825635", "teams": "UConn"},
    {"date": "2026-01-15", "start_time": "18:00", "end_time": "20:30", "event_id": "401825641", "teams": "UConn"},
    {"date": "2026-01-19", "start_time": "16:00", "end_time": "18:30", "event_id": "401817390", "teams": "UConn"},
    {"date": "2026-01-22", "start_time": "18:30", "end_time": "21:00", "event_id": "401825651", "teams": "UConn"},
    {"date": "2026-01-25", "start_time": "11:00", "end_time": "13:30", "event_id": "401825654", "teams": "UConn"},

    {"date": "2026-01-11", "start_time": "14:00", "end_time": "16:30", "event_id": "401825265", "teams": "Northwestern"},
    {"date": "2026-01-15", "start_time": "19:00", "end_time": "21:30", "event_id": "401825276", "teams": "Northwestern"},
    {"date": "2026-01-18", "start_time": "14:00", "end_time": "16:30", "event_id": "401825281", "teams": "Northwestern"},
    {"date": "2026-01-25", "start_time": "15:00", "end_time": "17:30", "event_id": "401825298", "teams": "Northwestern"},
    {"date": "2026-02-05", "start_time": "20:00", "end_time": "22:30", "event_id": "401825326", "teams": "Northwestern"},

    # test game
    {"date": "2026-01-11", "start_time": "19:00", "end_time": "20:30", "event_id": "401825267", "teams": "Test Match"},
]

def get_live_games(now=None):
    """Wrapper that passes the specified NCAABB game schedule to the shared scheduler utility."""
    return check_live(GAME_SCHEDULE, now)