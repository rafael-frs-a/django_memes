import pytest
from time import sleep
from pytest_django.asserts import assertTemplateUsed
from django.urls import reverse
from django.utils import timezone
from posts.models import Post
from ..models import ModerationStatus, fetch_post_moderate
from .test_utils import create_moderator_test_user, create_active_test_user, create_test_post


@pytest.mark.django_db
def test_render_template(client, valid_user_1):
    user = create_moderator_test_user(valid_user_1)
    client.force_login(user)
    url = reverse('moderation:moderate-fetch')
    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, 'moderation/moderate_fetch.html')


@pytest.mark.django_db
def test_redirect_post_left_moderating(client, valid_user_1, valid_image_file):
    user = create_moderator_test_user(valid_user_1)
    post = create_test_post(user, valid_image_file)
    client.force_login(user)
    fetch_post_moderate(user)
    assert user.status_moderating.post == post
    assert user.status_moderating.result == ModerationStatus.MODERATING
    assert user.status_moderating.moderator_result == user
    url = reverse('moderation:moderate-fetch')
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == reverse(
        'moderation:moderate-post', kwargs={'id': post.identifier})


@pytest.mark.django_db
def test_redirect_moderate_post(client, valid_user_1, valid_image_file):
    user = create_moderator_test_user(valid_user_1)
    post = create_test_post(user, valid_image_file)
    client.force_login(user)
    url = reverse('moderation:moderate-fetch')
    response = client.get(url)
    assert user.status_moderating.post == post
    assert user.status_moderating.result == ModerationStatus.MODERATING
    assert user.status_moderating.moderator_result == user
    assert response.status_code == 302
    assert response.url == reverse(
        'moderation:moderate-post', kwargs={'id': post.identifier})


@pytest.mark.django_db
def test_non_moderator_fetch_post(client, valid_user_1, valid_image_file):
    user = create_active_test_user(valid_user_1)
    create_test_post(user, valid_image_file)
    post = fetch_post_moderate(user)
    assert post is None


@pytest.mark.django_db
def test_moderator_fetch_post(client, valid_user_1, valid_image_file):
    user = create_moderator_test_user(valid_user_1)
    post = create_test_post(user, valid_image_file)
    post_moderating = fetch_post_moderate(user)
    assert post_moderating == post


@pytest.mark.django_db
def test_remove_moderating_user_not_moderator(client, valid_user_1, valid_image_file):
    user = create_moderator_test_user(valid_user_1)
    post = create_test_post(user, valid_image_file)
    post_moderating = fetch_post_moderate(user)
    assert post_moderating == post
    assert post_moderating.moderation_status == Post.MODERATING
    user.groups.clear()
    assert not user.is_moderator
    assert ModerationStatus.objects.count() == 0
    post = Post.objects.filter(id=post.id).first()
    assert post.moderation_status == Post.WAITING_MODERATION


@pytest.mark.django_db
def test_remove_moderating_user_deleted(client, valid_user_1, valid_user_2, valid_image_file):
    user1 = create_moderator_test_user(valid_user_1)
    user2 = create_active_test_user(valid_user_2)
    post = create_test_post(user2, valid_image_file)
    post_moderating = fetch_post_moderate(user1)
    assert post_moderating == post
    assert post_moderating.moderation_status == Post.MODERATING
    user1.delete()
    assert ModerationStatus.objects.count() == 0
    post = Post.objects.filter(id=post.id).first()
    assert post.moderation_status == Post.WAITING_MODERATION


@pytest.mark.django_db
def test_fetch_post_banned_user(client, valid_user_1, valid_user_2, valid_image_file):
    user1 = create_moderator_test_user(valid_user_1)
    user2 = create_active_test_user(valid_user_2)
    create_test_post(user2, valid_image_file)
    user2.banned = True
    user2.save()
    post_moderating = fetch_post_moderate(user1)
    assert not post_moderating


@pytest.mark.django_db
def test_fecth_post_banned_until_user(client, valid_user_1, valid_user_2, valid_image_file):
    user1 = create_moderator_test_user(valid_user_1)
    user2 = create_active_test_user(valid_user_2)
    create_test_post(user2, valid_image_file)
    user2.banned_until = timezone.now() + timezone.timedelta(minutes=1)
    user2.save()
    post_moderating = fetch_post_moderate(user1)
    assert not post_moderating


@pytest.mark.django_db
def test_fetch_post_banned_until_user_expired(client, valid_user_1, valid_user_2, valid_image_file):
    user1 = create_moderator_test_user(valid_user_1)
    user2 = create_active_test_user(valid_user_2)
    post = create_test_post(user2, valid_image_file)
    user2.banned_until = timezone.now() + timezone.timedelta(seconds=1)
    user2.save()
    sleep(1)
    post_moderating = fetch_post_moderate(user1)
    assert post_moderating == post
