import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from pytest_django.asserts import assertTemplateUsed
from .test_utils import create_activated_test_user, create_account_delete_requested_user

UserModel = get_user_model()


@pytest.mark.django_db
def test_render_template_cancel_delete_account(client, valid_user_1):
    user = create_account_delete_requested_user(valid_user_1)
    client.force_login(user)
    url = reverse('users:cancel-delete-account')
    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, 'users/cancel_delete_account.html')


def perform_delete_account_request_already_cancelled(client, user_data, request):
    user = create_activated_test_user(user_data)
    assert not user.delete_requested_at
    client.force_login(user)
    url = reverse('users:cancel-delete-account')
    response = request(url)
    assert response.status_code == 302
    assert response.url == reverse('users:account')
    user = UserModel.objects.filter(id=user.id).first()
    assert not user.delete_requested_at


@pytest.mark.django_db
def test_delete_account_request_already_cancelled_get(client, valid_user_1):
    perform_delete_account_request_already_cancelled(
        client, valid_user_1, client.get)


@pytest.mark.django_db
def test_delete_account_request_already_cancelled_post(client, valid_user_1):
    perform_delete_account_request_already_cancelled(
        client, valid_user_1, client.post)


@pytest.mark.django_db
def test_successful_cancel_delete_account(client, valid_user_1):
    user = create_account_delete_requested_user(valid_user_1)
    assert user.delete_requested_at
    client.force_login(user)
    url = reverse('users:cancel-delete-account')
    response = client.post(url)
    assert response.status_code == 302
    assert response.url == reverse('users:account')
    user = UserModel.objects.filter(id=user.id).first()
    assert not user.delete_requested_at
