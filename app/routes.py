from fastapi import APIRouter, UploadFile, File, Form, Depends
from fastapi.responses import Response
from app.database import test_connection, messages_collection, leads_collection, get_db
from app.llm import classify_message, generate_reply, enrich_lead
from app.schemas import IncomingMessage
from app.models import Lead, Invoice
from datetime import datetime
from sqlalchemy.orm import Session
from app.notifications import send_slack_alert
from app.crm import create_hubspot_contact

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
    messages_collection.insert_one({
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
    })

    # if lead, save to both MongoDB and PostgreSQL
    enrichment = None
    if classification["intent"] == "lead":
        company = classification["company"]
        enrichment = enrich_lead(company) if company else "No company provided"

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

        # create contact in HubSpot CRM
        create_hubspot_contact(
            name=classification["name"],
            email=classification["email"],
            company=company,
            summary=enrichment
        )

    # generate auto reply
    reply = generate_reply(classification, payload.channel)
    
    send_slack_alert(classification, payload.sender, payload.channel)

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


@router.post("/twilio/webhook")
async def twilio_webhook(
    From: str = Form(...),
    Body: str = Form(...),
    db: Session = Depends(get_db)
):
    # Twilio sends WhatsApp messages as form data
    # From = sender's WhatsApp number, Body = message text
    classification = classify_message(From, Body)

    # save to MongoDB
    messages_collection.insert_one({
        "sender": From,
        "channel": "whatsapp",
        "message": Body,
        "intent": classification["intent"],
        "summary": classification["summary"],
        "urgency": classification["urgency"],
        "name": classification["name"],
        "email": classification["email"],
        "company": classification["company"],
        "created_at": datetime.utcnow()
    })

    # if lead save to PostgreSQL
    if classification["intent"] == "lead":
        company = classification["company"]
        enrichment = enrich_lead(company) if company else "No company provided"

        leads_collection.insert_one({
            "name": classification["name"],
            "email": classification["email"],
            "company": company,
            "company_summary": enrichment,
            "source": "whatsapp",
            "sender": From,
            "created_at": datetime.utcnow()
        })

        lead = Lead(
            name=classification["name"],
            email=classification["email"],
            company=company,
            company_summary=enrichment,
            source="whatsapp",
            sender=From
        )
        db.add(lead)
        db.commit()

        # create contact in HubSpot CRM
        create_hubspot_contact(
            name=classification["name"],
            email=classification["email"],
            company=company,
            summary=enrichment
        )

    # generate reply and return in TwiML format so Twilio sends it back on WhatsApp
    reply = generate_reply(classification, "whatsapp")
    send_slack_alert(classification, From, "whatsapp")
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{reply}</Message>
</Response>"""

    return Response(content=twiml, media_type="application/xml")

@router.get("/messages")
def get_messages():
    # fetch last 50 messages from MongoDB
    messages = list(messages_collection.find(
        {}, {"_id": 0}
    ).sort("created_at", -1).limit(50))
    return {"messages": messages}

@router.get("/leads")
def get_leads(db: Session = Depends(get_db)):
    # fetch all leads from PostgreSQL
    leads = db.query(Lead).order_by(Lead.created_at.desc()).all()
    return {"leads": [
        {
            "id": l.id,
            "name": l.name,
            "company": l.company,
            "email": l.email,
            "source": l.source,
            "summary": l.summary,
            "created_at": str(l.created_at)
        } for l in leads
    ]}

@router.get("/invoices")
def get_invoices(db: Session = Depends(get_db)):
    # fetch all invoices from PostgreSQL
    invoices = db.query(Invoice).order_by(Invoice.created_at.desc()).all()
    return {"invoices": [
        {
            "id": i.id,
            "sender": i.sender,
            "vendor": i.vendor,
            "amount": i.amount,
            "due_date": i.due_date,
            "invoice_number": i.invoice_number,
            "created_at": str(i.created_at)
        } for i in invoices
    ]}

@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    # summary numbers for the dashboard header
    total_messages = messages_collection.count_documents({})
    total_leads = db.query(Lead).count()
    total_invoices = db.query(Invoice).count()
    high_urgency = messages_collection.count_documents({"urgency": "high"})
    
    return {
        "total_messages": total_messages,
        "total_leads": total_leads,
        "total_invoices": total_invoices,
        "high_urgency": high_urgency
    }