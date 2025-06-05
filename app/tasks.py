from celery import Celery
from .services.scoring import calculate_offers, full_scoring
from .services.mail import send_email
from .models import Offer, Deal, Application
from .database import SessionLocal
from .schemas import EmailSchema
from .config import settings
import random
import string

from app import models

celery = Celery(__name__)
celery.conf.broker_url = settings.REDIS_URL
celery.conf.result_backend = settings.REDIS_URL

@celery.task
def process_prescoring(application_id: int):
    db = SessionLocal()
    try:
        application = db.query(models.Application).filter(models.Application.id == application_id).first()
        if not application:
            return
        
        # Базовые проверки
        if application.amount <= 0 or application.term <= 0:
            application.status = "rejected"
            db.commit()
            return
        
        # Здесь должны быть реальные проверки КИ и нагрузки
        # Для примера - случайный отказ с 10% вероятностью
        if random.random() < 0.1:
            application.status = "rejected"
            db.commit()
            return
        
        application.status = "prescoring"
        db.commit()
        
        # Генерация предложений
        offers_data = calculate_offers(application_id)
        
        for offer_data in offers_data:
            offer = Offer(
                application_id=application_id,
                rate=offer_data["rate"],
                is_insurance=offer_data["is_insurance"],
                is_salary_client=offer_data["is_salary_client"],
                monthly_payment=offer_data["monthly_payment"],
                psk=offer_data["psk"]
            )
            db.add(offer)
        
        application.status = "offers"
        db.commit()
        
        # Отправка письма клиенту
        user = application.user
        
        email_data = EmailSchema(
            email=user.email,
            subject="Ваша заявка предварительно одобрена",
            message="Ваша заявка на кредит прошла предварительное одобрение. Пожалуйста, выберите один из предложенных вариантов."
        )
        
        send_email(email_data)
        
    finally:
        db.close()

@celery.task
def process_full_scoring(deal_id: int):
    db = SessionLocal()
    try:
        deal = db.query(Deal).filter(Deal.id == deal_id).first()
        if not deal:
            return
        
        application = deal.application
        scoring_result = full_scoring(deal_id)
        
        if scoring_result["approved"]:
            deal.final_rate = scoring_result["final_rate"]
            deal.final_amount = scoring_result["final_amount"]
            deal.final_term = scoring_result["final_term"]
            deal.psk = scoring_result["psk"]
            deal.payment_schedule = scoring_result["payment_schedule"]
            deal.status = "approved"
            application.status = "approved"
            
            subject = "Ваш кредит одобрен"
            message = "Поздравляем! Ваш кредит одобрен. Для завершения оформления перейдите по ссылке."
        else:
            deal.status = "rejected"
            application.status = "rejected"
            
            subject = "Отказ в кредите"
            message = "К сожалению, ваша заявка на кредит была отклонена."
        
        db.commit()
        
        # Отправка письма с результатом
        user = application.user
        
        email_data = EmailSchema(
            email=user.email,
            subject=subject,
            message=message
        )
        
        send_email(email_data)
        
    finally:
        db.close()

@celery.task
def generate_and_send_documents(deal_id: int):
    db = SessionLocal()
    try:
        deal = db.query(Deal).filter(Deal.id == deal_id).first()
        if not deal or deal.status != "approved":
            return
        
        # Генерация кода подтверждения
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        deal.verification_code = code
        db.commit()
        
        # Отправка документов
        application = deal.application
        user = application.user
        
        email_data = EmailSchema(
            email=user.email,
            subject="Документы по вашему кредиту",
            message=f"Пожалуйста, ознакомьтесь с прикрепленными документами.\n"
                   f"Для подписания введите код: {code}"
        )
        
        send_email(email_data)
        
    finally:
        db.close()