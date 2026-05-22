import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def classify_message(sender: str, message: str) -> dict:
    prompt = f"""
    You are a business assistant. Analyze the following message and extract structured information.

    Message from {sender}:
    "{message}"

    Respond in this exact JSON format, nothing else:
    {{
        "intent": "lead" | "support" | "invoice" | "other",
        "summary": "one line summary of what the person wants",
        "name": "extracted name or null",
        "email": "extracted email or null",
        "company": "extracted company name or null",
        "urgency": "low" | "medium" | "high"
    }}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a business message classifier. Always respond in valid JSON only."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    result = response.choices[0].message.content.strip()
    return json.loads(result)


def generate_reply(classification: dict, channel: str) -> str:
    intent = classification["intent"]
    name = classification["name"] or "there"
    company = classification["company"] or ""

    prompt = f"""
    Generate a short, professional, friendly reply for a {channel} message.
    
    Intent: {intent}
    Person's name: {name}
    Company: {company}
    Summary: {classification["summary"]}
    Urgency: {classification["urgency"]}

    Rules:
    - Keep it under 3 sentences
    - Sound human, not robotic
    - If lead: express interest and suggest a call
    - If support: acknowledge the issue and assure quick help
    - If invoice: confirm receipt and mention payment processing
    - If other: give a polite generic response
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful business assistant writing short replies."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    return response.choices[0].message.content.strip()