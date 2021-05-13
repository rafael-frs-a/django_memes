import pytest
from base.utils import inverse_case


@pytest.fixture
def valid_username1():
    return 'TestUser'


@pytest.fixture
def valid_username2():
    return '@second_user'


@pytest.fixture
def invalid_username():
    return 'Test User'


@pytest.fixture
def short_username():
    return 'abc'


@pytest.fixture
def long_username():
    return 'usernameusernameusernameusernameusernameu'


@pytest.fixture
def valid_email1():
    return 'testuser@email.com'


@pytest.fixture
def valid_email2():
    return 'seconduser@email.com'


@pytest.fixture
def valid_email3():
    return 'new_email@email.com'


@pytest.fixture
def invalid_email():
    return 'email'


@pytest.fixture
def valid_password1():
    return 'mvps8xa0'


@pytest.fixture
def valid_password2():
    return ' vps8xa '


@pytest.fixture
def password_similar_username1(valid_username1):
    return valid_username1.lower()


@pytest.fixture
def password_similar_email1(valid_email1):
    return valid_email1.upper()


@pytest.fixture
def short_password():
    return 'lavjo8x'


@pytest.fixture
def common_password():
    return 'password'


@pytest.fixture
def numeric_password():
    return '29387134'


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
def valid_user_3(valid_username1, valid_email1, valid_password2):
    return {
        'username': valid_username1,
        'email': valid_email1,
        'password': valid_password2
    }


@pytest.fixture
def user_missing_username(valid_email1, valid_password1):
    return {
        'email': valid_email1,
        'password': valid_password1
    }


@pytest.fixture
def user_missing_email(valid_username1, valid_password1):
    return {
        'username': valid_username1,
        'password': valid_password1
    }


@pytest.fixture
def user_missing_password(valid_username1, valid_email1):
    return {
        'username': valid_username1,
        'email': valid_email1
    }


@pytest.fixture
def user_invalid_username(invalid_username, valid_email1, valid_password1):
    return {
        'username': invalid_username,
        'email': valid_email1,
        'password': valid_password1
    }


@pytest.fixture
def user_short_username(short_username, valid_email1, valid_password1):
    return {
        'username': short_username,
        'email': valid_email1,
        'password': valid_password1
    }


@pytest.fixture
def user_long_username(long_username, valid_email1, valid_password1):
    return {
        'username': long_username,
        'email': valid_email1,
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
def user_password_similar_username(valid_username1, valid_email1, password_similar_username1):
    return {
        'username': valid_username1,
        'email': valid_email1,
        'password': password_similar_username1
    }


@pytest.fixture
def user_password_similar_email(valid_username1, valid_email1, password_similar_email1):
    return {
        'username': valid_username1,
        'email': valid_email1,
        'password': password_similar_email1
    }


@pytest.fixture
def user_short_password(valid_username1, valid_email1, short_password):
    return {
        'username': valid_username1,
        'email': valid_email1,
        'password': short_password
    }


@pytest.fixture
def user_common_password(valid_username1, valid_email1, common_password):
    return {
        'username': valid_username1,
        'email': valid_email1,
        'password': common_password
    }


@pytest.fixture
def user_numeric_password(valid_username1, valid_email1, numeric_password):
    return {
        'username': valid_username1,
        'email': valid_email1,
        'password': numeric_password
    }


@pytest.fixture
def user_repeating_username(valid_username1, valid_email2, valid_password1):
    return {
        'username': inverse_case(valid_username1),
        'email': valid_email2,
        'password': valid_password1
    }


@pytest.fixture
def user_repeating_email(valid_username2, valid_email1, valid_password1):
    return {
        'username': valid_username2,
        'email': inverse_case(valid_email1),
        'password': valid_password1
    }


@pytest.fixture
def valid_image_file():
    return 'image.PNG'
