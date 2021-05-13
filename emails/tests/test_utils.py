import pytest
from users.tests.test_utils import create_test_user


def create_email_test_user(user_data):
    return create_test_user(user_data)


@pytest.mark.django_db
def test_get_test_user(valid_user_1):
    user = create_email_test_user(valid_user_1)
    assert user.username == valid_user_1['username']
    assert user.email == valid_user_1['email']
    assert user.check_password(valid_user_1['password'])
