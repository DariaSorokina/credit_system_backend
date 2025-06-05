from typing import List, Dict
import random
from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models import Application

def calculate_monthly_payment(amount: float, term: int, rate: float) -> float:
    monthly_rate = rate / 100 / 12
    payment = amount * (monthly_rate * (1 + monthly_rate)**term) / ((1 + monthly_rate)**term - 1)
    return round(payment, 2)

def calculate_psk(amount: float, term: int, rate: float, has_insurance: bool) -> float:
    total_payment = calculate_monthly_payment(amount, term, rate) * term
    if has_insurance:
        total_payment += amount * 0.01  # Страховка 1% от суммы
    psk = ((total_payment - amount) / amount) * 100 / (term / 12)
    return round(psk, 2)

def calculate_offers(application_id: int) -> List[Dict]:
    db = SessionLocal()
    try:
        application = db.query(Application).filter(Application.id == application_id).first()
        if not application:
            return []
        
        amount = application.amount
        term = application.term
        base_rate = 15.0  # Базовая ставка
        
        offers = [
            {
                "rate": base_rate,
                "is_insurance": False,
                "is_salary_client": False,
                "monthly_payment": calculate_monthly_payment(amount, term, base_rate),
                "psk": calculate_psk(amount, term, base_rate, False)
            },
            {
                "rate": base_rate - 2.0,
                "is_insurance": True,
                "is_salary_client": False,
                "monthly_payment": calculate_monthly_payment(amount, term, base_rate - 2.0),
                "psk": calculate_psk(amount, term, base_rate - 2.0, True)
            },
            {
                "rate": base_rate - 3.0,
                "is_insurance": False,
                "is_salary_client": True,
                "monthly_payment": calculate_monthly_payment(amount, term, base_rate - 3.0),
                "psk": calculate_psk(amount, term, base_rate - 3.0, False)
            },
            {
                "rate": base_rate - 5.0,
                "is_insurance": True,
                "is_salary_client": True,
                "monthly_payment": calculate_monthly_payment(amount, term, base_rate - 5.0),
                "psk": calculate_psk(amount, term, base_rate - 5.0, True)
            }
        ]
        return offers
    finally:
        db.close()

def full_scoring(deal_id: int) -> Dict:
    db = SessionLocal()
    try:
        deal = db.query(models.Deal).filter(models.Deal.id == deal_id).first()
        if not deal:
            return {"approved": False}
        
        # Здесь должна быть реальная логика скоринга
        # Для примера используем случайное решение с 70% вероятностью одобрения
        approved = random.random() > 0.3
        
        if approved:
            payment_schedule = []
            monthly_payment = calculate_monthly_payment(
                deal.final_amount, 
                deal.final_term, 
                deal.final_rate
            )
            current_date = datetime.now()
            
            for i in range(1, deal.final_term + 1):
                payment_date = current_date + timedelta(days=30*i)
                payment_schedule.append({
                    "date": payment_date.strftime("%Y-%m-%d"),
                    "amount": monthly_payment,
                    "principal": monthly_payment * 0.7,  # Примерное распределение
                    "interest": monthly_payment * 0.3
                })
            
            return {
                "approved": True,
                "final_rate": deal.final_rate,
                "final_amount": deal.final_amount,
                "final_term": deal.final_term,
                "psk": deal.psk,
                "payment_schedule": payment_schedule
            }
        else:
            return {"approved": False}
    finally:
        db.close()