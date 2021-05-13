import pytest


@pytest.fixture
def valid_user_1():
    return {
        'username': 'TestUser',
        'email': 'testuser@email.com',
        'password': 'mvps8xa0'
    }


@pytest.fixture
def valid_user_2():
    return {
        'username': 'user2',
        'email': 'user2@email.com',
        'password': 'mvps8xa0'
    }


@pytest.fixture
def valid_image_file_1():
    return 'image.PNG'


@pytest.fixture
def valid_image_file_2():
    return 'image.JPG'


@pytest.fixture
def long_image():
    return 'long_image.jpg'


@pytest.fixture
def wide_image():
    return 'wide_image.jpg'
