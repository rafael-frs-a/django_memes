import json
import pytest
from urllib.parse import urlencode
from django.conf import settings
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from pytest_django.asserts import assertTemplateUsed
from moderation.models import ModerationStatus, fetch_post_moderate
from moderation.tests.test_utils import create_moderator_test_user, create_test_denial_reason
from .test_utils import create_test_user, create_test_post
from ..models import Post


@pytest.mark.django_db
def test_render_template(client, valid_user_1):
    user = create_test_user(valid_user_1)
    client.force_login(user)
    url = reverse('posts:user-posts')
    response = client.get(url)
    assertTemplateUsed(response, 'posts/user_posts.html')


def check_response_data(client, page, client_timezone, posts, has_next):
    params = {
        'page': page,
        'timezone': client_timezone
    }

    url = reverse('posts:user-posts')
    querystring = urlencode(params)
    response = client.get(f'{url}?{querystring}')
    assert response.status_code == 200
    assert type(response) == JsonResponse
    response_data = json.loads(response.content.decode('utf-8'))
    assert response_data['has_next'] == has_next
    assert response_data['posts'] == posts


@pytest.mark.django_db
def test_get_user_posts(client, valid_user_1, valid_user_2, valid_image_file_1):
    user1 = create_test_user(valid_user_1)
    user2 = create_moderator_test_user(valid_user_2)
    client.force_login(user1)
    client_timezone = 180
    posts = []
    post = create_test_post(user1, valid_image_file_1)
    fetch_post_moderate(user2)
    created_at = (post.created_at - timezone.timedelta(minutes=180)
                  ).strftime(settings.DATE_TIME_DISPLAY_FORMAT)
    status_created_at = post.status.first().created_at
    status_created_at = (
        status_created_at - timezone.timedelta(minutes=client_timezone)).strftime(settings.DATE_TIME_DISPLAY_FORMAT)
    post_data = {
        'meme_url': post.meme_file.url,
        'post_created_at': created_at,
        'is_waiting_moderation': False,
        'is_moderating': True,
        'is_denied': False,
        'is_approved': False,
        'status_created_at': status_created_at,
        'denial_reason': '',
        'denial_details': ''
    }

    posts.insert(0, post_data)
    post = create_test_post(user1, valid_image_file_1)
    created_at = (post.created_at - timezone.timedelta(minutes=client_timezone)
                  ).strftime(settings.DATE_TIME_DISPLAY_FORMAT)
    post_data = {
        'meme_url': post.meme_file.url,
        'post_created_at': created_at,
        'is_waiting_moderation': True,
        'is_moderating': False,
        'is_denied': False,
        'is_approved': False,
        'status_created_at': '',
        'denial_reason': '',
        'denial_details': ''
    }

    posts.insert(0, post_data)
    reason = create_test_denial_reason('test denial reason', user2)
    post = create_test_post(user1, valid_image_file_1)
    created_at = (post.created_at - timezone.timedelta(minutes=client_timezone)
                  ).strftime(settings.DATE_TIME_DISPLAY_FORMAT)
    status = ModerationStatus(post=post, result=ModerationStatus.DENIED, moderator_result=user2,
                              denial_reason=reason, denial_detail='test denial details')
    status.save()
    status_created_at = (status.created_at - timezone.timedelta(minutes=client_timezone)
                         ).strftime(settings.DATE_TIME_DISPLAY_FORMAT)
    post_data = {
        'meme_url': post.meme_file.url,
        'post_created_at': created_at,
        'is_waiting_moderation': False,
        'is_moderating': False,
        'is_denied': True,
        'is_approved': False,
        'status_created_at': status_created_at,
        'denial_reason': status.denial_reason.description,
        'denial_details': status.denial_detail
    }

    posts.insert(0, post_data)
    post = create_test_post(user1, valid_image_file_1)
    created_at = (post.created_at - timezone.timedelta(minutes=client_timezone)
                  ).strftime(settings.DATE_TIME_DISPLAY_FORMAT)
    status = ModerationStatus(
        post=post, result=ModerationStatus.APPROVED, moderator_result=user2)
    status.save()
    post = Post.objects.filter(id=post.id).first()
    status_created_at = (post.approved_at - timezone.timedelta(minutes=client_timezone)
                         ).strftime(settings.DATE_TIME_DISPLAY_FORMAT)
    post_data = {
        'meme_url': post.meme_file.url,
        'post_created_at': created_at,
        'is_waiting_moderation': False,
        'is_moderating': False,
        'is_denied': False,
        'is_approved': True,
        'status_created_at': status_created_at,
        'denial_reason': '',
        'denial_details': ''
    }

    posts.insert(0, post_data)
    create_test_post(user2, valid_image_file_1)
    settings.POSTS_PER_PAGE = 1
    check_response_data(client, 1, client_timezone, [posts[0]], True)
    check_response_data(client, 2, client_timezone, [posts[1]], True)
    check_response_data(client, 3, client_timezone, [posts[2]], True)
    check_response_data(client, 4, client_timezone, [posts[3]], False)
    check_response_data(client, 5, client_timezone, [], False)
