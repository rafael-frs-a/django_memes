from num2words import num2words
from django.db import models
from django.db.models.signals import post_save
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.template.loader import render_to_string
from base.url_serializer import url_timed_serializer
from .tasks import send_email

UserModel = get_user_model()


class Email(models.Model):
    subject = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    sent = models.BooleanField(default=False)
    recipients = models.TextField(blank=True, null=True)
    recipient = models.ForeignKey(
        UserModel, on_delete=models.CASCADE, related_name='emails')

    def __str__(self):
        return f'Email: {self.subject}. To: {self.recipient.email}'


def get_email_from_token(token, url_name, max_age):
    return url_timed_serializer.loads(
        token, salt=url_name, max_age=max_age)


def get_token_from_email(email, url_name):
    return url_timed_serializer.dumps(email, salt=url_name)


def __send_saved_email(sender, instance, created, **kwargs):
    if settings.TEST_MODE:
        return

    if not instance.sent:
        send_email.delay(instance.id)


def create_activation_email(user):
    token = get_token_from_email(user.email, 'account-activation')
    link = settings.SITE_URL + \
        reverse('users:activate-account', kwargs={'token': token})

    context = {
        'APP_NAME': settings.APP_NAME,
        'user': user,
        'hours': settings.ACCOUNT_ACTIVATION_EXPIRATION_TIME // 60 // 60,
        'link': link
    }

    body = render_to_string('emails/account_activation.html', context)
    email = Email(subject='Account Activation', body=body, recipient=user)
    email.sent = user.is_active
    email.save()


def create_change_email_confirmation(user, new_email):
    if not new_email or new_email == user.email:
        return False

    current_email_token = get_token_from_email(user.email, 'change-email')
    new_email_token = get_token_from_email(new_email, 'change-email')
    tokens = {
        'current_email_token': current_email_token,
        'new_email_token': new_email_token
    }

    link = settings.SITE_URL + reverse('users:change-email', kwargs=tokens)

    context = {
        'user': user,
        'new_email': new_email,
        'minutes': settings.CHANGE_EMAIL_EXPIRATION_TIME // 60,
        'link': link
    }

    body = render_to_string('emails/change_email.html', context)
    email = Email(subject='Change Email', body=body,
                  recipient=user, recipients=new_email)
    email.save()
    return True


def create_reset_password_email(user):
    token = get_token_from_email(user.email, 'reset-password')
    link = settings.SITE_URL + \
        reverse('users:reset-password-token', kwargs={'token': token})

    context = {
        'user': user,
        'minutes': settings.RESET_PASSWORD_EXPIRATION_TIME // 60,
        'link': link
    }

    body = render_to_string('emails/reset_password.html', context)
    email = Email(subject='Reset Password', body=body, recipient=user)
    email.save()


def create_delete_account_email(user):
    token = get_token_from_email(user.email, 'cancel-delete-account')
    link = settings.SITE_URL + \
        reverse('users:cancel-delete-account-token', kwargs={'token': token})

    context = {
        'user': user,
        'APP_NAME': settings.APP_NAME,
        'hours': settings.ACCOUNT_DELETION_INTERVAL // 60 // 60,
        'link': link
    }

    body = render_to_string('emails/delete_account.html', context)
    email = Email(subject='Account Deletion', body=body, recipient=user)
    email.save()


def create_ban_alert_email(moderation_status):
    post = moderation_status.post
    reason = moderation_status.denial_reason.description if moderation_status.denial_reason else None
    details = moderation_status.denial_detail
    user = post.author
    img_url = settings.SITE_URL + post.meme_file.url
    additional_msg = None

    if user.banned:
        ban_msg = f'Unfortunately, you have been indefinitely banned from {settings.APP_NAME} because of the following post:'
    else:
        ban_msg = f'Unfortunately, you have been temporarily banned from {settings.APP_NAME} because of the following post:'
        temporary_bans = num2words(user.temporary_bans, to='ordinal')
        remaining_bans = num2words(
            settings.USER_PERM_BAN_COUNT - user.temporary_bans).capitalize()
        additional_msg = f'Please, be careful. This is your {temporary_bans} ban. {remaining_bans} more ban(s) and it will last indefinitely.'

    context = {
        'user': user,
        'img_url': img_url,
        'reason': reason,
        'details': details,
        'ban_msg': ban_msg,
        'additional_msg': additional_msg
    }

    body = render_to_string('emails/ban_alert.html', context)
    email = Email(subject='Ban Alert', body=body, recipient=user)
    email.save()


post_save.connect(__send_saved_email, sender=Email)
