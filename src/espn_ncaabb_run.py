import requests 
import os 
from dotenv import load_dotenv 
import pandas as pd
import json

load_dotenv() # load .env file when runs 

# define teams of interest
teams = ["UConn", "Northwestern", "UCLA"] # add/remove teams anytime 
# players = # **if limiting to certain players, also update line 73**

def run_espn_ncaabb(event_id: str | None = None):

    #### SET UP PUSH NOTIFICATIONS ####

    # get pushover app token and user from environment file 
    PUSHOVER_TOKEN = os.getenv("PUSHOVER_TOKEN")
    PUSHOVER_USER = os.getenv("PUSHOVER_USER")

    # define function to send push notifications using Pushover app 
    def send_push(message: str) -> None:
        """Send a push notification using the Pushover API."""
        if not PUSHOVER_TOKEN or not PUSHOVER_USER:
            raise ValueError("Missing Pushover credentials. Check PUSHOVER_TOKEN and PUSHOVER_USER.")

        response = requests.post(
            "https://api.pushover.net/1/messages.json",
            data={
                "token": PUSHOVER_TOKEN,
                "user": PUSHOVER_USER,
                "message": message
            },
            timeout=10
        )
        # Optional: raise an error if the request failed
        response.raise_for_status()

    #### GET DATA ####

    # get in-game play-by-play data from ESPN for game based on game id 

    # pull event id into API URL
    espn_api_url = (
        "https://site.web.api.espn.com/apis/site/v2/sports/"
        "basketball/womens-college-basketball/summary"
    )

    params = {
        "region": "us",
        "lang": "en",
        "contentorigin": "espn",
        "event": event_id,
    }

    # get data and format as json 
    response = requests.get(espn_api_url, params=params)
    data = response.json()

    #### FIND PLAYER SUBSTITUTIONS DURING GAME ####

    sub_in = []

    # get plays data 
    plays = data.get("plays", [])

    # for each play, extract any player substitution data
    for play in plays:
        play_type = play.get("type", {}).get("text", "")
        description = play.get("text", "")
        
        if (
        play_type == "Substitution"
        and "subbing in" in description.lower()
        and any(t.lower() in description.lower() for t in teams)
        ): #can add players in addition to team if want to limit to certain player(s)

            sub_in.append({
                "period": play.get("period", {}).get("displayValue"),
                "clock": play.get("clock", {}).get("displayValue"),
                "team_id": play.get("team", {}).get("id"),
                "description": play.get("text"),
                "athlete_ids": [p["athlete"]["id"] for p in play.get("participants", [])],
                "sequenceNumber": play.get("sequenceNumber")
            })

    # Print results
    for sub in sub_in:
        print(sub)

    # create data frame of substitutions 

    subs = pd.DataFrame(sub_in)
    subs.head(10)

    #### IDENTIFY NEW SUBS SINCE LAST RUN ####

    # load existing substitutions
    SEEN_FILE = "seen_subs.json"
    EVENT_TRACK_FILE = "last_event.json" # track last event

    # first time event is tracked
    if not os.path.exists(EVENT_TRACK_FILE):
        with open(EVENT_TRACK_FILE, 'w') as f:
            json.dump({"event_id": event_id}, f)
        return set()
    
    # load last event id once prior events have been tracked
    with open(EVENT_TRACK_FILE, "r") as f:
        last = json.load(f).get("event_id")

    # if new event, delete old substitutions to reset
    if last != event_id: 
        if os.path.exists(SEEN_FILE):
            os.remove(SEEN_FILE)
        with open(EVENT_TRACK_FILE, "w") as f:
            json.dump({"event_id": event_id}, f)
        return set() 
    
    # load existing subs file (whether new or continuing for same event)
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            seen = set(json.load(f))
    else:
        seen = set()

    # identify new subbed players 
    new_subs = [s for s in sub_in if s["sequenceNumber"] not in seen]
    print(new_subs)

    #### SEND PUSH NOTIFICATIONS ####

    # send text about any new subs 
    for sub in new_subs:
        message_body = (
            f"NEW SUB: {sub['description']} "
            f"({sub['period']} @ {sub['clock']})"
        )

        send_push(message_body)

    # update list of subs to avoid duplicate notifications
    for sub in new_subs:
        seen.add(sub["sequenceNumber"])

    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)




