import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGODB_URL"))
db = client["ai_automation"]

messages_collection = db["messages"]
leads_collection = db["leads"]
invoices_collection = db["invoices"]

def test_connection():
    try:
        client.admin.command("ping")
        return True
    except Exception as e:
        print(f"DB Error: {e}")
        return False