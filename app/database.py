import os
from pymongo import MongoClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# MongoDB setup
mongo_client = MongoClient(os.getenv("MONGODB_URL"))
mongo_db = mongo_client["ai_automation"]
messages_collection = mongo_db["messages"]
leads_collection = mongo_db["leads"]
invoices_collection = mongo_db["invoices"]

# PostgreSQL setup
POSTGRES_URL = os.getenv("POSTGRES_URL")
engine = create_engine(POSTGRES_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection():
    try:
        mongo_client.admin.command("ping")
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"mongodb": "connected", "postgresql": "connected"}
    except Exception as e:
        return {"error": str(e)}