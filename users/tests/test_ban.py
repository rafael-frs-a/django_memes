import pytest
from pytest_django.asserts import assertTemplateUsed
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
from .test_utils import create_activated_test_user

UserModel = get_user_model()


def check_login(client):
    url = reverse('users:account')
    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, 'users/account.html')


def check_logout(client):
    url = reverse('users:account')
    response = client.get(url)
    assert response.status_code == 302
    assert response.url.startswith(reverse('users:login'))


def peform_login(client, user):
    client.force_login(user)
    check_login(client)


@pytest.mark.django_db
def test_banned(client, valid_user_1):
    user = create_activated_test_user(valid_user_1)
    peform_login(client, user)
    old_login_id = user.login_id
    assert not user.banned
    assert not user.banned_until
    user.banned = True
    user.save()
    assert user.banned
    assert old_login_id != user.login_id
    check_logout(client)


@pytest.mark.django_db
def test_banned_until(client, valid_user_1):
    user = create_activated_test_user(valid_user_1)
    peform_login(client, user)
    old_login_id = user.login_id
    assert not user.banned
    assert not user.banned_until
    user.banned_until = timezone.now() + timezone.timedelta(seconds=60)
    user.save()
    assert user.banned_until
    assert old_login_id != user.login_id
    check_logout(client)


@pytest.mark.django_db
def test_banned_until_expired(client, valid_user_1):
    user = create_activated_test_user(valid_user_1)
    peform_login(client, user)
    old_login_id = user.login_id
    assert not user.banned
    assert not user.banned_until
    user.banned_until = timezone.now() - timezone.timedelta(seconds=60)
    user.save()
    assert user.banned_until
    assert old_login_id == user.login_id
    check_login(client)
