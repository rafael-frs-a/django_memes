import pytest
from base.utils import inverse_case


@pytest.fixture
def valid_username1():
    return 'TestUser'


@pytest.fixture
def valid_username2():
    return '@second_user'


@pytest.fixture
def valid_email1():
    return 'testuser@email.com'


@pytest.fixture
def valid_email2():
    return 'seconduser@email.com'


@pytest.fixture
def valid_password1():
    return 'mvps8xa0'


@pytest.fixture
def valid_user_1(valid_username1, valid_email1, valid_password1):
    return {
        'username': valid_username1,
        'email': valid_email1,
        'password': valid_password1
    }


@pytest.fixture
def valid_user_2(valid_username2, valid_email2, valid_password1):
    return {
        'username': valid_username2,
        'email': valid_email2,
        'password': valid_password1
    }


@pytest.fixture
def short_denial_reason():
    return ''.join(['a'] * 9)


@pytest.fixture
def long_denial_reason():
    return ''.join(['a'] * 101)


@pytest.fixture
def valid_denial_reason_1():
    return ''.join(['a'] * 10)


@pytest.fixture
def valid_denial_reason_2():
    return ''.join(['b'] * 10)


@pytest.fixture
def repeated_denial_reason(valid_denial_reason_1):
    return inverse_case(valid_denial_reason_1)


@pytest.fixture
def valid_image_file():
    return 'image.JPG'
