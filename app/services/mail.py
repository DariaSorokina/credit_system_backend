import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings
from app.schemas import EmailSchema

def send_email(email_data: EmailSchema):
    msg = MIMEMultipart()
    msg['From'] = settings.EMAIL_FROM
    msg['To'] = email_data.email
    msg['Subject'] = email_data.subject
    
    msg.attach(MIMEText(email_data.message, 'plain'))
    
    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.send_message(msg)
    except Exception as e:
        print(f"Error sending email: {e}")