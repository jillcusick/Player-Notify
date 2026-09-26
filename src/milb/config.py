from datetime import datetime
import pendulum
import os 
from src.shared.scheduler import get_live_games as check_live

# Define target player to track in the game (or leave blank to track all pitching changes)
## UPDATE AS NEEDED ##
TARGET_PLAYER = ""

# Define games to track and notify (including start/end times for Airflow scheduling)
## UPDATE AS NEEDED ##
GAME_SCHEDULE = [
    {
        "teams": "ironpigs-vs-mets",
        "date": "2026-09-17",
        "start_time": "17:35",  # Adjust to local start time
        "end_time": "20:35",    # Adjust to expected local end time
        "event_id": "815634",
        "url": "https://www.milb.com/gameday/ironpigs-vs-mets/2026/09/17/815634/preview?affiliateId=mlbcom-milb"
    },
    {
        "teams": "ironpigs-vs-mets",
        "date": "2026-09-18",
        "start_time": "17:35",
        "end_time": "20:35",
        "event_id": "815624",
        "url": "https://www.milb.com/gameday/ironpigs-vs-mets/2026/09/18/815624/preview?affiliateId=mlbcom-milb"
    },
    {
        "teams": "ironpigs-vs-mets",
        "date": "2026-09-19",
        "start_time": "17:35",
        "end_time": "20:35",
        "event_id": "815623",
        "url": "https://www.milb.com/gameday/ironpigs-vs-mets/2026/09/19/815623/preview?affiliateId=mlbcom-milb"
    },
    {
        "teams": "ironpigs-vs-mets",
        "date": "2026-09-20",
        "start_time": "12:05",  
        "end_time": "16:05",
        "event_id": "815628",
        "url": "https://www.milb.com/gameday/ironpigs-vs-mets/2026/09/20/815628/preview?affiliateId=mlbcom-milb"
    }
]

def get_live_games(now=None):
    """Wrapper that passes the specified MiLB game schedule to the shared scheduler utility."""
    return check_live(GAME_SCHEDULE, now)