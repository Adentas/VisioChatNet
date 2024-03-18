from flask_mail import Message

from src import mail
from src.conf.config import settings


def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=settings.MAIL_DEFAULT_SENDER,
    )
    mail.send(msg)