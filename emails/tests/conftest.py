import pytest


@pytest.fixture
def valid_username1():
    return 'TestUser'


@pytest.fixture
def valid_email1():
    return 'testuser@email.com'


@pytest.fixture
def valid_email2():
    return 'seconduser@email.com'


@pytest.fixture
def invalid_email():
    return 'email'


@pytest.fixture
def valid_password1():
    return 'mvps8xa0'


@pytest.fixture
def user_missing_email(valid_username1, valid_password1):
    return {
        'username': valid_username1,
        'password': valid_password1
    }


@pytest.fixture
def user_invalid_email(valid_username1, invalid_email, valid_password1):
    return {
        'username': valid_username1,
        'email': invalid_email,
        'password': valid_password1
    }


@pytest.fixture
def valid_user_1(valid_username1, valid_email1, valid_password1):
    return {
        'username': valid_username1,
        'email': valid_email1,
        'password': valid_password1
    }
