from sqlalchemy import Column, Date, Integer, String, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    phone = Column(String)
    hashed_password = Column(String)

    applications = relationship("Application", back_populates="user")

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float)
    term = Column(Integer)
    status = Column(String, default="new")  # new, prescoring, offers, scoring, approved, rejected, signed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="applications")
    offers = relationship("Offer", back_populates="application")
    deal = relationship("Deal", back_populates="application", uselist=False)

class Offer(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"))
    rate = Column(Float)
    is_insurance = Column(Boolean)
    is_salary_client = Column(Boolean)
    monthly_payment = Column(Float)
    psk = Column(Float)
    is_selected = Column(Boolean, default=False)

    application = relationship("Application", back_populates="offers")

class Deal(Base):
    __tablename__ = "deals"
    
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"))
    final_rate = Column(Float)
    final_amount = Column(Float)
    final_term = Column(Integer)
    psk = Column(Float)
    payment_schedule = Column(JSON)
    status = Column(String, default="pending")  # pending, scoring, approved, rejected
    employer = Column(String)
    registration_address = Column(String)
    verification_code = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    application = relationship("Application", back_populates="deal")
    documents = relationship("Document", back_populates="deal")

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    deal_id = Column(Integer, ForeignKey("deals.id"))
    document_type = Column(String)
    file_path = Column(String)
    signing_date = Column(Date)
    
    deal = relationship("Deal", back_populates="documents")