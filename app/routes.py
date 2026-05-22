from fastapi import APIRouter
from app.database import test_connection, messages_collection, leads_collection
from app.llm import classify_message, generate_reply
from app.schemas import IncomingMessage
from datetime import datetime

router = APIRouter(prefix="/api", tags=["automation"])

@router.get("/health")
def health_check():
    db_status = test_connection()
    return {
        "status": "ok",
        "database": "connected" if db_status else "failed"
    }

@router.post("/webhook")
def handle_message(payload: IncomingMessage):
    classification = classify_message(payload.sender, payload.message)

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

    if classification["intent"] == "lead":
        lead = {
            "name": classification["name"],
            "email": classification["email"],
            "company": classification["company"],
            "source": payload.channel,
            "summary": classification["summary"],
            "sender": payload.sender,
            "created_at": datetime.utcnow()
        }
        leads_collection.insert_one(lead)

    reply = generate_reply(classification, payload.channel)

    return {
        "status": "processed",
        "classification": classification,
        "auto_reply": reply
    }