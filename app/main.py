from fastapi import FastAPI
from app.routes import router

app = FastAPI(
    title="AI Automation Platform",
    description="Automates WhatsApp, email, and document processing using AI",
    version="1.0.0"
)

app.include_router(router)

@app.get("/")
def root():
    return {"status": "running", "message": "AI Automation Platform is live"}