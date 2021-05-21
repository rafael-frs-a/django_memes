import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from posts.models import Post
from ..models import ModerationStatus, fetch_post_moderate
from .test_utils import create_moderator_test_user, create_test_post

UserModel = get_user_model()


@pytest.mark.django_db
def test_successful_approve_post(client, valid_user_1, valid_image_file):
    user = create_moderator_test_user(valid_user_1)
    max_posts_interval = user.max_posts_interval
    post = create_test_post(user, valid_image_file)
    client.force_login(user)
    fetch_post_moderate(user)
    assert user.status_moderating.post == post
    url = reverse('moderation:moderate-approve',
                  kwargs={'id': post.identifier})
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == reverse('moderation:moderate-fetch')
    post = Post.objects.filter(id=post.id).first()
    assert post.moderation_status == Post.APPROVED
    assert post.approved_at
    status = post.status.filter(result=ModerationStatus.APPROVED).first()
    assert status.moderator_result == user
    user = UserModel.objects.filter(id=user.id).first()
    assert user.max_posts_interval == max_posts_interval + 1

    with pytest.raises(ModerationStatus.DoesNotExist):
        user.status_moderating


@pytest.mark.django_db
def test_approve_post_not_moderating(client, valid_user_1, valid_image_file):
    user = create_moderator_test_user(valid_user_1)
    post = create_test_post(user, valid_image_file)
    client.force_login(user)
    url = reverse('moderation:moderate-approve',
                  kwargs={'id': post.identifier})
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_approve_post_another_user_moderating(client, valid_user_1, valid_user_2, valid_image_file):
    user1 = create_moderator_test_user(valid_user_1)
    user2 = create_moderator_test_user(valid_user_2)
    post = create_test_post(user1, valid_image_file)
    client.force_login(user1)
    fetch_post_moderate(user2)
    assert user2.status_moderating.post == post
    url = reverse('moderation:moderate-approve',
                  kwargs={'id': post.identifier})
    response = client.get(url)
    assert response.status_code == 404
