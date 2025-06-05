from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import List, Optional

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class ApplicationBase(BaseModel):
    amount: float
    term: int

class ApplicationCreate(ApplicationBase):
    pass

class Application(ApplicationBase):
    id: int
    user_id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class OfferBase(BaseModel):
    rate: float
    is_insurance: bool
    is_salary_client: bool
    monthly_payment: float
    psk: float

class OfferCreate(OfferBase):
    pass

class Offer(OfferBase):
    id: int
    application_id: int
    is_selected: bool

    class Config:
        orm_mode = True

class DealBase(BaseModel):
    final_rate: float
    final_amount: float
    final_term: int
    psk: float
    payment_schedule: dict

class DealUpdate(BaseModel):
    amount: int
    status: str

class DealCreate(DealBase):
    employer: str
    registration_address: str

class Deal(DealBase):
    id: int
    application_id: int
    status: str
    verification_code: Optional[str]

    class Config:
        orm_mode = True

class EmailSchema(BaseModel):
    email: EmailStr
    subject: str
    message: str

class MessageResponse(BaseModel):
    message: str    

class DocumentBase(BaseModel):
    deal_id: int
    document_type: str
    file_path: str
    signing_date: date

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(BaseModel):
    deal_id: Optional[int] = None
    document_type: Optional[str] = None
    file_path: Optional[str] = None
    signing_date: Optional[date] = None

class Document(DocumentBase):
    id: int

    class Config:
        from_attributes = True

class DealComplete(BaseModel):
    completion_date: date
    notes: Optional[str] = None

class DealVerification(BaseModel):
    code: str    