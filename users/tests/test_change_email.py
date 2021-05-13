import re
import pytest
from time import sleep
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
from emails.models import create_change_email_confirmation, get_token_from_email, get_email_from_token
from .test_utils import (create_test_user, create_activated_test_user,
                         create_banned_activated_test_user, create_banned_until_activated_test_user,
                         create_deleted_test_user)


def perform_successful_email_change(client, user, new_email, url, request):
    response = request(url)
    assert response.status_code == 302
    assert response.url == reverse('users:account')
    new_user = get_user_model().objects.first()
    assert user == new_user
    assert user.email != new_user.email
    assert new_user.email == new_email


def perform_email_change(client, user_data, new_email, request):
    user = create_activated_test_user(user_data)
    client.force_login(user)
    user.emails.all().delete()
    create_change_email_confirmation(user, new_email)
    assert user.emails.count() == 1
    url = re.findall('(?<=href=").+?(?=")', user.emails.first().body)[0]
    perform_successful_email_change(client, user, new_email, url, request)


@pytest.mark.django_db
def test_successful_email_change_get(client, valid_user_1, valid_email2):
    perform_email_change(client, valid_user_1, valid_email2, client.get)


@pytest.mark.django_db
def test_successful_email_change_post(client, valid_user_1, valid_email2):
    perform_email_change(client, valid_user_1, valid_email2, client.post)


def perform_failed_email_change(client, user, url, request):
    response = request(url)
    assert response.status_code == 302
    assert response.url == reverse('users:account')
    new_user = get_user_model().objects.first()
    assert user == new_user
    assert user.email == new_user.email


def perform_invalid_current_email_token(client, user_data, new_email, request):
    user = create_activated_test_user(user_data)
    client.force_login(user)
    new_email_token = get_token_from_email(new_email, 'change-email')
    email = get_email_from_token(
        new_email_token, 'change-email', settings.CHANGE_EMAIL_EXPIRATION_TIME)
    assert email == new_email
    args = {
        'current_email_token': 'token',
        'new_email_token': new_email_token
    }

    url = reverse('users:change-email', kwargs=args)
    perform_failed_email_change(client, user, url, request)


@pytest.mark.django_db
def test_invalid_current_email_token_get(client, valid_user_1, valid_email2):
    perform_invalid_current_email_token(
        client, valid_user_1, valid_email2, client.get)


@pytest.mark.django_db
def test_invalid_current_email_token_post(client, valid_user_1, valid_email2):
    perform_invalid_current_email_token(
        client, valid_user_1, valid_email2, client.post)


def perform_invalid_new_email_token(client, user_data, request):
    user = create_activated_test_user(user_data)
    client.force_login(user)
    current_email_token = get_token_from_email(user.email, 'change-email')
    email = get_email_from_token(
        current_email_token, 'change-email', settings.CHANGE_EMAIL_EXPIRATION_TIME)
    assert email == user.email
    args = {
        'current_email_token': current_email_token,
        'new_email_token': 'token'
    }

    url = reverse('users:change-email', kwargs=args)
    perform_failed_email_change(client, user, url, request)


@pytest.mark.django_db
def test_invalid_new_email_token_get(client, valid_user_1):
    perform_invalid_new_email_token(client, valid_user_1, client.get)


@pytest.mark.django_db
def test_invalid_new_email_token_post(client, valid_user_1):
    perform_invalid_new_email_token(client, valid_user_1, client.post)


def perform_expired_tokens(client, user_data, new_email, request):
    user = create_activated_test_user(user_data)
    client.force_login(user)
    user.emails.all().delete()
    create_change_email_confirmation(user, new_email)
    assert user.emails.count() == 1
    url = re.findall('(?<=href=").+?(?=")', user.emails.first().body)[0]
    expiration_time = settings.CHANGE_EMAIL_EXPIRATION_TIME
    settings.CHANGE_EMAIL_EXPIRATION_TIME = 0
    sleep(1)
    perform_failed_email_change(client, user, url, request)
    settings.CHANGE_EMAIL_EXPIRATION_TIME = expiration_time


@pytest.mark.django_db
def test_expired_tokens_get(client, valid_user_1, valid_email2):
    perform_expired_tokens(client, valid_user_1, valid_email2, client.get)


@pytest.mark.django_db
def test_expired_tokens_post(client, valid_user_1, valid_email2):
    perform_expired_tokens(client, valid_user_1, valid_email2, client.post)


def perform_user_not_found(client, user_data, new_email, request):
    user = create_activated_test_user(user_data)
    client.force_login(user)
    new_email_token = get_token_from_email(new_email, 'change-email')
    email = get_email_from_token(
        new_email_token, 'change-email', settings.CHANGE_EMAIL_EXPIRATION_TIME)
    assert email == new_email
    args = {
        'current_email_token': new_email_token,
        'new_email_token': new_email_token
    }

    url = reverse('users:change-email', kwargs=args)
    perform_failed_email_change(client, user, url, request)


@pytest.mark.django_db
def test_user_not_found_get(client, valid_user_1, valid_email2):
    perform_user_not_found(client, valid_user_1, valid_email2, client.get)


@pytest.mark.django_db
def test_user_not_found_post(client, valid_user_1, valid_email2):
    perform_user_not_found(client, valid_user_1, valid_email2, client.post)


def perform_user_not_activated(client, user_data, new_email, request):
    user = create_test_user(user_data)
    client.force_login(user)
    user.emails.all().delete()
    create_change_email_confirmation(user, new_email)
    assert user.emails.count() == 1
    url = re.findall('(?<=href=").+?(?=")', user.emails.first().body)[0]
    perform_failed_email_change(client, user, url, request)


@pytest.mark.django_db
def test_user_not_activated_get(client, valid_user_1, valid_email2):
    perform_user_not_activated(client, valid_user_1, valid_email2, client.get)


@pytest.mark.django_db
def test_user_not_activated_post(client, valid_user_1, valid_email2):
    perform_user_not_activated(client, valid_user_1, valid_email2, client.post)


def perform_user_banned(client, user_data, new_email, request):
    user = create_banned_activated_test_user(user_data)
    client.force_login(user)
    user.emails.all().delete()
    create_change_email_confirmation(user, new_email)
    assert user.emails.count() == 1
    url = re.findall('(?<=href=").+?(?=")', user.emails.first().body)[0]
    perform_failed_email_change(client, user, url, request)


@pytest.mark.django_db
def test_user_banned_get(client, valid_user_1, valid_email2):
    perform_user_banned(client, valid_user_1, valid_email2, client.get)


@pytest.mark.django_db
def test_user_banned_post(client, valid_user_1, valid_email2):
    perform_user_banned(client, valid_user_1, valid_email2, client.post)


def perform_user_banned_until(client, user_data, new_email, request):
    user = create_banned_until_activated_test_user(user_data, seconds=60)
    client.force_login(user)
    user.emails.all().delete()
    create_change_email_confirmation(user, new_email)
    assert user.emails.count() == 1
    url = re.findall('(?<=href=").+?(?=")', user.emails.first().body)[0]
    perform_failed_email_change(client, user, url, request)


@pytest.mark.django_db
def test_user_banned_until_get(client, valid_user_1, valid_email2):
    perform_user_banned_until(client, valid_user_1, valid_email2, client.get)


@pytest.mark.django_db
def test_user_banned_until_post(client, valid_user_1, valid_email2):
    perform_user_banned_until(client, valid_user_1, valid_email2, client.post)


def perform_user_banned_until_expired(client, user_data, new_email, request):
    user = create_banned_until_activated_test_user(user_data, seconds=1)
    client.force_login(user)
    user.emails.all().delete()
    create_change_email_confirmation(user, new_email)
    assert user.emails.count() == 1
    url = re.findall('(?<=href=").+?(?=")', user.emails.first().body)[0]
    sleep(1)
    perform_successful_email_change(client, user, new_email, url, request)


@pytest.mark.django_db
def test_user_banned_until_expired_get(client, valid_user_1, valid_email2):
    perform_user_banned_until_expired(
        client, valid_user_1, valid_email2, client.get)


@pytest.mark.django_db
def test_user_banned_until_expired_post(client, valid_user_1, valid_email2):
    perform_user_banned_until_expired(
        client, valid_user_1, valid_email2, client.post)


def perform_current_email_another_user(client, user_data_1, user_data_2, new_email, request):
    user = create_activated_test_user(user_data_1)
    client.force_login(user)
    create_test_user(user_data_2)
    current_email_token = get_token_from_email(
        user_data_2['email'], 'change-email')
    email = get_email_from_token(
        current_email_token, 'change-email', settings.CHANGE_EMAIL_EXPIRATION_TIME)
    assert email == user_data_2['email']
    new_email_token = get_token_from_email(new_email, 'change-email')
    email = get_email_from_token(
        new_email_token, 'change-email', settings.CHANGE_EMAIL_EXPIRATION_TIME)
    assert email == new_email
    args = {
        'current_email_token': current_email_token,
        'new_email_token': new_email_token
    }

    url = reverse('users:change-email', kwargs=args)
    perform_failed_email_change(client, user, url, request)


@pytest.mark.django_db
def test_current_email_another_user_get(client, valid_user_1, valid_user_2, valid_email3):
    perform_current_email_another_user(
        client, valid_user_1, valid_user_2, valid_email3, client.get)


@pytest.mark.django_db
def test_current_email_another_user_post(client, valid_user_1, valid_user_2, valid_email3):
    perform_current_email_another_user(
        client, valid_user_1, valid_user_2, valid_email3, client.post)


def perform_new_email_already_taken(client, user_data_1, user_data_2, request):
    user = create_activated_test_user(user_data_1)
    client.force_login(user)
    create_test_user(user_data_2)
    current_email_token = get_token_from_email(user.email, 'change-email')
    email = get_email_from_token(
        current_email_token, 'change-email', settings.CHANGE_EMAIL_EXPIRATION_TIME)
    assert email == user.email
    new_email_token = get_token_from_email(
        user_data_2['email'], 'change-email')
    email = get_email_from_token(
        new_email_token, 'change-email', settings.CHANGE_EMAIL_EXPIRATION_TIME)
    assert email == user_data_2['email']
    args = {
        'current_email_token': current_email_token,
        'new_email_token': new_email_token
    }

    url = reverse('users:change-email', kwargs=args)
    perform_failed_email_change(client, user, url, request)


@pytest.mark.django_db
def test_new_email_already_taken_get(client, valid_user_1, valid_user_2):
    perform_new_email_already_taken(
        client, valid_user_1, valid_user_2, client.get)


@pytest.mark.django_db
def test_new_email_already_taken_post(client, valid_user_1, valid_user_2):
    perform_new_email_already_taken(
        client, valid_user_1, valid_user_2, client.post)


def perform_user_deleted(client, user_data, new_email, request):
    user = create_deleted_test_user(user_data)
    client.force_login(user)
    user.emails.all().delete()
    create_change_email_confirmation(user, new_email)
    assert user.emails.count() == 1
    url = re.findall('(?<=href=").+?(?=")', user.emails.first().body)[0]
    perform_failed_email_change(client, user, url, request)


@pytest.mark.django_db
def test_user_deleted_get(client, valid_user_1, valid_user_2):
    perform_user_deleted(client, valid_user_1, valid_user_2, client.get)


@pytest.mark.django_db
def test_user_deleted_post(client, valid_user_1, valid_user_2):
    perform_user_deleted(client, valid_user_1, valid_user_2, client.post)
