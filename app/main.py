
import aiosmtplib
import os

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from fastapi import (Body, FastAPI, File, UploadFile, Response,
                     BackgroundTasks)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List

from app.depends import get_settings


settings = get_settings()

app = FastAPI(root_path=settings.root_path, title="MailSender")


# setup middleware
if settings.debug:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


class EmailData(BaseModel):
    recipients: List[str]
    subject: str = None
    message: str = None


async def emailing(data: EmailData, attachments: List):
    message = MIMEMultipart()
    message["from"] = settings.mail_from
    message["Subject"] = data.subject
    message.attach(MIMEText(data.message, 'plain'))
    for attachment in attachments:
        if isinstance(attachment, str):
            with open(attachment, 'r') as f:
                file = f.read()
            filename = attachment.split(os.path.sep)[-1]
        else:
            file = await attachment.read()
            filename = attachment.filename
        attachfile = MIMEApplication(
            file,
            _subtype=filename.split('.')[-1]
        )
        attachfile.add_header(
            'content-disposition', 'attachment', filename=filename
        )
        message.attach(attachfile)

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


@app.post("/email", status_code=201)
async def send_email(
    background: BackgroundTasks,
    recipients: List[EmailStr] = Body(...),
    subject: str = Body(''),
    message: str = Body(...),
    attachments: List[UploadFile] = File(None)
):
    data = EmailData(
        recipients=recipients,
        subject=subject,
        message=message
    )
    if not attachments:
        attachments = []
    background.add_task(emailing, data, attachments)
    return Response(status_code=201)


@app.post("/csv", status_code=201)
async def send_from_csv(
    background: BackgroundTasks,
    csv_file: UploadFile
):
    lines = csv_file.file.readlines()
    for line in lines[1:]:
        data = str(line, "utf-8").split(';')
        emailData = EmailData(
            recipients=[data[0].strip()],
            subject=data[1],
            message=data[2]
        )
        attachments = [data[3].strip()]
        background.add_task(emailing, emailData, attachments)

    return Response(status_code=201)
