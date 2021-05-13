import os
import pytest
from django.contrib.auth.models import Group
from django.core.files import File
from users.tests.test_utils import create_test_user
from posts.models import Post
from ..models import PostDenialReason


def create_moderator_test_user(user_data):
    user = create_test_user(user_data, is_active=True, is_moderator=True)
    return user


@pytest.mark.django_db
def test_create_moderator_test_user(valid_user_1):
    user = create_moderator_test_user(valid_user_1)
    assert user.is_active
    group = Group.objects.first()
    assert group.name == 'moderator'
    assert user.is_moderator


def create_admin_test_user(user_data):
    user = create_test_user(user_data, is_active=True, is_staff=True)
    return user


@pytest.mark.django_db
def test_create_admin_test_user(valid_user_1):
    user = create_admin_test_user(valid_user_1)
    assert user.is_active
    assert user.is_staff


def create_active_test_user(user_data):
    user = create_test_user(user_data, is_active=True)
    return user


@pytest.mark.django_db
def test_create_active_test_user(valid_user_1):
    user = create_active_test_user(valid_user_1)
    assert user.is_active
    assert not user.is_moderator


def create_test_post(user, image_file):
    current_path = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(current_path, 'images', image_file)
    post = Post(author=user)
    post.identifier = post._get_identifier()
    post.meme_file.save(image_file, File(open(image_path, 'rb')))
    post.save()
    return post


@pytest.mark.django_db
def test_create_test_post(valid_user_1, valid_image_file):
    user = create_moderator_test_user(valid_user_1)
    post = create_test_post(user, valid_image_file)
    assert post.author == user
    assert post.moderation_status == Post.WAITING_MODERATION


def create_test_denial_reason(description, moderator=None):
    reason = PostDenialReason(description=description, moderator=moderator)
    reason.save()
    return reason


@pytest.mark.django_db
def test_create_test_denial_reason(valid_denial_reason_1):
    reason = create_test_denial_reason(valid_denial_reason_1)
    assert reason.description == valid_denial_reason_1
    assert not reason.moderator


@pytest.mark.django_db
def test_create_test_denial_reason_with_moderator(valid_user_1, valid_denial_reason_1):
    user = create_moderator_test_user(valid_user_1)
    reason = create_test_denial_reason(valid_denial_reason_1, user)
    assert reason.description == valid_denial_reason_1
    assert reason.moderator == user
