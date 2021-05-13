import string
import pytest
from pytest_django.asserts import assertTemplateUsed
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from posts.models import Post
from .test_utils import (create_moderator_test_user, create_test_post, create_test_denial_reason,
                         create_active_test_user, create_admin_test_user)
from ..models import PostDenialReason, ModerationStatus, get_denial_reasons_moderator, fetch_post_moderate

UserModel = get_user_model()


@pytest.mark.django_db
def test_denial_reasons_fetch(valid_user_1, valid_user_2):
    user1 = create_moderator_test_user(valid_user_1)
    user2 = create_moderator_test_user(valid_user_2)
    letters = list(string.ascii_lowercase)

    for idx in range(len(letters)):
        if idx % 2:
            letters[idx] = letters[idx].upper()

        reason = PostDenialReason(description=letters[idx], moderator=user1)
        reason.save()

    numbers = [str(_) for _ in range(10)]

    for num in numbers:
        reason = PostDenialReason(description=num, moderator=user2)
        reason.save()

    for letter in letters:
        reason = PostDenialReason(description=letter)
        reason.save()

    reasons = get_denial_reasons_moderator(user1)
    expected_reasons = [(letter, None) for letter in letters] + \
        [(letter, user1) for letter in letters]

    for idx in range(len(reasons)):
        assert reasons[idx].description == expected_reasons[idx][0]
        assert reasons[idx].moderator == expected_reasons[idx][1]


@pytest.mark.django_db
def test_render_template(client, valid_user_1, valid_image_file):
    user = create_moderator_test_user(valid_user_1)
    post = create_test_post(user, valid_image_file)
    client.force_login(user)
    fetch_post_moderate(user)
    assert user.status_moderating.post == post
    url = reverse('moderation:moderate-deny', kwargs={'id': post.identifier})
    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, 'moderation/moderate_deny.html')


def perform_moderate_deny_post_not_fetched(client, user_data, image_file, request):
    user = create_moderator_test_user(user_data)
    post = create_test_post(user, image_file)
    client.force_login(user)
    url = reverse('moderation:moderate-deny', kwargs={'id': post.identifier})
    response = request(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_moderate_deny_post_not_fetched_get(client, valid_user_1, valid_image_file):
    perform_moderate_deny_post_not_fetched(
        client, valid_user_1, valid_image_file, client.get)


@pytest.mark.django_db
def test_moderate_deny_post_not_fetched_post(client, valid_user_1, valid_image_file):
    perform_moderate_deny_post_not_fetched(
        client, valid_user_1, valid_image_file, client.post)


def perform_moderate_post_fetched_another_user(client, user_data1, user_data2, image_file, request):
    user1 = create_moderator_test_user(user_data1)
    user2 = create_moderator_test_user(user_data2)
    post = create_test_post(user1, image_file)
    client.force_login(user1)
    fetch_post_moderate(user2)
    assert user2.status_moderating.post == post
    url = reverse('moderation:moderate-deny', kwargs={'id': post.identifier})
    response = request(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_moderate_post_fetched_another_user_get(client, valid_user_1, valid_user_2, valid_image_file):
    perform_moderate_post_fetched_another_user(
        client, valid_user_1, valid_user_2, valid_image_file, client.get)


@pytest.mark.django_db
def test_moderate_post_fetched_another_user_post(client, valid_user_1, valid_user_2, valid_image_file):
    perform_moderate_post_fetched_another_user(
        client, valid_user_1, valid_user_2, valid_image_file, client.post)


@pytest.mark.django_db
def test_denial_reason_not_informed(client, valid_user_1, valid_image_file):
    user = create_moderator_test_user(valid_user_1)
    post = create_test_post(user, valid_image_file)
    client.force_login(user)
    fetch_post_moderate(user)
    assert user.status_moderating.post == post
    url = reverse('moderation:moderate-deny', kwargs={'id': post.identifier})
    denial_data = {}
    response = client.post(url, denial_data)
    assert response.status_code == 302
    assert response.url == url


@pytest.mark.django_db
def test_denial_reason_another_user(client, valid_user_1, valid_user_2, valid_image_file, valid_denial_reason_1):
    user1 = create_moderator_test_user(valid_user_1)
    user2 = create_moderator_test_user(valid_user_2)
    post = create_test_post(user1, valid_image_file)
    reason = create_test_denial_reason(valid_denial_reason_1, user2)
    client.force_login(user1)
    fetch_post_moderate(user1)
    assert user1.status_moderating.post == post
    url = reverse('moderation:moderate-deny', kwargs={'id': post.identifier})
    denial_data = {
        'denial_reason': reason.id
    }

    response = client.post(url, denial_data)
    assert response.status_code == 302
    assert response.url == url


@pytest.mark.django_db
def test_successfully_deny_post(client, valid_user_1, valid_image_file, valid_denial_reason_1):
    user = create_moderator_test_user(valid_user_1)
    post = create_test_post(user, valid_image_file)
    reason = create_test_denial_reason(valid_denial_reason_1)
    client.force_login(user)
    fetch_post_moderate(user)
    assert user.status_moderating.post == post
    url = reverse('moderation:moderate-deny', kwargs={'id': post.identifier})
    denial_data = {
        'denial_reason': reason.id
    }

    response = client.post(url, denial_data)
    assert response.status_code == 302
    assert response.url == reverse('moderation:moderate-fetch')
    post = Post.objects.filter(id=post.id).first()
    assert post.moderation_status == Post.DENIED
    status = post.status.filter(result=ModerationStatus.DENIED).first()
    assert status.moderator_result == user


@pytest.mark.django_db
def test_deny_post_ban_user(client, valid_user_1, valid_user_2, valid_image_file, valid_denial_reason_1):
    user1 = create_moderator_test_user(valid_user_1)
    user2 = create_active_test_user(valid_user_2)
    assert not user2.banned
    assert not user2.banned_until
    assert user2.temporary_bans == 0
    email_count = user2.emails.count()
    post = create_test_post(user2, valid_image_file)
    reason = create_test_denial_reason(valid_denial_reason_1)
    client.force_login(user1)
    fetch_post_moderate(user1)
    assert user1.status_moderating.post == post
    url = reverse('moderation:moderate-deny', kwargs={'id': post.identifier})
    denial_data = {
        'denial_reason': reason.id,
        'ban_user': True
    }

    response = client.post(url, denial_data)
    assert response.status_code == 302
    assert response.url == reverse('moderation:moderate-fetch')
    user2 = UserModel.objects.filter(id=user2.id).first()
    assert user2.banned_until
    assert not user2.banned
    assert user2.temporary_bans == 1
    assert user2.emails.count() == email_count + 1


@pytest.mark.django_db
def test_deny_post_perm_ban_user(client, valid_user_1, valid_user_2, valid_image_file, valid_denial_reason_1):
    user1 = create_moderator_test_user(valid_user_1)
    user2 = create_active_test_user(valid_user_2)
    user2.temporary_bans = settings.USER_PERM_BAN_COUNT - 1
    user2.save()
    assert not user2.banned
    assert not user2.banned_until
    email_count = user2.emails.count()
    post = create_test_post(user2, valid_image_file)
    reason = create_test_denial_reason(valid_denial_reason_1)
    client.force_login(user1)
    fetch_post_moderate(user1)
    assert user1.status_moderating.post == post
    url = reverse('moderation:moderate-deny', kwargs={'id': post.identifier})
    denial_data = {
        'denial_reason': reason.id,
        'ban_user': True
    }

    response = client.post(url, denial_data)
    assert response.status_code == 302
    assert response.url == reverse('moderation:moderate-fetch')
    user2 = UserModel.objects.filter(id=user2.id).first()
    assert not user2.banned_until
    assert user2.banned
    assert user2.temporary_bans == settings.USER_PERM_BAN_COUNT
    assert user2.emails.count() == email_count + 1


@pytest.mark.django_db
def test_deny_post_ban_moderator(client, valid_user_1, valid_user_2, valid_image_file, valid_denial_reason_1):
    user1 = create_moderator_test_user(valid_user_1)
    user2 = create_moderator_test_user(valid_user_2)
    assert not user2.banned
    assert not user2.banned_until
    post = create_test_post(user2, valid_image_file)
    reason = create_test_denial_reason(valid_denial_reason_1)
    client.force_login(user1)
    fetch_post_moderate(user1)
    assert user1.status_moderating.post == post
    url = reverse('moderation:moderate-deny', kwargs={'id': post.identifier})
    denial_data = {
        'denial_reason': reason.id,
        'ban_user': True
    }

    response = client.post(url, denial_data)
    assert response.status_code == 302
    assert response.url == url
    user2 = UserModel.objects.filter(id=user2.id).first()
    assert not user2.banned_until
    assert not user2.banned


@pytest.mark.django_db
def test_deny_post_ban_admin(client, valid_user_1, valid_user_2, valid_image_file, valid_denial_reason_1):
    user1 = create_moderator_test_user(valid_user_1)
    user2 = create_admin_test_user(valid_user_2)
    assert not user2.banned
    assert not user2.banned_until
    post = create_test_post(user2, valid_image_file)
    reason = create_test_denial_reason(valid_denial_reason_1)
    client.force_login(user1)
    fetch_post_moderate(user1)
    assert user1.status_moderating.post == post
    url = reverse('moderation:moderate-deny', kwargs={'id': post.identifier})
    denial_data = {
        'denial_reason': reason.id,
        'ban_user': True
    }

    response = client.post(url, denial_data)
    assert response.status_code == 302
    assert response.url == url
    user2 = UserModel.objects.filter(id=user2.id).first()
    assert not user2.banned_until
    assert not user2.banned
