import aiosmtplib
from email.message import EmailMessage
from pydantic import EmailStr

from src.services.auth import auth_service
from src.conf.connfig import config


async def send_email(email: EmailStr, host: str):
    token = auth_service.create_email_token({"sub": email})
    message = EmailMessage()
    message["From"] = config.MAIL_FROM
    message["To"] = email
    message["Subject"] = "Verify to email"

    verify_link = f"{host}api/auth/confirmed_email/{token}"
    message.set_content(f"Click to verify your email: {verify_link}")

    await aiosmtplib.send(
        message,
        hostname=config.MAIL_SERVER,
        port=config.MAIL_PORT,
        username=config.MAIL_USERNAME,
        password=config.MAIL_PASSWORD,
        use_tls=False,
    )
