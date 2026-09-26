from datetime import datetime, timedelta
import os
import sys

from airflow import DAG
from airflow.operators.python import PythonOperator

# Import schedule checkers and runners from modular src folders
from src.ncaabb.config import get_live_games as get_live_ncaabb_games
from src.ncaabb.runner import run_espn_ncaabb

from src.milb.config import get_live_games as get_live_milb_games
from src.milb.runner import run_milb_tracker


def run_all_live_trackers(**kwargs):
    """Checks NCAABB and MiLB game schedules, tracking any games currently live."""
    now = kwargs["logical_date"]
    
    # Check and run live NCAABB games
    live_ncaabb = get_live_ncaabb_games(now)
    if live_ncaabb:
        for game in live_ncaabb:
            event_id = game["event_id"]
            print(f"[NCAABB] Running for live game ID: {event_id}")
            run_espn_ncaabb(event_id=event_id)
    else:
        print("[NCAABB] No live games found.")

    # Check and run live MiLB games
    live_milb = get_live_milb_games(now)
    if live_milb:
        for game in live_milb:
            game_id = game["event_id"]
            teams = game.get("teams", "Unknown Matchup")
            print(f"[MiLB] Running for live game ID: {game_id} ({teams})")
            run_milb_tracker(game_id=game_id)
    else:
        print("[MiLB] No live games found.")


default_args = {
    "owner": "airflow",
    "retries": 0,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    dag_id="games_tracker",
    default_args=default_args,
    start_date=datetime(2025, 1, 1),
    schedule_interval="*/2 * * * *",  # runs every 2 minutes
    catchup=False,
) as dag:

    poll_games = PythonOperator(
        task_id="track_all_games_if_live",
        python_callable=run_all_live_trackers,
    )