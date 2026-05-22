from fastapi import FastAPI
from app.routes import router
from app.database import engine, test_connection
from app import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Automation Platform",
    description="Automates WhatsApp, email, and document processing using AI",
    version="1.0.0"
)

app.include_router(router)

@app.get("/")
def root():
    db_status = test_connection()
    return {"status": "running", "databases": db_status}