from sqlalchemy import Column, Integer, String, Text, Float, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    company = Column(String)
    company_summary = Column(Text)
    source = Column(String)
    sender = Column(String)
    summary = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    sender = Column(String)
    vendor = Column(String)
    amount = Column(String)
    due_date = Column(String)
    invoice_number = Column(String)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())