import pytest
from time import sleep
from django.urls import reverse
from django.contrib.auth import get_user_model
from pytest_django.asserts import assertTemplateUsed
from .test_utils import create_activated_test_user, create_account_delete_requested_user

UserModel = get_user_model()


@pytest.mark.django_db
def test_render_delete_account_template(client, valid_user_1):
    user = create_activated_test_user(valid_user_1)
    client.force_login(user)
    url = reverse('users:delete-account')
    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, 'users/delete_account.html')


def perform_delete_account_already_requestd(client, user_data, request):
    user = create_account_delete_requested_user(user_data)
    delete_requested_at = user.delete_requested_at
    client.force_login(user)
    url = reverse('users:delete-account')
    sleep(1)
    response = request(url)
    assert response.status_code == 302
    assert response.url == reverse('users:account')
    user = UserModel.objects.filter(id=user.id).first()
    assert user.delete_requested_at == delete_requested_at


@pytest.mark.django_db
def test_delete_account_already_requested_get(client, valid_user_1):
    perform_delete_account_already_requestd(client, valid_user_1, client.get)


@pytest.mark.django_db
def test_delete_account_already_requested_post(client, valid_user_1):
    perform_delete_account_already_requestd(client, valid_user_1, client.post)


@pytest.mark.django_db
def test_successful_delete_account_request(client, valid_user_1):
    user = create_activated_test_user(valid_user_1)
    assert not user.delete_requested_at
    client.force_login(user)
    user.emails.all().delete()
    url = reverse('users:delete-account')
    response = client.post(url)
    assert response.status_code == 302
    assert response.url == reverse('users:account')
    user = UserModel.objects.filter(id=user.id).first()
    assert user.delete_requested_at
    assert user.emails.count() == 1
