import pytest
from smtplib import SMTPRecipientsRefused
from django.conf import settings
from django.test.utils import override_settings
from .test_utils import create_email_test_user
from ..tasks import send_email, SendEmailResponses


def get_test_user(user_data):
    user = create_email_test_user(user_data)
    email = user.emails.first()
    assert not email.sent
    assert not email.recipients
    return user, email


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend')
def test_successful_send_email(user_missing_email):
    user_missing_email['email'] = settings.EMAIL_HOST_USER
    user, email = get_test_user(user_missing_email)
    response = send_email(email.id)
    assert response == user.email
    email = user.emails.first()
    assert email.sent


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend')
def test_send_email_different_recipient(user_missing_email):
    user_missing_email['email'] = settings.EMAIL_HOST_USER
    user, email = get_test_user(user_missing_email)
    email.recipients = settings.EMAIL_TEST_USER
    email.save()
    response = send_email(email.id)
    assert response == email.recipients
    email = user.emails.first()
    assert email.sent


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend')
def test_send_email_multiple_recipients(user_missing_email):
    user_missing_email['email'] = settings.EMAIL_HOST_USER
    user, email = get_test_user(user_missing_email)
    email.recipients = f'{settings.EMAIL_TEST_USER}, {settings.EMAIL_HOST_USER}'
    email.save()
    response = send_email(email.id)
    assert response == email.recipients
    email = user.emails.first()
    assert email.sent


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend')
def test_send_invalid_email(user_invalid_email):
    user, email = get_test_user(user_invalid_email)

    with pytest.raises(SMTPRecipientsRefused):
        send_email(email.id)

    email = user.emails.first()
    assert not email.sent


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend')
def test_send_email_not_found(valid_user_1, valid_email2):
    user, email = get_test_user(valid_user_1)
    response = send_email(email.id + 1)
    assert response == SendEmailResponses.EMAIL_NOT_FOUND.name
    email = user.emails.first()
    assert not email.sent


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend')
def test_send_email_already_sent(valid_user_1):
    user, email = get_test_user(valid_user_1)
    email.sent = True
    email.save()
    response = send_email(email.id)
    assert response == SendEmailResponses.EMAIL_ALREADY_SENT.name
    email = user.emails.first()
    assert email.sent
