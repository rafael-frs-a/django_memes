import pytest
from time import sleep
from django.urls import reverse
from base.utils import inverse_case
from .test_utils import (create_test_user, create_activated_test_user,
                         create_banned_activated_test_user, create_banned_until_activated_test_user,
                         create_deleted_test_user)


def perform_login(client, user_data, final_url):
    url = reverse('users:login')
    response = client.post(url, user_data)
    assert response.status_code == 302
    assert response.url == reverse(final_url)


@pytest.mark.django_db
def test_login_username(client, valid_user_1):
    create_activated_test_user(valid_user_1)
    user_data = {'username': inverse_case(
        valid_user_1['username']), 'password': valid_user_1['password']}
    perform_login(client, user_data, 'posts:home')


@pytest.mark.django_db
def test_login_email(client, valid_user_3):
    create_activated_test_user(valid_user_3)
    user_data = {'username': inverse_case(
        valid_user_3['email']), 'password': valid_user_3['password']}
    perform_login(client, user_data, 'posts:home')


@pytest.mark.django_db
def test_login_missing_username(client, valid_user_1):
    create_activated_test_user(valid_user_1)
    user_data = {'password': valid_user_1['password']}
    perform_login(client, user_data, 'users:login')


@pytest.mark.django_db
def test_login_missing_password(client, valid_user_1):
    create_activated_test_user(valid_user_1)
    user_data = {'username': valid_user_1['username']}
    perform_login(client, user_data, 'users:login')


@pytest.mark.django_db
def test_login_wrong_username(client, valid_user_1, valid_user_2):
    create_activated_test_user(valid_user_1)
    user_data = {
        'username': valid_user_2['username'], 'password': valid_user_1['password']}
    perform_login(client, user_data, 'users:login')


@pytest.mark.django_db
def test_login_wrong_password(client, valid_user_1, valid_user_3):
    create_activated_test_user(valid_user_1)
    user_data = {
        'username': valid_user_1['username'], 'password': valid_user_3['password']}
    perform_login(client, user_data, 'users:login')


@pytest.mark.django_db
def test_user_not_activated(client, valid_user_1):
    create_test_user(valid_user_1)
    perform_login(client, valid_user_1, 'users:login')


@pytest.mark.django_db
def test_login_next_logout(client, valid_user_1):
    create_activated_test_user(valid_user_1)
    url = reverse('users:login') + '?next=/logout/'
    response = client.post(url, valid_user_1)
    assert response.status_code == 302
    assert response.url == reverse('posts:home')


@pytest.mark.django_db
def test_user_banned(client, valid_user_1):
    create_banned_activated_test_user(valid_user_1)
    user_data = {
        'username': valid_user_1['username'],
        'password': valid_user_1['password']
    }

    perform_login(client, user_data, 'users:login')


@pytest.mark.django_db
def test_user_banned_until(client, valid_user_1):
    create_banned_until_activated_test_user(valid_user_1, 60)
    user_data = {
        'username': valid_user_1['username'],
        'password': valid_user_1['password']
    }

    perform_login(client, user_data, 'users:login')


@pytest.mark.django_db
def test_user_banned_until_expired(client, valid_user_1):
    create_banned_until_activated_test_user(valid_user_1, 1)
    user_data = {
        'username': valid_user_1['username'],
        'password': valid_user_1['password']
    }

    sleep(1)
    perform_login(client, user_data, 'posts:home')


@pytest.mark.django_db
def test_user_deleted(client, valid_user_1):
    create_deleted_test_user(valid_user_1)
    user_data = {
        'username': valid_user_1['username'],
        'password': valid_user_1['password']
    }

    perform_login(client, user_data, 'users:login')
