# backend/utils/email_utils.py
import aiosmtplib
from email.message import EmailMessage
import os

async def send_email(to: str, subject: str, body: str):
    msg = EmailMessage()
    msg["From"] = os.getenv("SMTP_EMAIL")
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    await aiosmtplib.send(
        msg,
        hostname=os.getenv("SMTP_HOST", "smtp.gmail.com"),
        port=int(os.getenv("SMTP_PORT", 587)),
        username=os.getenv("SMTP_EMAIL"),
        password=os.getenv("SMTP_PASSWORD"),
        start_tls=True
    )
