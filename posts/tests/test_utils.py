import os
import pytest
from django.core.files import File
from django.core.files.storage import default_storage
from users.tests.test_utils import create_activated_test_user
from ..models import Post


def create_test_user(user_data):
    return create_activated_test_user(user_data)


@pytest.mark.django_db
def test_get_test_user(valid_user_1):
    user = create_test_user(valid_user_1)
    assert user.username == valid_user_1['username']
    assert user.email == valid_user_1['email']
    assert user.check_password(valid_user_1['password'])
    assert user.posts.count() == 0


def create_test_post(user, image_file):
    current_path = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(current_path, 'images', image_file)
    post = Post(author=user)
    post.identifier = post._get_identifier()
    post.meme_file.save(image_file, File(open(image_path, 'rb')))
    post.save()
    return post


@pytest.mark.django_db
def test_create_test_post(valid_user_1, valid_image_file_1):
    user = create_test_user(valid_user_1)
    post = create_test_post(user, valid_image_file_1)
    assert post.author == user
    assert default_storage.exists(post.meme_file.name)
