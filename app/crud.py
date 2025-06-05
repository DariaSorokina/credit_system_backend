import os
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from . import models, schemas
from passlib.context import CryptContext
from typing import List, Dict, Set, Tuple, Optional, Any
from app.schemas import DealUpdate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        email=user.email,
        full_name=user.full_name,
        phone=user.phone,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_application(db: Session, application_id: int):
    return db.query(models.Application).filter(models.Application.id == application_id).first()

def get_applications(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Application).offset(skip).limit(limit).all()

def create_application(db: Session, application: schemas.ApplicationCreate, user_id: int):
    db_application = models.Application(
        **application.dict(),
        user_id=user_id
    )
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application

def get_offers(db: Session, application_id: int):
    return db.query(models.Offer).filter(models.Offer.application_id == application_id).all()

def create_offers(db: Session, offers: List[schemas.OfferCreate], application_id: int):
    db_offers = []
    for offer in offers:
        db_offer = models.Offer(
            **offer.dict(),
            application_id=application_id
        )
        db.add(db_offer)
        db_offers.append(db_offer)
    db.commit()
    return db_offers

def select_offer(db: Session, application_id: int, offer_id: int):
    # Reset all offers selection
    db.query(models.Offer).filter(models.Offer.application_id == application_id).update({"is_selected": False})
    
    # Select the specified offer
    offer = db.query(models.Offer).filter(
        models.Offer.id == offer_id,
        models.Offer.application_id == application_id
    ).first()
    
    if offer:
        offer.is_selected = True
        db.commit()
        db.refresh(offer)
    return offer

def create_deal(db: Session, deal: schemas.DealCreate):
    db_deal = models.Deal(**deal.model_dump())
    db.add(db_deal)
    db.commit()
    db.refresh(db_deal)
    return db_deal

def get_deal(db: Session, deal_id: int):
    return db.query(models.Deal).filter(models.Deal.id == deal_id).first()

def get_deals(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Deal).offset(skip).limit(limit).all()

def update_deal(db: Session, deal_id: int, deal: schemas.DealUpdate):
    db_deal = db.query(models.Deal).filter(models.Deal.id == deal_id).first()
    if not db_deal:
        return None
    
    update_data = deal.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_deal, key, value)
    
    db.commit()
    db.refresh(db_deal)
    return db_deal

def delete_deal(db: Session, deal_id: int):
    db_deal = db.query(models.Deal).filter(models.Deal.id == deal_id).first()
    if not db_deal:
        return False
    
    db.delete(db_deal)
    db.commit()
    return True

def complete_deal(db: Session, deal_id: int, deal_data: schemas.DealComplete):
    db_deal = get_deal(db, deal_id)
    if not db_deal:
        return None
    
    db_deal.status = "completed"
    db_deal.completion_date = deal_data.completion_date
    db_deal.notes = deal_data.notes
    
    db.commit()
    db.refresh(db_deal)
    return db_deal

def verify_deal(db: Session, deal_id: int, code: str):
    db_deal = get_deal(db, deal_id)
    if not db_deal or db_deal.verification_code != code:
        return None
    
    db_deal.is_verified = True
    db.commit()
    db.refresh(db_deal)
    return db_deal

def get_application(db: Session, application_id: int):
    return db.query(models.Application).filter(models.Application.id == application_id).first()

def has_related_records(db: Session, application_id: int) -> bool:
    """Проверяет наличие связанных записей (offers, deals)"""
    return (
        db.query(models.Offer).filter(models.Offer.application_id == application_id).first() is not None or
        db.query(models.Deal).filter(models.Deal.application_id == application_id).first() is not None
    )

def delete_application(db: Session, application_id: int) -> bool:
    """Удаляет заявку и возвращает True если успешно"""
    try:
        db_application = db.query(models.Application).get(application_id)
        if not db_application:
            return False
            
        # Удаляем связанную сделку (если есть)
        if db_application.deal:
            db.delete(db_application.deal)
        
        # Offers удалятся автоматически благодаря каскаду
        db.delete(db_application)
        db.commit()
        return True
            
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Error deleting application: {str(e)}")
        return None
def create_document(db: Session, document: schemas.DocumentCreate):
    db_document = models.Document(**document.model_dump())
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

def get_document(db: Session, document_id: int):
    return db.query(models.Document).filter(models.Document.id == document_id).first()

def get_documents(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Document).offset(skip).limit(limit).all()

def get_documents_by_deal(db: Session, deal_id: int):
    return db.query(models.Document).filter(models.Document.deal_id == deal_id).all()

def update_document(db: Session, document_id: int, document: schemas.DocumentUpdate):
    db_document = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not db_document:
        return None
    
    update_data = document.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_document, key, value)
    
    db.commit()
    db.refresh(db_document)
    return db_document

def delete_document(db: Session, document_id: int):
    db_document = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not db_document:
        return False
    
    # Удаляем физический файл если он существует
    if os.path.exists(db_document.file_path):
        os.remove(db_document.file_path)
    
    db.delete(db_document)
    db.commit()
    return True

def create_deal_from_offer(db: Session, application_id: int, offer: schemas.Offer):
    db_deal = models.Deal(
        application_id=application_id,
        final_rate=offer.rate,
        final_amount=offer.monthly_payment * offer.application.term,
        final_term=offer.application.term,
        psk=offer.psk,
        status="pending"
    )
    db.add(db_deal)
    db.commit()
    db.refresh(db_deal)
    return db_deal