from app.database import messages_collection, leads_collection, get_db
from app.llm import enrich_lead
from app.models import Lead
from app.crm import create_hubspot_contact
from app.notifications import send_slack_alert
from datetime import datetime
from twilio.rest import Client
import os

def save_message(sender: str, channel: str, message: str, classification: dict):
    # save every incoming message to MongoDB
    messages_collection.insert_one({
        "sender": sender,
        "channel": channel,
        "message": message,
        "intent": classification["intent"],
        "summary": classification["summary"],
        "urgency": classification["urgency"],
        "name": classification["name"],
        "email": classification["email"],
        "company": classification["company"],
        "created_at": datetime.utcnow()
    })


def process_lead(sender: str, channel: str, classification: dict, db):
    # enrich, save and sync lead to CRM
    company = classification["company"]
    enrichment = enrich_lead(company) if company else "No company provided"

    # save to MongoDB
    leads_collection.insert_one({
        "name": classification["name"],
        "email": classification["email"],
        "company": company,
        "company_summary": enrichment,
        "source": channel,
        "summary": classification["summary"],
        "sender": sender,
        "created_at": datetime.utcnow()
    })

    # save to PostgreSQL
    lead = Lead(
        name=classification["name"],
        email=classification["email"],
        company=company,
        company_summary=enrichment,
        source=channel,
        summary=classification["summary"],
        sender=sender
    )
    db.add(lead)
    db.commit()

    # sync to HubSpot
    create_hubspot_contact(
        name=classification["name"],
        email=classification["email"],
        company=company,
        summary=enrichment
    )

    return enrichment

def send_whatsapp_reply(to: str, message: str):
    try:
        # clean the number - remove whatsapp: prefix if present
        clean_to = to.replace("whatsapp:", "")
        print(f"Attempting Twilio reply to {clean_to}")
        client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"),
            os.getenv("TWILIO_AUTH_TOKEN")
        )
        msg = client.messages.create(
            from_="whatsapp:+14155238886",
            to=f"whatsapp:{clean_to}",
            body=message
        )
        print(f"Twilio reply sent: {msg.sid}")
    except Exception as e:
        print(f"Twilio reply error: {str(e)}")