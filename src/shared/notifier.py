# src/common/notifier.py
import os
import requests

def send_push(message: str) -> None:
    """Send a push notification using the Pushover API."""
    pushover_token = os.getenv("PUSHOVER_TOKEN")
    pushover_user = os.getenv("PUSHOVER_USER")

    if not pushover_token or not pushover_user:
        raise ValueError("Missing Pushover credentials. Check PUSHOVER_TOKEN and PUSHOVER_USER in your .env file.")

    response = requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": pushover_token,
            "user": pushover_user,
            "message": message
        },
        timeout=10
    )
    response.raise_for_status()