import pytest
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed
from .test_utils import create_admin_test_user, create_activated_test_user


def get_login_url(client):
    url = reverse('admin:index')
    response = client.get(url, follow=True)
    return response.redirect_chain[-1][0]


def test_admin_redirect_login(client):
    url = get_login_url(client)
    assert url.startswith(reverse('users:login'))


@pytest.mark.django_db
def test_successful_admin_login(client, valid_user_1):
    create_admin_test_user(valid_user_1)
    url = get_login_url(client)
    response = client.post(url, valid_user_1, follow=True)
    assert response.status_code == 200
    assert response.redirect_chain[-1][0] == reverse('admin:index')


@pytest.mark.django_db
def test_user_not_admin_login(client, valid_user_1):
    create_activated_test_user(valid_user_1)
    url = get_login_url(client)
    response = client.post(url, valid_user_1, follow=True)
    assert response.status_code == 403
    assertTemplateUsed(response, 'errors/403.html')


@pytest.mark.django_db
def test_admin_logout(client, valid_user_1):
    user = create_admin_test_user(valid_user_1)
    client.force_login(user)
    url = reverse('admin:logout')
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == reverse('posts:home')
