import os
import pytest
from time import sleep
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
from django.utils import timezone
from pytest_django.asserts import assertTemplateUsed
from .test_utils import create_test_user


UserModel = get_user_model()


@pytest.mark.django_db
def test_render_template(client, valid_user_1):
    user = create_test_user(valid_user_1)
    client.force_login(user)
    url = reverse('posts:create-post')
    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, 'posts/create_post.html')


def get_first_user():
    return UserModel.objects.first()


def create_test_user_login(client, user_data):
    user = create_test_user(user_data)
    client.force_login(user)
    return user


def perform_create_post(client, post_data, final_url):
    url = reverse('posts:create-post')
    response = client.post(url, post_data)
    assert response.status_code == 302
    assert response.url == reverse(final_url)


@pytest.mark.django_db
def test_create_post_missing_file(client, valid_user_1):
    user = create_test_user_login(client, valid_user_1)
    perform_create_post(client, {}, 'posts:create-post')
    assert user.posts.count() == 0
    new_user = get_first_user()
    assert user == new_user
    assert new_user.count_posts_interval == 0


@pytest.mark.django_db
@pytest.mark.parametrize('image', [
    'image.TXT',
    'image.BMP'
])
def test_invalid_images(client, valid_user_1, image):
    current_path = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(current_path, 'images', image)
    user = create_test_user_login(client, valid_user_1)

    with open(image_path, 'rb') as img:
        post_data = {
            'meme_file': img
        }

        perform_create_post(client, post_data, 'posts:create-post')
        assert user.posts.count() == 0
        new_user = get_first_user()
        assert user == new_user
        assert new_user.count_posts_interval == 0


@pytest.mark.django_db
@pytest.mark.parametrize('image', [
    'image.PNG',
    'image.JPG',
    'image.JPEG',
    'long_image.jpg',
    'wide_image.jpg'
])
def test_valid_images(client, valid_user_1, image):
    current_path = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(current_path, 'images', image)
    user = create_test_user_login(client, valid_user_1)

    with open(image_path, 'rb') as img:
        post_data = {
            'meme_file': img
        }

        perform_create_post(client, post_data, 'posts:home')
        assert user.posts.count() == 1
        new_user = get_first_user()
        assert user == new_user
        assert new_user.count_posts_interval == 1
        assert default_storage.exists(user.posts.first().meme_file.name)


@pytest.mark.django_db
def test_limit_posts(client, valid_user_1, valid_image_file_1):
    current_path = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(current_path, 'images', valid_image_file_1)
    user = create_test_user_login(client, valid_user_1)
    assert not user.post_wait_until

    for count in range(1, user.max_posts_interval + 1):
        with open(image_path, 'rb') as img:
            post_data = {
                'meme_file': img
            }

            perform_create_post(client, post_data, 'posts:home')
            assert user.posts.count() == count
            new_user = get_first_user()
            assert user == new_user
            assert new_user.count_posts_interval == count

    for post in user.posts.all():
        assert default_storage.exists(post.meme_file.name)

    new_user = get_first_user()
    assert user == new_user
    assert new_user.post_wait_until > timezone.now()

    with open(image_path, 'rb') as img:
        post_data = {
            'meme_file': img
        }

        perform_create_post(client, post_data, 'posts:create-post')
        assert user.posts.count() == count
        new_user = get_first_user()
        assert user == new_user
        assert new_user.count_posts_interval == count


@pytest.mark.django_db
def test_limit_posts_expired(client, valid_user_1, valid_image_file_1):
    current_path = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(current_path, 'images', valid_image_file_1)
    user = create_test_user_login(client, valid_user_1)
    user.count_posts_interval = user.max_posts_interval
    user.post_wait_until = timezone.now() + timezone.timedelta(seconds=2)
    user.save()

    with open(image_path, 'rb') as img:
        post_data = {
            'meme_file': img
        }

        perform_create_post(client, post_data, 'posts:create-post')
        assert user.posts.count() == 0

    sleep(2)

    with open(image_path, 'rb') as img:
        post_data = {
            'meme_file': img
        }

        perform_create_post(client, post_data, 'posts:home')
        assert user.posts.count() == 1
        new_user = get_first_user()
        assert user == new_user
        assert new_user.count_posts_interval == 1
