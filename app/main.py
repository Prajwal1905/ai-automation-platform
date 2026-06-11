from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router
from app.database import engine, test_connection
from app import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Automation Platform",
    description="Automates WhatsApp, email, and document processing using AI",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def root():
    db_status = test_connection()
    return {"status": "running", "databases": db_status}