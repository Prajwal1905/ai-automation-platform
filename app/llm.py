import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from app.scraper import scrape_company_website, summarize_company

load_dotenv()

# two model configs: deterministic for classification, creative for replies
llm_strict = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_creative = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)


def classify_message(sender: str, message: str) -> dict:
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a business message classifier. Always respond in valid JSON only."),
        ("user", """Analyze this message from {sender}: "{message}"

Respond in this exact JSON format, nothing else:
{{"intent": "lead" | "support" | "invoice" | "other",
  "summary": "one line summary of what the person wants",
  "name": "extracted name or null",
  "email": "extracted email or null",
  "company": "extracted company name or null",
  "urgency": "low" | "medium" | "high"}}""")
    ])

    chain = prompt | llm_strict | JsonOutputParser()
    return chain.invoke({"sender": sender, "message": message})


def generate_reply(classification: dict, channel: str) -> str:
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful business assistant writing short replies."),
        ("user", """Generate a short, professional, friendly reply for a {channel} message.

Intent: {intent}
Person's name: {name}
Company: {company}
Summary: {summary}
Urgency: {urgency}

Rules:
- Keep it under 3 sentences
- Sound human, not robotic
- If lead: express interest and suggest a call
- If support: acknowledge the issue and assure quick help
- If invoice: confirm receipt and mention payment processing
- If other: give a polite generic response""")
    ])

    chain = prompt | llm_creative | StrOutputParser()
    return chain.invoke({
        "channel": channel,
        "intent": classification["intent"],
        "name": classification["name"] or "there",
        "company": classification["company"] or "",
        "summary": classification["summary"],
        "urgency": classification["urgency"]
    })

def enrich_lead(company_name: str) -> str:
    scraped = scrape_company_website(company_name)
    return summarize_company(company_name, scraped)