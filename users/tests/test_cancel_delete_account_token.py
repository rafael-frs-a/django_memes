import re
import pytest
from time import sleep
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from emails.models import get_token_from_email, get_email_from_token
from .test_utils import create_account_delete_requested_user, create_activated_test_user

UserModel = get_user_model()


def perform_successful_cancel_delete_account_token_logged_out(client, user_data, request):
    user = create_account_delete_requested_user(user_data)
    assert user.delete_requested_at
    url = re.findall('(?<=href=").+?(?=")', user.emails.first().body)[0]
    response = request(url)
    assert response.status_code == 302
    assert response.url == reverse('posts:home')
    user = UserModel.objects.filter(id=user.id).first()
    assert not user.delete_requested_at


def perform_successful_cancel_delete_account_token_logged_in(client, user_data, request):
    user = create_account_delete_requested_user(user_data)
    assert user.delete_requested_at
    client.force_login(user)
    url = re.findall('(?<=href=").+?(?=")', user.emails.first().body)[0]
    response = request(url)
    assert response.status_code == 302
    assert response.url == reverse('users:account')
    user = UserModel.objects.filter(id=user.id).first()
    assert not user.delete_requested_at


@pytest.mark.django_db
def test_successful_cancel_delete_account_token_get_logged_out(client, valid_user_1):
    perform_successful_cancel_delete_account_token_logged_out(
        client, valid_user_1, client.get)


@pytest.mark.django_db
def test_successful_cancel_delete_account_token_post_logged_out(client, valid_user_1):
    perform_successful_cancel_delete_account_token_logged_out(
        client, valid_user_1, client.post)


@pytest.mark.django_db
def test_successful_cancel_delete_account_token_get_logged_in(client, valid_user_1):
    perform_successful_cancel_delete_account_token_logged_in(
        client, valid_user_1, client.get)


@pytest.mark.django_db
def test_successful_cancel_delete_account_token_post_logged_in(client, valid_user_1):
    perform_successful_cancel_delete_account_token_logged_in(
        client, valid_user_1, client.post)


@pytest.mark.django_db
def test_invalid_token_logged_out_get(client, valid_user_1):
    user = create_account_delete_requested_user(valid_user_1)
    url = reverse('users:cancel-delete-account-token',
                  kwargs={'token': 'token'})
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == reverse('posts:home')
    user = UserModel.objects.filter(id=user.id).first()
    assert user.delete_requested_at


@pytest.mark.django_db
def test_invalid_token_logged_out_post(client, valid_user_1):
    user = create_account_delete_requested_user(valid_user_1)
    url = reverse('users:cancel-delete-account-token',
                  kwargs={'token': 'token'})
    response = client.post(url)
    assert response.status_code == 302
    assert response.url == reverse('posts:home')
    user = UserModel.objects.filter(id=user.id).first()
    assert user.delete_requested_at


@pytest.mark.django_db
def test_invalid_token_logged_in_get(client, valid_user_1):
    user = create_account_delete_requested_user(valid_user_1)
    client.force_login(user)
    url = reverse('users:cancel-delete-account-token',
                  kwargs={'token': 'token'})
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == reverse('users:account')
    user = UserModel.objects.filter(id=user.id).first()
    assert user.delete_requested_at


@pytest.mark.django_db
def test_invalid_token_logged_in_post(client, valid_user_1):
    user = create_account_delete_requested_user(valid_user_1)
    client.force_login(user)
    url = reverse('users:cancel-delete-account-token',
                  kwargs={'token': 'token'})
    response = client.post(url)
    assert response.status_code == 302
    assert response.url == reverse('users:account')
    user = UserModel.objects.filter(id=user.id).first()
    assert user.delete_requested_at


@pytest.mark.django_db
def test_expired_token_logged_out_get(client, valid_user_1):
    user = create_account_delete_requested_user(valid_user_1)
    url = re.findall('(?<=href=").+?(?=")', user.emails.first().body)[0]
    account_deletion_interval = settings.ACCOUNT_DELETION_INTERVAL
    settings.ACCOUNT_DELETION_INTERVAL = 0
    sleep(1)
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == reverse('posts:home')
    user = UserModel.objects.filter(id=user.id).first()
    assert user.delete_requested_at
    settings.ACCOUNT_DELETION_INTERVAL = account_deletion_interval


@pytest.mark.django_db
def test_expired_token_logged_out_post(client, valid_user_1):
    user = create_account_delete_requested_user(valid_user_1)
    url = re.findall('(?<=href=").+?(?=")', user.emails.first().body)[0]
    account_deletion_interval = settings.ACCOUNT_DELETION_INTERVAL
    settings.ACCOUNT_DELETION_INTERVAL = 0
    sleep(1)
    response = client.post(url)
    assert response.status_code == 302
    assert response.url == reverse('posts:home')
    user = UserModel.objects.filter(id=user.id).first()
    assert user.delete_requested_at
    settings.ACCOUNT_DELETION_INTERVAL = account_deletion_interval


@pytest.mark.django_db
def test_expired_token_logged_in_get(client, valid_user_1):
    user = create_account_delete_requested_user(valid_user_1)
    client.force_login(user)
    url = re.findall('(?<=href=").+?(?=")', user.emails.first().body)[0]
    account_deletion_interval = settings.ACCOUNT_DELETION_INTERVAL
    settings.ACCOUNT_DELETION_INTERVAL = 0
    sleep(1)
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == reverse('users:account')
    user = UserModel.objects.filter(id=user.id).first()
    assert user.delete_requested_at
    settings.ACCOUNT_DELETION_INTERVAL = account_deletion_interval


@pytest.mark.django_db
def test_expired_token_logged_in_post(client, valid_user_1):
    user = create_account_delete_requested_user(valid_user_1)
    client.force_login(user)
    url = re.findall('(?<=href=").+?(?=")', user.emails.first().body)[0]
    account_deletion_interval = settings.ACCOUNT_DELETION_INTERVAL
    settings.ACCOUNT_DELETION_INTERVAL = 0
    sleep(1)
    response = client.post(url)
    assert response.status_code == 302
    assert response.url == reverse('users:account')
    user = UserModel.objects.filter(id=user.id).first()
    assert user.delete_requested_at
    settings.ACCOUNT_DELETION_INTERVAL = account_deletion_interval


@pytest.mark.django_db
def test_valid_token_user_not_found_logged_out_get(client, valid_user_1, valid_email2):
    user = create_account_delete_requested_user(valid_user_1)
    assert user.email != valid_email2
    token = get_token_from_email(valid_email2, 'cancel-delete-account')
    email = get_email_from_token(
        token, 'cancel-delete-account', settings.ACCOUNT_DELETION_INTERVAL)
    assert email == valid_email2
    url = reverse('users:cancel-delete-account-token', kwargs={'token': token})
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == reverse('posts:home')
    user = UserModel.objects.filter(id=user.id).first()
    assert user.delete_requested_at


@pytest.mark.django_db
def test_valid_token_user_not_found_logged_out_post(client, valid_user_1, valid_email2):
    user = create_account_delete_requested_user(valid_user_1)
    assert user.email != valid_email2
    token = get_token_from_email(valid_email2, 'cancel-delete-account')
    email = get_email_from_token(
        token, 'cancel-delete-account', settings.ACCOUNT_DELETION_INTERVAL)
    assert email == valid_email2
    url = reverse('users:cancel-delete-account-token', kwargs={'token': token})
    response = client.post(url)
    assert response.status_code == 302
    assert response.url == reverse('posts:home')
    user = UserModel.objects.filter(id=user.id).first()
    assert user.delete_requested_at


@pytest.mark.django_db
def test_valid_token_user_not_found_logged_in_get(client, valid_user_1, valid_email2):
    user = create_account_delete_requested_user(valid_user_1)
    client.force_login(user)
    assert user.email != valid_email2
    token = get_token_from_email(valid_email2, 'cancel-delete-account')
    email = get_email_from_token(
        token, 'cancel-delete-account', settings.ACCOUNT_DELETION_INTERVAL)
    assert email == valid_email2
    url = reverse('users:cancel-delete-account-token', kwargs={'token': token})
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == reverse('users:account')
    user = UserModel.objects.filter(id=user.id).first()
    assert user.delete_requested_at


@pytest.mark.django_db
def test_valid_token_user_not_found_logged_in_post(client, valid_user_1, valid_email2):
    user = create_account_delete_requested_user(valid_user_1)
    client.force_login(user)
    assert user.email != valid_email2
    token = get_token_from_email(valid_email2, 'cancel-delete-account')
    email = get_email_from_token(
        token, 'cancel-delete-account', settings.ACCOUNT_DELETION_INTERVAL)
    assert email == valid_email2
    url = reverse('users:cancel-delete-account-token', kwargs={'token': token})
    response = client.post(url)
    assert response.status_code == 302
    assert response.url == reverse('users:account')
    user = UserModel.objects.filter(id=user.id).first()
    assert user.delete_requested_at


def perform_valid_token_user_unable_login(client, user, request):
    assert user.delete_requested_at
    url = re.findall('(?<=href=").+?(?=")', user.emails.first().body)[0]
    response = request(url)
    assert response.status_code == 302
    assert response.url == reverse('posts:home')
    user = UserModel.objects.filter(id=user.id).first()
    assert not user.delete_requested_at


@pytest.mark.django_db
def test_user_not_activated_get(client, valid_user_1):
    user = create_account_delete_requested_user(valid_user_1)
    user.activated_at = None
    user.save()
    assert not user.is_active
    perform_valid_token_user_unable_login(client, user, client.get)


@pytest.mark.django_db
def test_user_not_activated_post(client, valid_user_1):
    user = create_account_delete_requested_user(valid_user_1)
    user.activated_at = None
    user.save()
    assert not user.is_active
    perform_valid_token_user_unable_login(client, user, client.post)


@pytest.mark.django_db
def test_user_banned_get(client, valid_user_1):
    user = create_account_delete_requested_user(valid_user_1)
    user.banned = True
    user.save()
    assert user.banned
    perform_valid_token_user_unable_login(client, user, client.get)


@pytest.mark.django_db
def test_user_banned_post(client, valid_user_1):
    user = create_account_delete_requested_user(valid_user_1)
    user.banned = True
    user.save()
    assert user.banned
    perform_valid_token_user_unable_login(client, user, client.post)


@pytest.mark.django_db
def test_user_banned_until_get(client, valid_user_1):
    user = create_account_delete_requested_user(valid_user_1)
    user.banned_until = timezone.now() + timezone.timedelta(minutes=2)
    user.save()
    assert user.banned_until
    perform_valid_token_user_unable_login(client, user, client.get)


@pytest.mark.django_db
def test_user_banned_until_post(client, valid_user_1):
    user = create_account_delete_requested_user(valid_user_1)
    user.banned_until = timezone.now() + timezone.timedelta(minutes=2)
    user.save()
    assert user.banned_until
    perform_valid_token_user_unable_login(client, user, client.post)


def perform_valid_token_logged_another_user(client, user_data_1, user_data_2, request):
    user1 = create_account_delete_requested_user(user_data_1)
    user2 = create_activated_test_user(user_data_2)
    client.force_login(user2)
    url = re.findall('(?<=href=").+?(?=")', user1.emails.first().body)[0]
    response = request(url)
    assert response.status_code == 302
    assert response.url == reverse('users:account')
    user1 = UserModel.objects.filter(id=user1.id).first()
    assert user1.delete_requested_at


@pytest.mark.django_db
def test_valid_token_logged_another_user_get(client, valid_user_1, valid_user_2):
    perform_valid_token_logged_another_user(
        client, valid_user_1, valid_user_2, client.get)


@pytest.mark.django_db
def test_valid_token_logged_another_user_post(client, valid_user_1, valid_user_2):
    perform_valid_token_logged_another_user(
        client, valid_user_1, valid_user_2, client.post)
