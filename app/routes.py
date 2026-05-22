from fastapi import APIRouter
from app.database import test_connection, messages_collection, leads_collection
from app.llm import classify_message, generate_reply, enrich_lead
from app.schemas import IncomingMessage
from datetime import datetime

router = APIRouter(prefix="/api", tags=["automation"])


@router.get("/health")
def health_check():
    # check server and database status
    db_status = test_connection()
    return {
        "status": "ok",
        "database": "connected" if db_status else "failed"
    }


@router.post("/webhook")
def handle_message(payload: IncomingMessage):
    # classify incoming message using LLM
    classification = classify_message(payload.sender, payload.message)

    # save every message to MongoDB
    record = {
        "sender": payload.sender,
        "channel": payload.channel,
        "message": payload.message,
        "intent": classification["intent"],
        "summary": classification["summary"],
        "urgency": classification["urgency"],
        "name": classification["name"],
        "email": classification["email"],
        "company": classification["company"],
        "created_at": datetime.utcnow()
    }
    messages_collection.insert_one(record)

    # if lead, scrape company website and save to leads collection
    enrichment = None
    if classification["intent"] == "lead":
        company = classification["company"]
        enrichment = enrich_lead(company) if company else "No company provided"

        lead = {
            "name": classification["name"],
            "email": classification["email"],
            "company": company,
            "company_summary": enrichment,
            "source": payload.channel,
            "summary": classification["summary"],
            "sender": payload.sender,
            "created_at": datetime.utcnow()
        }
        leads_collection.insert_one(lead)

    # generate auto reply based on intent
    reply = generate_reply(classification, payload.channel)

    return {
        "status": "processed",
        "classification": classification,
        "auto_reply": reply,
        "company_summary": enrichment
    }