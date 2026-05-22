import os
from pypdf import PdfReader
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from openai import OpenAI
from dotenv import load_dotenv
import uuid

load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
qdrant = QdrantClient(url=os.getenv("QDRANT_URL"))

COLLECTION_NAME = "invoices"

def create_collection_if_not_exists():
    # create qdrant collection if it doesn't exist yet
    existing = [c.name for c in qdrant.get_collections().collections]
    if COLLECTION_NAME not in existing:
        qdrant.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
        )

def extract_text_from_pdf(file_bytes: bytes) -> str:
    # read pdf and extract all text
    import io
    reader = PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def embed_text(text: str) -> list:
    # convert text to vector embedding using OpenAI
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

def store_invoice(file_bytes: bytes, sender: str) -> dict:
    # extract text from pdf
    raw_text = extract_text_from_pdf(file_bytes)

    if not raw_text.strip():
        return {"error": "Could not extract text from PDF"}

    # embed and store in qdrant
    create_collection_if_not_exists()
    embedding = embed_text(raw_text[:2000])

    point_id = str(uuid.uuid4())
    qdrant.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(
                id=point_id,
                vector=embedding,
                payload={"sender": sender, "text": raw_text[:2000]}
            )
        ]
    )

    # extract key fields using LLM
    extracted = extract_invoice_fields(raw_text)
    return {"point_id": point_id, "extracted": extracted, "raw_text": raw_text[:500]}

def extract_invoice_fields(text: str) -> dict:
    # ask LLM to pull out the important invoice fields
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Extract invoice fields and return only valid JSON."},
            {"role": "user", "content": f"""
            Extract these fields from the invoice text below:
            {{
                "vendor": "company name or null",
                "amount": "total amount or null",
                "due_date": "due date or null",
                "invoice_number": "invoice number or null",
                "description": "what the invoice is for or null"
            }}

            Invoice text:
            {text[:1500]}
            """}
        ],
        temperature=0
    )
    import json
    result = response.choices[0].message.content.strip()
    return json.loads(result)