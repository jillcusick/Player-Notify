import requests
import os
import json
import re
from dotenv import load_dotenv
from src.milb.config import TARGET_PLAYER

load_dotenv()  # Load environment variables

def send_push(message: str) -> None:
    """Send a push notification using the Pushover API."""
    pushover_token = os.getenv("PUSHOVER_TOKEN")
    pushover_user = os.getenv("PUSHOVER_USER")

    if not pushover_token or not pushover_user:
        raise ValueError("Missing Pushover credentials. Check PUSHOVER_TOKEN and PUSHOVER_USER.")

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

def run_milb_tracker(game_id: str | None = None):
    """Fetches live MLB/MiLB game data, parses pitching changes, and sends notifications."""
    if not game_id:
        print("Error: A valid game_id is required for the MiLB tracker.")
        return

    print(f"[*] Polling MiLB live data for Game ID: {game_id}")

    # MLB/MiLB Stats API live feed endpoint
    mlb_api_url = f"https://statsapi.mlb.com/api/v1.1/game/{game_id}/feed/live"

    # get in-game data from MLB API for game of interest
    try:
        response = requests.get(mlb_api_url, timeout=15)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Error fetching game data for ID {game_id}: {e}")
        return

#### PARSE PLAYS FOR PITCHING CHANGES ####
    pitching_changes = []

    live_data = data.get("liveData", {})
    plays = live_data.get("plays", {})
    all_plays = plays.get("allPlays", [])

    # Extract incoming and outgoing pitchers
    pattern = re.compile(r"Pitching Change:\s*(.*?)\s+replaces\s+(.*?)\.", re.IGNORECASE)

    for play in all_plays:
        about = play.get("about", {})
        
        # Collect all candidate descriptions from both top-level and nested playEvents
        candidate_events = []
        
        # 1. Check top-level result description
        result = play.get("result", {})
        if "pitching substitution" in result.get("eventType", "").lower() or "pitching change" in result.get("description", "").lower():
            candidate_events.append(result.get("description", ""))

        # 2. Check nested playEvents for any pitching change events
        
        # loops through all play events
        for event in play.get("playEvents", []):
            
            # pulls play event information
            event_details = event.get("details", {})
            desc = event_details.get("description", "")
            ev_type = event_details.get("eventType", "")
            
            # Restrict to play events that are pitching changes/substitutions
            if "pitching" in ev_type.lower() or "pitching change" in desc.lower() or "pitching substitution" in ev_type.lower():
                if desc and desc not in candidate_events:
                    candidate_events.append(desc)

        # Process any found pitching change descriptions
        for description in candidate_events:
            match = pattern.search(description)
            
            incoming_pitcher = match.group(1).strip() if match else ""
            outgoing_pitcher = match.group(2).strip() if match else ""

            # If TARGET_PLAYER is set, check if they are the incoming pitcher
            player_match = True
            if TARGET_PLAYER:
                # If regex didn't parse incoming_pitcher but TARGET_PLAYER is specified, 
                # fallback to checking the full description string
                if incoming_pitcher:
                    player_match = TARGET_PLAYER.lower() in incoming_pitcher.lower()
                else:
                    player_match = TARGET_PLAYER.lower() in description.lower()

            if player_match:
                pitching_changes.append({
                    "inning": about.get("inning"),
                    "half_inning": about.get("halfInning", "").capitalize(),
                    "description": description,
                    "incoming": incoming_pitcher,
                    "outgoing": outgoing_pitcher,
                    "play_id": about.get("atBatIndex")
                })

    if not pitching_changes:
        print(f"[-] No matching pitching changes found for target criteria in game {game_id}.")
        return

    #### IDENTIFY NEW CHANGES SINCE LAST RUN ####
    seen_file = f"seen_milb_subs_{game_id}.json"
    event_track_file = "last_milb_event.json"

    # Reset tracking if it's a new game
    if os.path.exists(event_track_file):
        try:
            with open(event_track_file, "r") as f:
                last_game = json.load(f).get("event_id")
            if last_game != game_id and os.path.exists(seen_file):
                os.remove(seen_file)
        except Exception:
            pass

    with open(event_track_file, "w") as f:
        json.dump({"event_id": game_id}, f)

    # Load previously seen play IDs
    if os.path.exists(seen_file):
        with open(seen_file, "r") as f:
            seen = set(json.load(f))
    else:
        seen = set()

    # Filter out subs already notified about
    new_changes = [c for c in pitching_changes if str(c["play_id"]) not in seen]

    #### SEND PUSH NOTIFICATIONS ####
    for change in new_changes:
        message_body = (
            f"{change['description']} "
            f"({change['half_inning']} {change['inning']})"
        )
        print(f"[*] Sending alert: {message_body}")
        
        try:
            send_push(message_body)
            seen.add(str(change["play_id"]))
        except Exception as e:
            print(f"[!] Failed to send push notification: {e}")

    # Save updated history
    with open(seen_file, "w") as f:
        json.dump(list(seen), f)