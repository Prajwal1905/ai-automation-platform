import os
import requests
from dotenv import load_dotenv

load_dotenv()

HUBSPOT_API_KEY = os.getenv("HUBSPOT_API_KEY")

def create_hubspot_contact(name: str, email: str, company: str, summary: str):
    # only create contact if we have at least a name or email
    if not name and not email:
        return None

    url = "https://api.hubapi.com/crm/v3/objects/contacts"
    headers = {
        "Authorization": f"Bearer {HUBSPOT_API_KEY}",
        "Content-Type": "application/json"
    }

    # split name into first and last
    parts = (name or "").split(" ", 1)
    first_name = parts[0]
    last_name = parts[1] if len(parts) > 1 else ""

    payload = {
        "properties": {
            "firstname": first_name,
            "lastname": last_name,
            "email": email or "",
            "company": company or "",
            
        }
    }

    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 201:
        return response.json().get("id")
    else:
        print(f"HubSpot error: {response.status_code} - {response.text}")
        return None