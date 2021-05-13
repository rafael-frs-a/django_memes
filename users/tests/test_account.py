import os
import pytest
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
from pytest_django.asserts import assertTemplateUsed
from .test_utils import create_test_user, create_activated_test_user

UserModel = get_user_model()


@pytest.mark.django_db
def test_render_template(client, valid_user_1):
    user = create_activated_test_user(valid_user_1)
    client.force_login(user)
    url = reverse('users:account')
    response = client.get(url)
    assertTemplateUsed(response, 'users/account.html')


def perform_account_request(client, change_data, final_url):
    url = reverse('users:account')
    response = client.post(url, change_data)
    assert response.status_code == 302
    assert response.url == reverse(final_url)


def perform_account_changes(client, user_data, change_data, final_url, delete_emails=False):
    user = create_activated_test_user(user_data)

    if delete_emails:
        user.emails.all().delete()

    client.force_login(user)
    perform_account_request(client, change_data, final_url)
    return user


def check_user_didnt_change(user):
    new_user = UserModel.objects.first()
    assert user == new_user
    assert user.username == new_user.username
    assert user.email == new_user.email
    assert user.password == new_user.password
    assert user.profile_pic == new_user.profile_pic


@pytest.mark.django_db
def test_no_changes_made(client, valid_user_1):
    user = perform_account_changes(client, valid_user_1, {}, 'posts:home')
    check_user_didnt_change(user)


@pytest.mark.django_db
def test_same_new_email(client, valid_user_1):
    change_data = {'new_email': valid_user_1['email']}
    user = perform_account_changes(client, valid_user_1, change_data, 'posts:home')
    check_user_didnt_change(user)


@pytest.mark.django_db
def test_invalid_new_email(client, valid_user_1, invalid_email):
    change_data = {'new_email': invalid_email}
    perform_account_changes(client, valid_user_1, change_data, 'users:account')


@pytest.mark.django_db
def test_valid_new_email_already_used(client, valid_user_1, valid_user_2):
    create_test_user(valid_user_2)
    change_data = {'new_email': valid_user_2['email']}
    perform_account_changes(client, valid_user_1, change_data, 'users:account')


@pytest.mark.django_db
def test_successful_new_email(client, valid_user_1, valid_email2):
    change_data = {'new_email': valid_email2}
    user = perform_account_changes(
        client, valid_user_1, change_data, 'posts:home', True)
    assert user.emails.count() == 1
    email = user.emails.first()
    assert email.recipients == valid_email2


@pytest.mark.django_db
def test_valid_new_password_current_not_informed(client, valid_user_1, valid_password2):
    change_data = {'new_password': valid_password2}
    perform_account_changes(client, valid_user_1, change_data, 'users:account')


@pytest.mark.django_db
def test_valid_new_password_incorrect_current_password(client, valid_user_1, valid_password2):
    change_data = {
        'current_password': valid_password2,
        'new_password': valid_password2
    }

    perform_account_changes(client, valid_user_1, change_data, 'users:account')


@pytest.mark.django_db
def test_new_password_same_current(client, valid_user_1):
    change_data = {
        'current_password': valid_user_1['password'],
        'new_password': valid_user_1['password']
    }

    perform_account_changes(client, valid_user_1, change_data, 'users:account')


@pytest.mark.django_db
def test_new_password_similar_username(client, valid_user_1, password_similar_username1):
    change_data = {
        'current_password': valid_user_1['password'],
        'new_password': password_similar_username1
    }

    perform_account_changes(client, valid_user_1, change_data, 'users:account')


@pytest.mark.django_db
def test_new_password_similar_email(client, valid_user_1, password_similar_email1):
    change_data = {
        'current_password': valid_user_1['password'],
        'new_password': password_similar_email1
    }

    perform_account_changes(client, valid_user_1, change_data, 'users:account')


@pytest.mark.django_db
def test_new_password_similar_new_email(client, valid_user_2, valid_email1, password_similar_email1):
    change_data = {
        'new_email': valid_email1,
        'current_password': valid_user_2['password'],
        'new_password': password_similar_email1
    }

    perform_account_changes(client, valid_user_2, change_data, 'users:account')


@pytest.mark.django_db
def test_new_password_short(client, valid_user_1, short_password):
    change_data = {
        'current_password': valid_user_1['password'],
        'new_password': short_password
    }

    perform_account_changes(client, valid_user_1, change_data, 'users:account')


@pytest.mark.django_db
def test_new_password_common(client, valid_user_1, common_password):
    change_data = {
        'current_password': valid_user_1['password'],
        'new_password': common_password
    }

    perform_account_changes(client, valid_user_1, change_data, 'users:account')


@pytest.mark.django_db
def test_new_password_numeric(client, valid_user_1, numeric_password):
    change_data = {
        'current_password': valid_user_1['password'],
        'new_password': numeric_password
    }

    perform_account_changes(client, valid_user_1, change_data, 'users:account')


@pytest.mark.django_db
def test_successful_new_password(client, valid_user_1, valid_password2):
    change_data = {
        'current_password': valid_user_1['password'],
        'new_password': valid_password2
    }

    user = perform_account_changes(client, valid_user_1, change_data, 'posts:home')
    new_user = UserModel.objects.first()
    assert user == new_user
    assert user.username == new_user.username
    assert user.email == new_user.email
    assert user.password != new_user.password
    assert user.profile_pic == new_user.profile_pic
    assert new_user.check_password(valid_password2)


@pytest.mark.django_db
@pytest.mark.parametrize('image', [
    'image.TXT',
    'image.BMP'
])
def test_invalid_images(client, valid_user_1, image):
    current_path = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(current_path, 'images', image)

    with open(image_path, 'rb') as img:
        change_data = {
            'profile_pic': img
        }

        perform_account_changes(client, valid_user_1, change_data, 'users:account')


@pytest.mark.django_db
@pytest.mark.parametrize('image', [
    'image.PNG',
    'image.JPG',
    'image.JPEG'
])
def test_valid_images(client, valid_user_1, image):
    current_path = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(current_path, 'images', image)

    with open(image_path, 'rb') as img:
        change_data = {
            'profile_pic': img
        }

        user = perform_account_changes(
            client, valid_user_1, change_data, 'posts:home')
        new_user = UserModel.objects.first()
        assert user == new_user
        assert user.username == new_user.username
        assert user.email == new_user.email
        assert user.password == new_user.password
        assert user.profile_pic != new_user.profile_pic
        assert default_storage.exists(new_user.profile_pic.name)

    assert os.path.exists(os.path.join(
        settings.MEDIA_ROOT, UserModel.DEFAULT_PROFILE_PIC))


@pytest.mark.django_db
def test_change_profile_pic_twice(client, valid_user_1, valid_image_file):
    current_path = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(current_path, 'images', valid_image_file)

    with open(image_path, 'rb') as img:
        change_data = {
            'profile_pic': img
        }

        user = perform_account_changes(
            client, valid_user_1, change_data, 'posts:home')
        new_user = UserModel.objects.first()
        assert user == new_user
        assert user.profile_pic != new_user.profile_pic
        assert default_storage.exists(new_user.profile_pic.name)
        old_profile_pic = new_user.profile_pic

    with open(image_path, 'rb') as img:
        change_data = {
            'profile_pic': img
        }

        perform_account_request(client, change_data, 'posts:home')
        new_user = UserModel.objects.first()
        assert user == new_user
        assert user.profile_pic != new_user.profile_pic
        assert new_user.profile_pic != old_profile_pic
        assert not default_storage.exists(old_profile_pic.name)
        assert default_storage.exists(new_user.profile_pic.name)

    assert os.path.exists(os.path.join(
        settings.MEDIA_ROOT, UserModel.DEFAULT_PROFILE_PIC))


@pytest.mark.django_db
def test_change_profile_pic_once_keep(client, valid_user_1, valid_image_file, valid_email2):
    current_path = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(current_path, 'images', valid_image_file)

    with open(image_path, 'rb') as img:
        change_data = {
            'profile_pic': img
        }

        user = perform_account_changes(
            client, valid_user_1, change_data, 'posts:home')
        new_user = UserModel.objects.first()
        assert user == new_user
        assert user.profile_pic != new_user.profile_pic
        assert default_storage.exists(new_user.profile_pic.name)
        old_profile_pic = new_user.profile_pic

    change_data = {
        'new_email': valid_email2
    }

    user.emails.all().delete()
    perform_account_request(client, change_data, 'posts:home')
    new_user = UserModel.objects.first()
    assert user == new_user
    assert new_user.emails.count() == 1
    assert new_user.profile_pic == old_profile_pic
    assert default_storage.exists(new_user.profile_pic.name)
    assert os.path.exists(os.path.join(
        settings.MEDIA_ROOT, UserModel.DEFAULT_PROFILE_PIC))
