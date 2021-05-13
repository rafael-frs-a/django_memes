import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from emails.models import Email
from .test_utils import create_test_user


def perform_successful_register(client, user_data, initial_count=0):
    UserModel = get_user_model()
    assert UserModel.objects.count() == initial_count
    assert Email.objects.count() == initial_count
    url = reverse('users:register')
    response = client.post(url, user_data)
    assert UserModel.objects.count() == initial_count + 1
    assert Email.objects.count() == initial_count + 1
    user = UserModel.objects.filter(username=user_data['username']).first()
    assert user.emails.count() == 1
    assert response.status_code == 302
    assert response.url == reverse('users:login')


def perform_failed_register(client, user_data, initial_count=0):
    UserModel = get_user_model()
    assert UserModel.objects.count() == initial_count
    assert Email.objects.count() == initial_count
    url = reverse('users:register')
    response = client.post(url, user_data)
    assert UserModel.objects.count() == initial_count
    assert Email.objects.count() == initial_count
    assert response.status_code == 302
    assert response.url == reverse('users:register')


@pytest.mark.django_db
def test_valid_user_1(client, valid_user_1):
    perform_successful_register(client, valid_user_1)


@pytest.mark.django_db
def test_valid_user_2(client, valid_user_1, valid_user_2):
    create_test_user(valid_user_1)
    perform_successful_register(client, valid_user_2, 1)


@pytest.mark.django_db
def test_valid_user_3(client, valid_user_3):
    perform_successful_register(client, valid_user_3)


@pytest.mark.django_db
def test_user_missing_username(client, user_missing_username):
    perform_failed_register(client, user_missing_username)


@pytest.mark.django_db
def test_user_missing_email(client, user_missing_email):
    perform_failed_register(client, user_missing_email)


@pytest.mark.django_db
def test_user_missing_password(client, user_missing_password):
    perform_failed_register(client, user_missing_password)


@pytest.mark.django_db
def test_user_invalid_username(client, user_invalid_username):
    perform_failed_register(client, user_invalid_username)


@pytest.mark.django_db
def test_user_short_username(client, user_short_username):
    perform_failed_register(client, user_short_username)


@pytest.mark.django_db
def test_user_long_username(client, user_long_username):
    perform_failed_register(client, user_long_username)


@pytest.mark.django_db
def test_user_invalid_email(client, user_invalid_email):
    perform_failed_register(client, user_invalid_email)


@pytest.mark.django_db
def test_user_password_similar_username(client, user_password_similar_username):
    perform_failed_register(client, user_password_similar_username)


@pytest.mark.django_db
def test_user_password_similar_email(client, user_password_similar_email):
    perform_failed_register(client, user_password_similar_email)


@pytest.mark.django_db
def test_user_short_password(client, user_short_password):
    perform_failed_register(client, user_short_password)


@pytest.mark.django_db
def test_user_common_password(client, user_common_password):
    perform_failed_register(client, user_common_password)


@pytest.mark.django_db
def test_user_numeric_password(client, user_numeric_password):
    perform_failed_register(client, user_numeric_password)


@pytest.mark.django_db
def test_user_repeating_username(client, valid_user_1, user_repeating_username):
    create_test_user(valid_user_1)
    perform_failed_register(client, user_repeating_username, 1)


@pytest.mark.django_db
def test_user_repeating_email(client, valid_user_1, user_repeating_email):
    create_test_user(valid_user_1)
    perform_failed_register(client, user_repeating_email, 1)
