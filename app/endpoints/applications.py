
from fastapi import APIRouter, Depends, HTTPException
from fastapi import status  
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, crud
from ..database import get_db
from ..tasks import process_prescoring

router = APIRouter(prefix="/applications", tags=["applications"])

@router.post("/", response_model=schemas.Application)
def create_application(
    application: schemas.ApplicationCreate,
    user_id: int,
    db: Session = Depends(get_db)
):
    db_application = crud.create_application(db, application, user_id)
    process_prescoring.delay(db_application.id)
    return db_application

@router.get("/{application_id}", response_model=schemas.Application)
def read_application(application_id: int, db: Session = Depends(get_db)):
    db_application = crud.get_application(db, application_id=application_id)
    if db_application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    return db_application

@router.get("/{application_id}/offers", response_model=List[schemas.Offer])
def read_offers(application_id: int, db: Session = Depends(get_db)):
    return crud.get_offers(db, application_id=application_id)

@router.post("/{application_id}/select-offer/{offer_id}", response_model=schemas.Application)
def select_offer(
    application_id: int, 
    offer_id: int,
    db: Session = Depends(get_db)
):
    db_offer = crud.select_offer(db, application_id, offer_id)
    if not db_offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    
    # Создаем сделку при выборе предложения
    crud.create_deal_from_offer(db, application_id, db_offer)
    
    # Обновляем статус заявки
    db_application = crud.get_application(db, application_id)
    db_application.status = "scoring"
    db.commit()
    db.refresh(db_application)
    
    return db_application

@router.delete(
    "/{application_id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.MessageResponse,
    responses={
        404: {"model": schemas.MessageResponse, "description": "Application not found"},
        500: {"model": schemas.MessageResponse, "description": "Database error"}
    }
)
def delete_application(
    application_id: int,
    db: Session = Depends(get_db)
):
    result = crud.delete_application(db, application_id)
    
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Database error during deletion"}
        )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "Application not found"}
        )
    
    return {"message": "Application and all related data deleted successfully"}