from passlib.context import CryptContext
import os
import smtplib
from email.mime.text import MIMEText

pwd_context = CryptContext(schemes=['bcrypt'],deprecated="auto")

def hash(password : str):
    return pwd_context.hash(password)

def verify(plain_pswd,hash_pswd):
    return pwd_context.verify(plain_pswd,hash_pswd)
    
def send_otp_email(to_email: str, otp: str):
    msg = MIMEText(f"Your OTP for password reset is: {otp}\nThis code expires in 5 minutes.")
    msg["Subject"] = "Password Reset OTP"
    msg["From"] = os.getenv("SMTP_FROM")
    msg["To"] = to_email

    with smtplib.SMTP(os.getenv("SMTP_HOST"), int(os.getenv("SMTP_PORT"))) as server:
        server.starttls()
        server.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASSWORD"))
        server.send_message(msg)
