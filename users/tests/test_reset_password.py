import pytest
from time import sleep
from django.urls import reverse
from base.utils import inverse_case
from .test_utils import (create_test_user, create_activated_test_user,
                         create_banned_activated_test_user, create_banned_until_activated_test_user,
                         create_deleted_test_user)


def perform_reset_password(client, user_data, final_url):
    url = reverse('users:reset-password')
    response = client.post(url, user_data)
    assert response.status_code == 302
    assert response.url == reverse(final_url)


def perform_successful_reset_password(client, user, user_data):
    perform_reset_password(client, user_data, 'users:login')
    assert user.emails.count() == 2


def perform_failed_reset_password(client, user, user_data):
    perform_reset_password(client, {}, 'users:reset-password')
    assert user.emails.count() == 1


@pytest.mark.django_db
def test_successful_reset_password(client, valid_user_1):
    user = create_activated_test_user(valid_user_1)
    user_data = {'email': inverse_case(valid_user_1['email'])}
    perform_successful_reset_password(client, user, user_data)


@pytest.mark.django_db
def test_reset_password_missing_email(client, valid_user_1):
    user = create_activated_test_user(valid_user_1)
    perform_failed_reset_password(client, user, {})


@pytest.mark.django_db
def test_reset_password_not_activated_user(client, valid_user_1):
    user = create_test_user(valid_user_1)
    user_data = {'email': valid_user_1['email']}
    perform_failed_reset_password(client, user, user_data)


@pytest.mark.django_db
def test_reset_password_user_not_found(client, valid_user_1, valid_email2):
    user = create_activated_test_user(valid_user_1)
    user_data = {'email': valid_email2}
    perform_failed_reset_password(client, user, user_data)


@pytest.mark.django_db
def test_reset_password_invalid_email(client, valid_user_1, invalid_email):
    user = create_activated_test_user(valid_user_1)
    user.email = invalid_email
    user.save()
    assert user.email == invalid_email
    user_data = {'email': invalid_email}
    perform_failed_reset_password(client, user, user_data)


@pytest.mark.django_db
def test_user_banned(client, valid_user_1):
    user = create_banned_activated_test_user(valid_user_1)
    user_data = {'email': valid_user_1['email']}
    perform_failed_reset_password(client, user, user_data)


@pytest.mark.django_db
def test_user_banned_until(client, valid_user_1):
    user = create_banned_until_activated_test_user(valid_user_1, 60)
    user_data = {'email': valid_user_1['email']}
    perform_failed_reset_password(client, user, user_data)


@pytest.mark.django_db
def test_user_banned_until_expired(client, valid_user_1):
    user = create_banned_until_activated_test_user(valid_user_1, 1)
    sleep(1)
    user_data = {'email': valid_user_1['email']}
    perform_successful_reset_password(client, user, user_data)


@pytest.mark.django_db
def test_user_deleted(client, valid_user_1):
    user = create_deleted_test_user(valid_user_1)
    user_data = {
        'email': valid_user_1['email']
    }

    perform_failed_reset_password(client, user, user_data)
