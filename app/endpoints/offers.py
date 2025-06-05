from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.crud import create_offers, get_offers, select_offer
from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/applications/{application_id}/offers", tags=["offers"])

@router.post("/", response_model=List[schemas.Offer])
def create_offers_endpoint(
    application_id: int,
    offers: List[schemas.OfferCreate],
    db: Session = Depends(get_db)
):
    # Проверка существования заявки
    application = db.query(models.Application).filter(models.Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    return create_offers(db=db, offers=offers, application_id=application_id)

@router.get("/", response_model=List[schemas.Offer])
def read_offers(
    application_id: int,
    db: Session = Depends(get_db)
):
    application = db.query(models.Application).filter(models.Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    return get_offers(db=db, application_id=application_id)

@router.post("/{offer_id}/select", response_model=schemas.Offer)
def select_offer_endpoint(
    application_id: int,
    offer_id: int,
    db: Session = Depends(get_db)
):
    # Проверка существования заявки
    application = db.query(models.Application).filter(models.Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    selected_offer = select_offer(db=db, application_id=application_id, offer_id=offer_id)
    if not selected_offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    
    return selected_offer