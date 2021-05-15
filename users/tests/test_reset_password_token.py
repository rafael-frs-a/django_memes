import re
import pytest
from urllib.parse import urlsplit
from time import sleep
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
from pytest_django.asserts import assertTemplateUsed
from emails.models import Email, get_token_from_email, get_email_from_token, create_reset_password_email
from .test_utils import create_test_user


def create_test_user_reset_password(user_data, is_active=True,
                                    is_banned=False, banned_seconds=None, is_deleted=False):
    user = create_test_user(user_data, is_active=is_active,
                            is_banned=is_banned, banned_seconds=banned_seconds)
    user.emails.all().delete()

    if is_deleted:
        user.deleted = True
        user.save()

    create_reset_password_email(user)
    return user


@pytest.mark.django_db
def test_create_test_user_reset_password(valid_user_1):
    user = create_test_user_reset_password(valid_user_1)
    assert Email.objects.count() == 1
    assert user.emails.count() == 1


@pytest.mark.django_db
def test_successful_reset_password(client, valid_user_1, valid_password2):
    user = create_test_user_reset_password(valid_user_1)
    url = re.findall('(?<=href=").+?(?=")', user.emails.first().body)[0]
    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, 'users/reset_password_token.html')
    response = client.post(url, {'password': valid_password2})
    assert response.status_code == 302
    assert response.url == reverse('users:login')
    user = get_user_model().objects.first()
    assert user.check_password(valid_password2)


@pytest.mark.django_db
def test_invalid_token(client):
    url = reverse('users:reset-password-token', kwargs={'token': 'token'})
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == reverse('users:login')


@pytest.mark.django_db
def test_valid_token_user_not_found(client, valid_user_1, valid_email2):
    user = create_test_user_reset_password(valid_user_1)
    assert user.email != valid_email2
    token = get_token_from_email(valid_email2, 'reset-password')
    email = get_email_from_token(
        token, 'reset-password', settings.RESET_PASSWORD_EXPIRATION_TIME)
    assert email == valid_email2
    url = reverse('users:reset-password-token', kwargs={'token': token})
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == reverse('users:login')


@pytest.mark.django_db
def test_valid_token_user_not_activated(client, valid_user_1):
    user = create_test_user_reset_password(valid_user_1, is_active=False)
    url = re.findall('(?<=href=").+?(?=")', user.emails.first().body)[0]
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == reverse('users:login')


@pytest.mark.django_db
def test_valid_token_user_banned(client, valid_user_1):
    user = create_test_user_reset_password(valid_user_1, is_banned=True)
    url = re.findall('(?<=href=").+?(?=")', user.emails.first().body)[0]
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == reverse('users:login')


@pytest.mark.django_db
def test_valid_token_user_banned_until(client, valid_user_1):
    user = create_test_user_reset_password(valid_user_1, banned_seconds=60)
    url = re.findall('(?<=href=").+?(?=")', user.emails.first().body)[0]
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == reverse('users:login')


@pytest.mark.django_db
def test_valid_token_user_banned_until_expired(client, valid_user_1):
    user = create_test_user_reset_password(valid_user_1, banned_seconds=1)
    url = re.findall('(?<=href=").+?(?=")', user.emails.first().body)[0]
    sleep(1)
    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, 'users/reset_password_token.html')


@pytest.mark.django_db
def test_valid_token_user_deleted(client, valid_user_1):
    user = create_test_user_reset_password(valid_user_1, is_deleted=True)
    url = re.findall('(?<=href=").+?(?=")', user.emails.first().body)[0]
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == reverse('users:login')


@pytest.mark.django_db
def test_expired_token(client, valid_user_1):
    user = create_test_user_reset_password(valid_user_1)
    url = re.findall('(?<=href=").+?(?=")', user.emails.first().body)[0]
    expiration_time = settings.RESET_PASSWORD_EXPIRATION_TIME
    settings.RESET_PASSWORD_EXPIRATION_TIME = 0
    sleep(1)
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == reverse('users:login')
    settings.RESET_PASSWORD_EXPIRATION_TIME = expiration_time


def perform_failed_reset_password(client, user_data, password):
    user = create_test_user_reset_password(user_data)
    url = re.findall('(?<=href=").+?(?=")', user.emails.first().body)[0]
    url = urlsplit(url).path
    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, 'users/reset_password_token.html')
    response = client.post(url, {'password': password})
    assert response.status_code == 302
    assert response.url == url
    assert not user.check_password(
        password) or user_data['password'] == password


@pytest.mark.django_db
def test_missing_password(client, valid_user_1):
    perform_failed_reset_password(client, valid_user_1, '')


@pytest.mark.django_db
def test_password_similar_username(client, valid_user_1, password_similar_username1):
    perform_failed_reset_password(
        client, valid_user_1, password_similar_username1)


@pytest.mark.django_db
def test_password_similar_email(client, valid_user_1, user_password_similar_email):
    perform_failed_reset_password(
        client, valid_user_1, user_password_similar_email)


@pytest.mark.django_db
def test_short_password(client, valid_user_1, user_short_password):
    perform_failed_reset_password(client, valid_user_1, user_short_password)


@pytest.mark.django_db
def test_common_password(client, valid_user_1, user_common_password):
    perform_failed_reset_password(client, valid_user_1, user_common_password)


@pytest.mark.django_db
def test_numeric_password(client, valid_user_1, user_numeric_password):
    perform_failed_reset_password(client, valid_user_1, user_numeric_password)


@pytest.mark.django_db
def test_current_password(client, valid_user_1):
    perform_failed_reset_password(
        client, valid_user_1, valid_user_1['password'])
