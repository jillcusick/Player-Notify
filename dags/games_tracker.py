from datetime import datetime, timedelta
import os
import sys

from airflow import DAG
from airflow.operators.python import PythonOperator

# Ensure src is importable inside the container
repo_path = os.path.dirname(os.path.dirname(__file__))
if repo_path not in sys.path:
    sys.path.append(repo_path)

from src.game_schedule import get_live_games
from src.espn_ncaabb_run import run_espn_ncaabb


def run_if_game_live(**kwargs): 
    now = kwargs["logical_date"]
    live_games = get_live_games(now)

    if not live_games:
        print("No live games, skipping ESPN run.")
        return

    for game in live_games:
        event_id = game["event_id"]
        print(f"Running for live game: {event_id}")
        run_espn_ncaabb(event_id=event_id)


default_args = {
    "owner": "airflow",
    "retries": 0,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    dag_id="games_tracker",
    default_args=default_args,
    start_date=datetime(2025, 1, 1),
    schedule_interval="*/2 * * * *",  # every 2 minutes
    catchup=False,
) as dag:

    poll_games = PythonOperator(
    task_id="track_games_if_live",
    python_callable=run_if_game_live,
    )
