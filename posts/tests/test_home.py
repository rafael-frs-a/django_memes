import json
import pytest
from urllib.parse import urlencode
from django.conf import settings
from django.http import JsonResponse
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed
from moderation.models import ModerationStatus, fetch_post_moderate
from moderation.tests.test_utils import create_moderator_test_user, create_test_denial_reason
from .test_utils import create_test_user, create_test_post
from ..models import PostTag


def test_render_template(client):
    url = reverse('posts:home')
    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, 'posts/home.html')


def check_response_data(client, page, posts, has_next, search=''):
    params = {
        'page': page,
        'search': search
    }

    url = reverse('posts:home')
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
def test_get_posts(client, valid_user_1, valid_user_2, valid_image_file_1):
    user1 = create_test_user(valid_user_1)
    user2 = create_moderator_test_user(valid_user_2)
    posts = []
    post = create_test_post(user1, valid_image_file_1)
    fetch_post_moderate(user2)
    create_test_post(user1, valid_image_file_1)
    post = create_test_post(user1, valid_image_file_1)
    reason = create_test_denial_reason('test denial reason', user2)
    status = ModerationStatus(
        post=post, result=ModerationStatus.DENIED, moderator_result=user2, denial_reason=reason)
    status.save()
    post = create_test_post(user1, valid_image_file_1)
    status = ModerationStatus(
        post=post, result=ModerationStatus.APPROVED, moderator_result=user2)
    status.save()
    post.meme_text = 'user1 post text'
    post.save()
    post_tag = PostTag(post=post, description='user1 post label')
    post_tag.save()
    post_data = get_post_data(post)
    posts.insert(0, post_data)
    create_test_post(user2, valid_image_file_1)
    post = create_test_post(user2, valid_image_file_1)
    status = ModerationStatus(
        post=post, result=ModerationStatus.APPROVED, moderator_result=user2)
    status.save()
    post.meme_text = 'user2 post text'
    post.save()
    post_tag = PostTag(post=post, description='user2 post label')
    post_tag.save()
    post_data = get_post_data(post)
    posts.insert(0, post_data)
    settings.POSTS_PER_PAGE = 1
    check_response_data(client, 1, [posts[0]], True)
    check_response_data(client, 2, [posts[1]], False)
    check_response_data(client, 3, [], False)
    check_response_data(
        client, 1, [posts[0]], False, f'User2 Label {user2.username.lower()}')
    check_response_data(
        client, 1, [posts[1]], False, f'User1 Label {user1.username.lower()}')
    check_response_data(
        client, 1, [posts[0]], False, f'User2 Text {user2.username.lower()}')
    check_response_data(
        client, 1, [posts[1]], False, f'User1 Text {user1.username.lower()}')
