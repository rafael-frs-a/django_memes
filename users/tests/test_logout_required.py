import pytest
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed
from .test_utils import create_activated_test_user


@pytest.mark.django_db
@pytest.mark.parametrize('view', [
    ('users:register', {}, 'users/register.html'),
    ('users:login', {}, 'users/login.html'),
    ('users:activate-account', {'token': 'token'}, 'users/login.html'),
    ('users:reset-password', {}, 'users/reset_password.html'),
    ('users:reset-password-token', {'token': 'token'}, 'users/login.html')
])
def test_successful_logout_required_request(client, view):
    url = reverse(view[0], kwargs=view[1])
    response = client.get(url, follow=True)
    assert response.status_code == 200
    assertTemplateUsed(response, view[2])
    response = client.post(url, follow=True)
    assert response.status_code == 200
    assertTemplateUsed(response, view[2])


@pytest.mark.django_db
@pytest.mark.parametrize('view', [
    ('users:register', {}),
    ('users:login', {}),
    ('users:activate-account', {'token': 'token'}),
    ('users:reset-password', {}),
    ('users:reset-password-token', {'token': 'token'})
])
def test_failed_logout_required_request(client, view, valid_user_1):
    user = create_activated_test_user(valid_user_1)
    client.force_login(user)
    url = reverse(view[0], kwargs=view[1])
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == reverse('posts:home')
    response = client.post(url)
    assert response.status_code == 302
    assert response.url == reverse('posts:home')
