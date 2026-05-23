# AI Automation Platform

A production-grade business automation platform that processes incoming WhatsApp and email messages using AI — classifying intent, enriching leads, extracting invoice data, and syncing everything to a CRM automatically.

Built to demonstrate real-world agentic AI and automation capabilities using the same stack enterprises use.

---

# What it does

A customer sends a WhatsApp message. Within seconds:

- The message is classified by GPT (lead, support, invoice, or other)
- If it's a lead, the company is researched via web scraping and a profile is built
- If it's an invoice PDF, key fields are extracted using a RAG pipeline
- A human-sounding reply is sent back automatically
- The sales team is notified on Slack
- A contact is created in HubSpot CRM
- Everything is saved to MongoDB and PostgreSQL
- The live dashboard updates in real time

Zero human involvement.

---

# Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI |
| AI / LLM | OpenAI GPT-4o-mini, LangChain |
| RAG Pipeline | Qdrant, OpenAI Embeddings |
| Workflow Automation | n8n |
| WhatsApp Integration | Twilio |
| Notifications | Slack Webhooks |
| CRM | HubSpot |
| Databases | MongoDB, PostgreSQL |
| Frontend | React, Vite |
| DevOps | Docker, Docker Compose |

---

# Architecture

```text
WhatsApp / Email
        ↓
n8n (workflow orchestration)
        ↓
FastAPI Backend
        ↓
┌─────────────────────────────┐
│ LLM Classifier (GPT-4o)     │
│ Lead Enrichment (scraper)   │
│ Invoice RAG (Qdrant)        │
│ Auto Reply Generator        │
└─────────────────────────────┘
        ↓              ↓           ↓
     MongoDB       PostgreSQL    HubSpot
    (messages)    (leads,        (CRM)
                   invoices)
        ↓
    Slack Alert
        ↓
 React Dashboard
```

---

# Project Structure

```text
ai-automation-platform/
├── app/
│   ├── main.py          # FastAPI app entry point
│   ├── routes.py        # API endpoints
│   ├── llm.py           # LLM classifier and reply generator
│   ├── rag.py           # Invoice RAG pipeline
│   ├── scraper.py       # Company website scraper
│   ├── crm.py           # HubSpot CRM integration
│   ├── notifications.py # Slack alerts
│   ├── database.py      # MongoDB and PostgreSQL connections
│   ├── models.py        # PostgreSQL table definitions
│   └── schemas.py       # Pydantic request schemas
├── frontend/            # React dashboard
├── docker-compose.yml
├── Dockerfile
└── .env
```

---

# Setup

## Prerequisites

- Python 3.9+
- Docker Desktop
- Node.js 18+

---

# Backend Setup

```bash
# create virtual environment
python -m venv venv

# activate virtual environment
venv\Scripts\activate

# install dependencies
pip install -r requirements.txt

# configure environment
cp .env.example .env

# fill in your API keys inside .env

# start dependencies
docker start qdrant mongodb n8n

# run backend server
uvicorn app.main:app --reload --port 8001
```

---

# Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

---

# Environment Variables

```env
MONGODB_URL=mongodb://localhost:27017
POSTGRES_URL=postgresql://postgres:password@localhost:5432/ai_automation
OPENAI_API_KEY=
QDRANT_URL=http://localhost:6333
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
SLACK_WEBHOOK_URL=
HUBSPOT_API_KEY=
```

---

# API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | /api/webhook | Process incoming message (JSON) |
| POST | /api/twilio/webhook | Process WhatsApp via Twilio |
| POST | /api/invoice | Upload and process invoice PDF |
| GET | /api/messages | Fetch all messages |
| GET | /api/leads | Fetch all leads |
| GET | /api/invoices | Fetch all invoices |
| GET | /api/stats | Dashboard summary stats |
| GET | /api/health | Health check |

---

# Key Design Decisions

### MongoDB for messages, PostgreSQL for leads and invoices

Messages are unstructured and written at high frequency, making MongoDB a natural fit. Leads and invoices are structured relational data that benefit from SQL queries and foreign key constraints.

### LLM fallback for company enrichment

When web scraping fails due to bot detection, the system falls back to the LLM's own knowledge about well-known companies. This ensures enrichment always returns useful data.

### TwiML response format

Twilio requires responses in XML (TwiML) format to send messages back on WhatsApp. The endpoint returns XML directly rather than JSON.

### n8n as the orchestration layer

Keeps the FastAPI backend stateless and focused on business logic. n8n handles the polling, scheduling, and routing between channels.

---

# .env.example

```env
MONGODB_URL=mongodb://localhost:27017
POSTGRES_URL=postgresql://postgres:password@localhost:5432/ai_automation
OPENAI_API_KEY=your_openai_key_here
QDRANT_URL=http://localhost:6333
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
SLACK_WEBHOOK_URL=your_slack_webhook
HUBSPOT_API_KEY=your_hubspot_key
```