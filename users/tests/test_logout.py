import pytest
from django.urls import reverse
from .test_utils import create_activated_test_user


def perform_successful_logout(client, user_data, request):
    user = create_activated_test_user(user_data)
    client.force_login(user)
    url = reverse('users:logout')
    response = request(url)
    assert response.status_code == 302
    assert response.url == reverse('posts:home')


@pytest.mark.django_db
def test_logout_authenticated_user(client, valid_user_1):
    perform_successful_logout(client, valid_user_1, client.get)


@pytest.mark.django_db
def test_post_logout_authenticated_user(client, valid_user_1):
    perform_successful_logout(client, valid_user_1, client.post)
