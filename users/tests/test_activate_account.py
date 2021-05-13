import re
import pytest
from time import sleep
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.conf import settings
from emails.models import get_email_from_token, get_token_from_email
from .test_utils import create_test_user, create_activated_test_user


def perform_successful_account_activation(user_data, request):
    user = create_test_user(user_data)
    assert not user.activated_at
    url = re.findall('(?<=href=").+?(?=")', user.emails.first().body)[0]
    response = request(url)
    assert response.status_code == 302
    assert response.url == reverse('users:login')
    user = get_user_model().objects.first()
    assert user.is_active


@pytest.mark.django_db
def test_get_successful_account_activation(client, valid_user_1):
    perform_successful_account_activation(valid_user_1, client.get)


@pytest.mark.django_db
def test_post_successful_account_activation(client, valid_user_1):
    perform_successful_account_activation(valid_user_1, client.post)


def perform_invalid_token(user_data, request):
    user = create_test_user(user_data)
    assert not user.activated_at
    url = reverse('users:activate-account', kwargs={'token': 'token'})
    response = request(url)
    assert response.status_code == 302
    assert response.url == reverse('users:login')
    user = get_user_model().objects.first()
    assert not user.activated_at


@pytest.mark.django_db
def test_get_invalid_token(client, valid_user_1):
    perform_invalid_token(valid_user_1, client.get)


@pytest.mark.django_db
def test_post_invalid_token(client, valid_user_1):
    perform_invalid_token(valid_user_1, client.post)


def perform_valid_token_user_not_found(user_data, valid_email, request):
    user = create_test_user(user_data)
    assert not user.activated_at
    assert user.email != valid_email
    token = get_token_from_email(valid_email, 'account-activation')
    email = get_email_from_token(
        token, 'account-activation', settings.ACCOUNT_ACTIVATION_EXPIRATION_TIME)
    assert email == valid_email
    url = reverse('users:activate-account', kwargs={'token': token})
    response = request(url)
    assert response.status_code == 302
    assert response.url == reverse('users:login')
    user = get_user_model().objects.first()
    assert not user.activated_at


@pytest.mark.django_db
def test_get_valid_token_user_not_found(client, valid_user_1, valid_email2):
    perform_valid_token_user_not_found(valid_user_1, valid_email2, client.get)


@pytest.mark.django_db
def test_post_valid_token_user_not_found(client, valid_user_1, valid_email2):
    perform_valid_token_user_not_found(valid_user_1, valid_email2, client.post)


def perform_expired_token(user_data, request):
    user = create_test_user(user_data)
    assert not user.activated_at
    url = re.findall('(?<=href=").+?(?=")', user.emails.first().body)[0]
    expiration_time = settings.ACCOUNT_ACTIVATION_EXPIRATION_TIME
    settings.ACCOUNT_ACTIVATION_EXPIRATION_TIME = 0
    sleep(1)
    response = request(url)
    assert response.status_code == 302
    assert response.url == reverse('users:login')
    settings.ACCOUNT_ACTIVATION_EXPIRATION_TIME = expiration_time
    user = get_user_model().objects.first()
    assert not user.activated_at


@pytest.mark.django_db
def test_get_expired_token(client, valid_user_1):
    perform_expired_token(valid_user_1, client.get)


@pytest.mark.django_db
def test_post_expired_token(client, valid_user_1):
    perform_expired_token(valid_user_1, client.post)


def perform_user_already_activated(user_data, request):
    user = create_activated_test_user(user_data)
    assert user.activated_at
    activation_time = user.activated_at
    url = re.findall('(?<=href=").+?(?=")', user.emails.first().body)[0]
    sleep(1)
    response = request(url)
    assert response.status_code == 302
    assert response.url == reverse('users:login')
    user = get_user_model().objects.first()
    assert user.activated_at == activation_time


@pytest.mark.django_db
def test_get_user_already_activated(client, valid_user_1):
    perform_user_already_activated(valid_user_1, client.get)


@pytest.mark.django_db
def test_post_user_already_activated(client, valid_user_1):
    perform_user_already_activated(valid_user_1, client.post)
