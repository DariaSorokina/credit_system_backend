from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, crud
from ..database import get_db
from ..tasks import generate_and_send_documents
import shutil
import os

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/", response_model=schemas.Document, status_code=status.HTTP_201_CREATED)
def create_document(
    document: schemas.DocumentCreate,
    db: Session = Depends(get_db)
):
    # Проверяем существование сделки
    db_deal = crud.get_deal(db, document.deal_id)
    if not db_deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    return crud.create_document(db=db, document=document)

@router.get("/", response_model=List[schemas.Document])
def read_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return crud.get_documents(db, skip=skip, limit=limit)

@router.get("/{document_id}", response_model=schemas.Document)
def read_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    db_document = crud.get_document(db, document_id=document_id)
    if db_document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return db_document

@router.get("/deal/{deal_id}", response_model=List[schemas.Document])
def read_deal_documents(
    deal_id: int,
    db: Session = Depends(get_db)
):
    documents = crud.get_documents_by_deal(db, deal_id=deal_id)
    if not documents:
        raise HTTPException(status_code=404, detail="No documents found for this deal")
    return documents

@router.put("/{document_id}", response_model=schemas.Document)
def update_document(
    document_id: int,
    document: schemas.DocumentUpdate,
    db: Session = Depends(get_db)
):
    db_document = crud.update_document(db, document_id=document_id, document=document)
    if db_document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return db_document

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    success = crud.delete_document(db, document_id=document_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return None

@router.post("/{deal_id}/generate", status_code=status.HTTP_202_ACCEPTED)
def generate_documents(
    deal_id: int, 
    db: Session = Depends(get_db)
):
    db_deal = crud.get_deal(db, deal_id)
    if not db_deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    if db_deal.status != "approved":
        raise HTTPException(
            status_code=400, 
            detail="Deal must be in 'approved' status to generate documents"
        )
    
    generate_and_send_documents.delay(deal_id)
    return {"message": "Document generation and sending process started"}

@router.post("/upload/{deal_id}", response_model=schemas.Document)
async def upload_document(
    deal_id: int,
    document_type: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Проверяем существование сделки
    db_deal = crud.get_deal(db, deal_id)
    if not db_deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    # Создаем папку для документов если ее нет
    os.makedirs("documents", exist_ok=True)
    
    # Генерируем путь к файлу
    file_path = f"documents/deal_{deal_id}_{file.filename}"
    
    # Сохраняем файл
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Создаем запись в базе данных
    document_data = schemas.DocumentCreate(
        deal_id=deal_id,
        document_type=document_type,
        file_path=file_path,
        signing_date="2023-01-01"  # Здесь должна быть логика получения реальной даты
    )
    
    return crud.create_document(db=db, document=document_data)