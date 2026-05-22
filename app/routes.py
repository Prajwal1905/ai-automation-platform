from fastapi import APIRouter, UploadFile, File
from app.database import test_connection, messages_collection, leads_collection, get_db
from app.llm import classify_message, generate_reply, enrich_lead
from app.schemas import IncomingMessage
from app.models import Lead, Invoice
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import Depends

router = APIRouter(prefix="/api", tags=["automation"])

@router.get("/health")
def health_check():
    db_status = test_connection()
    return {"status": "ok", "databases": db_status}

@router.post("/webhook")
def handle_message(payload: IncomingMessage, db: Session = Depends(get_db)):
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

    # if lead, save to both MongoDB and PostgreSQL
    enrichment = None
    if classification["intent"] == "lead":
        company = classification["company"]
        enrichment = enrich_lead(company) if company else "No company provided"

        # save to MongoDB
        leads_collection.insert_one({
            "name": classification["name"],
            "email": classification["email"],
            "company": company,
            "company_summary": enrichment,
            "source": payload.channel,
            "summary": classification["summary"],
            "sender": payload.sender,
            "created_at": datetime.utcnow()
        })

        # save to PostgreSQL
        lead = Lead(
            name=classification["name"],
            email=classification["email"],
            company=company,
            company_summary=enrichment,
            source=payload.channel,
            summary=classification["summary"],
            sender=payload.sender
        )
        db.add(lead)
        db.commit()

    # generate auto reply
    reply = generate_reply(classification, payload.channel)

    return {
        "status": "processed",
        "classification": classification,
        "auto_reply": reply,
        "company_summary": enrichment
    }


@router.post("/invoice")
async def process_invoice(sender: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    from app.rag import store_invoice
    file_bytes = await file.read()
    result = store_invoice(file_bytes, sender)

    # save to PostgreSQL
    invoice = Invoice(
        sender=sender,
        vendor=result["extracted"].get("vendor"),
        amount=result["extracted"].get("amount"),
        due_date=result["extracted"].get("due_date"),
        invoice_number=result["extracted"].get("invoice_number"),
        description=result["extracted"].get("description")
    )
    db.add(invoice)
    db.commit()

    return {
        "status": "processed",
        "sender": sender,
        "extracted_fields": result["extracted"],
        "stored_in_qdrant": True,
        "stored_in_postgresql": True
    }