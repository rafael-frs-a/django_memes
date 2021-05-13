from enum import Enum
from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from django.utils.html import strip_tags
from django.core.mail import send_mail

logger = get_task_logger(__name__)


class SendEmailResponses(Enum):
    SUCCESS = 0
    EMAIL_NOT_FOUND = 1
    EMAIL_ALREADY_SENT = 2


@shared_task(autoretry_for=(Exception,), retry_kwargs={'max_retries': 10}, default_retry_delay=5 * 60)
def send_email(id):
    from .models import Email
    email = Email.objects.filter(id=id).first()

    if not email:
        logger.info(f'Email with id {id} not found...')
        return SendEmailResponses.EMAIL_NOT_FOUND.name

    if email.sent:
        logger.info(f'Email with id {id} already sent...')
        return SendEmailResponses.EMAIL_ALREADY_SENT.name

    plain_message = strip_tags(email.body)
    logger.info(f'Sending email with id {id}...')

    if email.recipients:
        recipients = email.recipients.split(', ')
    else:
        recipients = [email.recipient.email]

    send_mail(email.subject, plain_message, settings.EMAIL_FROM,
              recipients, html_message=email.body)
    email.sent = True
    email.save()
    return ', '.join(recipients)
