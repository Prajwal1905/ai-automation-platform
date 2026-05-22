import os
import requests
from dotenv import load_dotenv

load_dotenv()

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def send_slack_alert(classification: dict, sender: str, channel: str):
    # only notify for leads or high urgency messages
    if classification["urgency"] != "high" and classification["intent"] != "lead":
        return

    intent = classification["intent"]
    name = classification["name"] or "Unknown"
    company = classification["company"] or "Unknown"
    urgency = classification["urgency"]
    summary = classification["summary"]

    message = (
        f"*New {intent} from {name} ({company})*\n"
        f"Channel: {channel} | Urgency: {urgency}\n"
        f"Summary: {summary}\n"
        f"Sender: {sender}"
    )

    requests.post(SLACK_WEBHOOK_URL, json={"text": message})