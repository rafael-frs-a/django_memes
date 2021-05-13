import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone
from emails.models import Email
from ..models import User

UserModel = get_user_model()


def create_test_user(user_data, is_active=False, is_staff=False,
                     is_moderator=False, is_banned=False, banned_seconds=0):
    user_data['is_active'] = is_active
    user_data['is_staff'] = is_staff
    user_data['is_banned'] = is_banned
    user_data['is_moderator'] = is_moderator
    user_data['banned_seconds'] = banned_seconds
    user = UserModel.objects.create_user(**user_data)
    return user


@pytest.mark.django_db
def test_create_test_user(valid_user_1):
    user = create_test_user(valid_user_1)
    assert UserModel.objects.count() == 1
    assert Email.objects.count() == 1
    assert user.emails.count() == 1
    assert user.profile_pic == User.DEFAULT_PROFILE_PIC
    assert not user.is_active
    assert not user.is_staff


def create_activated_test_user(user_data):
    user = create_test_user(user_data, is_active=True)
    return user


@pytest.mark.django_db
def test_create_activated_test_user(valid_user_1):
    user = create_activated_test_user(valid_user_1)
    assert user.is_active
    assert not user.is_staff


def create_admin_test_user(user_data):
    user = create_test_user(user_data, is_active=True, is_staff=True)
    return user


@pytest.mark.django_db
def test_create_admin_test_user(valid_user_1):
    user = create_admin_test_user(valid_user_1)
    assert user.is_active
    group = Group.objects.first()
    assert group.name == 'admin'
    assert user.is_staff


def create_banned_activated_test_user(user_data):
    user = create_test_user(user_data, is_active=True, is_banned=True)
    return user


@pytest.mark.django_db
def test_create_banned_activated_test_user(valid_user_1):
    user = create_banned_activated_test_user(valid_user_1)
    assert user.is_active
    assert user.banned


def create_banned_until_activated_test_user(user_data, seconds):
    user = create_test_user(user_data, is_active=True, banned_seconds=seconds)
    return user


@pytest.mark.django_db
def test_create_banned_until_activated_test_user(valid_user_1):
    user = create_banned_until_activated_test_user(valid_user_1, 1)
    assert user.is_active
    assert user.banned_until


def create_account_delete_requested_user(user_data):
    user = create_activated_test_user(user_data)
    user.emails.all().delete()
    user.delete_requested_at = timezone.now()
    user.save()
    return user


@pytest.mark.django_db
def test_create_account_delete_requested_user(valid_user_1):
    user = create_account_delete_requested_user(valid_user_1)
    assert user.delete_requested_at
    assert user.emails.count() == 1


def create_deleted_test_user(user_data):
    user = create_activated_test_user(user_data)
    user.deleted = True
    user.save()
    return user


@pytest.mark.django_db
def test_create_deleted_test_user(valid_user_1):
    user = create_deleted_test_user(valid_user_1)
    assert user.deleted
