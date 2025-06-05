from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, crud
from ..database import get_db
from ..tasks import process_full_scoring

router = APIRouter(prefix="/deals", tags=["deals"])

@router.post("/", response_model=schemas.Deal, status_code=status.HTTP_201_CREATED)
def create_deal(
    deal: schemas.DealCreate,
    db: Session = Depends(get_db)
):
    return crud.create_deal(db=db, deal=deal)

@router.get("/", response_model=List[schemas.Deal])
def read_deals(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    deals = crud.get_deals(db, skip=skip, limit=limit)
    return deals

@router.get("/{deal_id}", response_model=schemas.Deal)
def read_deal(
    deal_id: int,
    db: Session = Depends(get_db)
):
    db_deal = crud.get_deal(db, deal_id=deal_id)
    if db_deal is None:
        raise HTTPException(status_code=404, detail="Deal not found")
    return db_deal

@router.put("/{deal_id}", response_model=schemas.Deal)
def update_deal(
    deal_id: int,
    deal: schemas.DealUpdate,
    db: Session = Depends(get_db)
):
    db_deal = crud.update_deal(db, deal_id=deal_id, deal=deal)
    if db_deal is None:
        raise HTTPException(status_code=404, detail="Deal not found")
    return db_deal

@router.delete("/{deal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_deal(
    deal_id: int,
    db: Session = Depends(get_db)
):
    success = crud.delete_deal(db, deal_id=deal_id)
    if not success:
        raise HTTPException(status_code=404, detail="Deal not found")
    return None

@router.post("/{deal_id}/complete", response_model=schemas.Deal)
def complete_deal(
    deal_id: int,
    deal_data: schemas.DealComplete,
    db: Session = Depends(get_db)
):
    db_deal = crud.complete_deal(db, deal_id=deal_id, deal_data=deal_data)
    if not db_deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    process_full_scoring.delay(deal_id)
    return db_deal

@router.post("/{deal_id}/verify-code", response_model=schemas.Deal)
def verify_code(
    deal_id: int,
    verification: schemas.DealVerification,
    db: Session = Depends(get_db)
):
    db_deal = crud.verify_deal(db, deal_id=deal_id, code=verification.code)
    if not db_deal:
        raise HTTPException(status_code=400, detail="Invalid verification code")
    return db_deal