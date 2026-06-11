# AI Automation Platform

A production-grade business automation platform that processes incoming WhatsApp and email messages using AI — classifying intent, enriching leads, extracting invoice data, and syncing everything to a CRM automatically.

Built to demonstrate real-world agentic AI and automation capabilities using the same stack enterprises use.

---

## 🎥 Demo

<!-- Drag and drop your demo video here in the GitHub editor, or replace with your link -->
[Watch the demo](https://drive.google.com/file/d/1vte-3BrAvF8mpg_NU0iwg6GjNdpHyVGZ/view?usp=sharing) — one WhatsApp message triggers AI classification, lead enrichment, CRM sync, Slack alert, and an auto-reply. Invoice PDFs emailed to the business inbox are processed automatically via a Gmail n8n workflow and RAG pipeline — with zero human involvement.

---

## What it does

A customer sends a WhatsApp message. Within seconds:

- The message is classified by GPT via a LangChain pipeline (lead, support, invoice, or other)
- If it's a lead, the company is researched via web scraping and a profile is built
- If it's an invoice PDF, key fields are extracted using a RAG pipeline
- If it's an email with a PDF attachment, n8n detects it via Gmail polling, downloads the attachment, and routes it through the RAG pipeline automatically
- A human-sounding reply is sent back automatically
- The sales team is notified on Slack
- A contact is created in HubSpot CRM
- Everything is saved to MongoDB and PostgreSQL
- The live dashboard updates in real time

Zero human involvement.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI |
| AI / LLM | OpenAI GPT-4o-mini, LangChain (LCEL chains) |
| RAG Pipeline | Qdrant, OpenAI Embeddings |
| Workflow Automation | n8n |
| WhatsApp Integration | Twilio |
| Notifications | Slack Webhooks |
| CRM | HubSpot |
| Databases | MongoDB, PostgreSQL |
| Frontend | React, Vite |
| DevOps | Docker, Docker Compose |

---

## Architecture

```text
WhatsApp /Email
        ↓
n8n (workflow orchestration)
        ↓
FastAPI Backend
        ↓
┌──────────────────────────────────┐
│ LangChain LCEL Pipelines:        │
│  • Classifier (JsonOutputParser) │
│  • Reply Generator               │
│  • Company Summarizer            │
│  • Invoice Extractor             │
│ Lead Enrichment (web scraper)    │
│ Invoice RAG (Qdrant embeddings)  │
└──────────────────────────────────┘
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

## How the AI layer works

All LLM interactions run through **LangChain LCEL chains** (`prompt | model | parser`):

- **Classification** — `ChatPromptTemplate → ChatOpenAI (temperature=0) → JsonOutputParser`. Deterministic, structured output: intent, summary, name, email, company, urgency.
- **Auto-replies** — same pattern with `temperature=0.7` and `StrOutputParser` for natural, varied responses.
- **Invoice extraction** — PDF text → OpenAI embedding (1536-dim) stored in Qdrant (cosine similarity) → LCEL chain extracts vendor, amount, due date, and invoice number as JSON.
- **Lead enrichment** — DuckDuckGo search + BeautifulSoup scraping → LCEL summarization chain. Falls back to the LLM's own knowledge when scraping is blocked.

---

## Project Structure

```text
ai-automation-platform/
├── app/
│   ├── main.py          # FastAPI app entry point
│   ├── routes.py        # API endpoints
│   ├── llm.py           # LangChain classification and reply chains
│   ├── rag.py           # Invoice RAG pipeline (Qdrant + extraction chain)
│   ├── scraper.py       # Company website scraper + summarization chain
│   ├── crm.py           # HubSpot CRM integration
│   ├── notifications.py # Slack alerts
│   ├── helpers.py       # Message saving and lead processing
│   ├── database.py      # MongoDB and PostgreSQL connections
│   ├── models.py        # PostgreSQL table definitions
│   └── schemas.py       # Pydantic request schemas
├── frontend/            # React dashboard
├── docker-compose.yml
├── Dockerfile
└── .env
```

---

## Setup

### Prerequisites

- Python 3.9+
- Docker Desktop
- Node.js 18+

### Backend

```bash
# create and activate virtual environment
python -m venv venv
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

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Environment Variables

```env
MONGODB_URL=mongodb://localhost:27017
POSTGRES_URL=postgresql://postgres:password@localhost:5432/ai_automation
OPENAI_API_KEY=your_openai_key_here
QDRANT_URL=http://localhost:6333
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
SLACK_WEBHOOK_URL=your_slack_webhook
HUBSPOT_API_KEY=your_hubspot_private_app_token
```

---

## API Endpoints

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

Interactive API docs available at `http://localhost:8001/docs` (Swagger UI).

---

## Example: end-to-end lead flow

Request:

```json
POST /api/webhook
{
  "sender": "+919876543210",
  "channel": "whatsapp",
  "message": "Hi, I'm Rahul from Tata Motors. We're interested in your automation product. Can we schedule a demo?"
}
```

Result (seconds later):

- Classified as `lead` with extracted name, company, and urgency
- Company profile generated automatically
- Lead saved to MongoDB and PostgreSQL
- Contact created in HubSpot CRM
- Slack alert sent to the sales team
- Personalized reply returned to the sender

---

## Key Design Decisions

### LangChain LCEL for all LLM calls

Every LLM interaction is a composable chain: `prompt | model | parser`. `JsonOutputParser` makes structured extraction robust against malformed output (handles markdown fences and stray text better than raw `json.loads`), while `StrOutputParser` handles free-text replies. Two model configurations are used: `temperature=0` for deterministic extraction, `temperature=0.7` for natural-sounding replies.

### MongoDB for messages, PostgreSQL for leads and invoices

Messages are unstructured and written at high frequency, making MongoDB a natural fit. Leads and invoices are structured relational data that benefit from SQL queries and reporting.

### LLM fallback for company enrichment

When web scraping fails due to bot detection, the system falls back to the LLM's own knowledge about well-known companies. This ensures enrichment always returns useful data.

### TwiML response format

Twilio requires responses in XML (TwiML) format to send messages back on WhatsApp. The endpoint returns XML directly rather than JSON.

### n8n as the orchestration layer

Keeps the FastAPI backend stateless and focused on business logic. n8n handles the polling, scheduling, and routing between channels.

---

## Roadmap / Known Improvements

- [ ] Twilio request signature verification on the webhook
- [ ] Background task queue (Celery + Redis) so LLM processing doesn't block requests
- [ ] Idempotency on invoice uploads (unique constraint on invoice_number)
- [ ] Numeric amount column with currency parsing
- [ ] WebSocket-based live dashboard updates
- [ ] Retry + structured logging for Slack and HubSpot integration failures
