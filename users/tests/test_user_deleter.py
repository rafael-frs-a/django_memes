import os
import pytest
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.files.images import ImageFile
from django.core.files.storage import default_storage
from services.user_deleter import delete_not_activated_users_expired_links, delete_users_delete_request
from posts.tests.test_utils import create_test_post
from .test_utils import create_test_user, create_activated_test_user, create_account_delete_requested_user


UserModel = get_user_model()


@pytest.mark.django_db
def test_not_activated_user_expired_link_deletion(valid_user_1):
    user = create_test_user(valid_user_1)
    user.created_at -= timezone.timedelta(
        hours=settings.ACCOUNT_ACTIVATION_EXPIRATION_TIME)
    user.save()
    delete_not_activated_users_expired_links()
    assert UserModel.objects.count() == 0


@pytest.mark.django_db
def test_not_activated_user_not_expired_link_deletion(valid_user_1):
    user = create_test_user(valid_user_1)
    delete_not_activated_users_expired_links()
    new_user = UserModel.objects.first()
    assert user == new_user


@pytest.mark.django_db
def test_activated_user_expired_link_deletion(valid_user_1):
    user = create_activated_test_user(valid_user_1)
    user.created_at -= timezone.timedelta(
        hours=settings.ACCOUNT_ACTIVATION_EXPIRATION_TIME)
    user.save()
    delete_not_activated_users_expired_links()
    new_user = UserModel.objects.first()
    assert user == new_user


@pytest.mark.django_db
def test_activated_user_not_expired_link_deletion(valid_user_1):
    user = create_activated_test_user(valid_user_1)
    delete_not_activated_users_expired_links()
    new_user = UserModel.objects.first()
    assert user == new_user


@pytest.mark.django_db
def test_not_activated_user_profile_pic(valid_user_1, valid_image_file):
    user = create_test_user(valid_user_1)
    current_path = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(current_path, 'images', valid_image_file)
    user.profile_pic = ImageFile(open(image_path, 'rb'))
    user.created_at -= timezone.timedelta(
        hours=settings.ACCOUNT_ACTIVATION_EXPIRATION_TIME)
    user.save()
    filename = user.profile_pic.name
    assert filename != UserModel.DEFAULT_PROFILE_PIC
    assert filename.startswith(UserModel.PROFILE_PICS_FOLDER)
    assert default_storage.exists(filename)
    delete_not_activated_users_expired_links()
    assert UserModel.objects.count() == 0
    assert not default_storage.exists(filename)
    assert os.path.exists(os.path.join(
        settings.MEDIA_ROOT, UserModel.DEFAULT_PROFILE_PIC))


@pytest.mark.django_db
def test_user_account_delete_required_expired(valid_user_1, valid_image_file):
    user = create_account_delete_requested_user(valid_user_1)
    assert user.delete_requested_at
    assert user.emails.count() == 1
    login_id = user.login_id
    current_path = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(current_path, 'images', valid_image_file)
    user.profile_pic = ImageFile(open(image_path, 'rb'))
    user.delete_requested_at -= timezone.timedelta(
        hours=settings.ACCOUNT_DELETION_INTERVAL)
    user.save()
    filename = user.profile_pic.name
    assert filename != UserModel.DEFAULT_PROFILE_PIC
    assert filename.startswith(UserModel.PROFILE_PICS_FOLDER)
    assert default_storage.exists(filename)
    create_test_post(user, valid_image_file)
    assert user.posts.count() == 1
    delete_users_delete_request()
    user = UserModel.objects.filter(id=user.id).first()
    assert user.email == f'deleted.user.{user.id}@djangomemes.com'
    assert user.login_id != login_id
    assert user.deleted
    assert user.emails.count() == 0
    assert user.posts.count() == 0
    assert user.profile_pic.name == UserModel.DEFAULT_PROFILE_PIC
    assert not default_storage.exists(filename)


@pytest.mark.django_db
def test_user_account_delete_request_expired_already_deleted(valid_user_1):
    user = create_account_delete_requested_user(valid_user_1)
    login_id = user.login_id
    email = user.email
    user.deleted = True
    user.delete_requested_at -= timezone.timedelta(
        hours=settings.ACCOUNT_DELETION_INTERVAL)
    user.save()
    delete_users_delete_request()
    user = UserModel.objects.filter(id=user.id).first()
    assert user.email == email
    assert user.login_id == login_id
    assert user.deleted
