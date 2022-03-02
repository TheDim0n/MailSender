
import aiosmtplib

from email.message import EmailMessage
from fastapi import FastAPI, Response, BackgroundTasks
from pydantic import BaseModel, EmailStr
from typing import List

from app.depends import get_settings


settings = get_settings()

app = FastAPI()


class EmailData(BaseModel):
    recipients: List[EmailStr]
    subject: str
    message: str


async def emailing(data: EmailData):
    message = EmailMessage()
    message["from"] = settings.mail_from
    message["Subject"] = data.subject
    message.set_content(data.message)

    await aiosmtplib.send(
        message,
        recipients=data.recipients,
        hostname=settings.mail_server,
        port=settings.mail_port,
        username=settings.mail_username,
        password=settings.mail_password,
        use_tls=settings.mail_tls,
        validate_certs=settings.validate_certs
    )


@app.post("/email/", status_code=201)
async def send_email(data: EmailData, background: BackgroundTasks):
    background.add_task(emailing, data)
    return Response(status_code=201)
