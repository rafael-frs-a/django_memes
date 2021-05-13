import json
import pytest
from urllib.parse import urlencode
from django.conf import settings
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from pytest_django.asserts import assertTemplateUsed
from base.utils import inverse_case
from moderation.models import ModerationStatus
from moderation.tests.test_utils import create_moderator_test_user
from .test_utils import create_test_user, create_test_post
from ..models import PostTag


@pytest.mark.django_db
def test_render_template(client, valid_user_1):
    user = create_test_user(valid_user_1)
    url = reverse('posts:author-posts', kwargs={'username': user.username})
    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, 'posts/home.html')


def perform_failed_author_posts(client, username):
    url = reverse('posts:author-posts', kwargs={'username': username})
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_non_existent_author(client):
    perform_failed_author_posts(client, 'user')


@pytest.mark.django_db
def test_non_activated_author(client, valid_user_1):
    user = create_test_user(valid_user_1)
    user.activated_at = None
    user.save()
    assert not user.is_active
    perform_failed_author_posts(client, user.username)


@pytest.mark.django_db
def test_banned_author(client, valid_user_1):
    user = create_test_user(valid_user_1)
    user.banned = True
    user.save()
    perform_failed_author_posts(client, user.username)


@pytest.mark.django_db
def test_temporarily_banned_author(client, valid_user_1):
    user = create_test_user(valid_user_1)
    user.banned_until = timezone.now() + timezone.timedelta(minutes=2)
    user.save()
    perform_failed_author_posts(client, user.username)


@pytest.mark.django_db
def test_deleted_author(client, valid_user_1):
    user = create_test_user(valid_user_1)
    user.deleted = True
    user.save()
    perform_failed_author_posts(client, user.username)


def check_response_data(client, username, page, posts, has_next, search=''):
    params = {
        'page': page,
        'search': search
    }

    url = reverse('posts:author-posts',
                  kwargs={'username': inverse_case(username)})
    querystring = urlencode(params)
    response = client.get(f'{url}?{querystring}')
    assert response.status_code == 200
    assert type(response) == JsonResponse
    response_data = json.loads(response.content.decode('utf-8'))
    assert response_data['has_next'] == has_next
    assert response_data['posts'] == posts


def get_post_data(post):
    return {
        'profile_pic_url': post.author.profile_pic.url,
        'author': post.author.username,
        'meme_url': post.meme_file.url,
        'post_link': reverse('posts:post-view', kwargs={'id': post.identifier}),
        'author_link': reverse('posts:author-posts', kwargs={'username': post.author.username}),
        'tags': [_.description for _ in post.tags.order_by('description')]
    }


@pytest.mark.django_db
def test_successful_author_posts(client, valid_user_1, valid_user_2, valid_image_file_1):
    user1 = create_test_user(valid_user_1)
    user2 = create_moderator_test_user(valid_user_2)
    create_test_post(user1, valid_image_file_1)
    post = create_test_post(user1, valid_image_file_1)
    status = ModerationStatus(
        post=post, result=ModerationStatus.APPROVED, moderator_result=user2)
    status.save()
    post.meme_text = 'user1 post text'
    post.save()
    post_tag = PostTag(post=post, description='user1 post label')
    post_tag.save()
    post_data = get_post_data(post)
    posts = [post_data]
    create_test_post(user2, valid_image_file_1)
    post = create_test_post(user2, valid_image_file_1)
    status = ModerationStatus(
        post=post, result=ModerationStatus.APPROVED, moderator_result=user2)
    status.save()
    post.meme_text = 'user2 post text'
    post.save()
    post_tag = PostTag(post=post, description='user2 post label')
    post_tag.save()
    settings.POSTS_PER_PAGE = 1
    check_response_data(client, user1.username, 1, [posts[0]], False)
    check_response_data(client, user1.username, 2, [], False)
    post_data = get_post_data(post)
    posts = [post_data]
    check_response_data(client, user2.username, 1, [posts[0]], False)
    check_response_data(client, user2.username, 2, [], False)
    check_response_data(client, user2.username, 1, [
                        posts[0]], False, user2.username.lower())
    check_response_data(client, user2.username, 1, [],
                        False, user1.username.lower())
    check_response_data(client, user2.username, 1, [
                        posts[0]], False, 'User2 Text')
    check_response_data(client, user2.username, 1, [], False, 'User1 Text')
    check_response_data(client, user2.username, 1, [
                        posts[0]], False, 'User2 Label')
    check_response_data(client, user2.username, 1, [], False, 'User1 Label')
