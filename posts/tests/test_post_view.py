import pytest
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed
from moderation.models import ModerationStatus
from moderation.tests.test_utils import create_moderator_test_user
from .test_utils import create_test_post


def perform_failed_view_post(client, post_id):
    url = reverse('posts:post-view', kwargs={'id': post_id})
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_view_non_existent_post(client):
    perform_failed_view_post(client, 'id')


@pytest.mark.django_db
def test_successful_view_approved_post(client, valid_user_1, valid_image_file_1):
    user = create_moderator_test_user(valid_user_1)
    post = create_test_post(user, valid_image_file_1)
    status = ModerationStatus(
        post=post, result=ModerationStatus.APPROVED, moderator_result=user)
    status.save()
    url = reverse('posts:post-view', kwargs={'id': post.identifier})
    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, 'posts/post_detail.html')


@pytest.mark.django_db
def test_view_post_not_approved(client, valid_user_1, valid_image_file_1):
    user = create_moderator_test_user(valid_user_1)
    post = create_test_post(user, valid_image_file_1)
    perform_failed_view_post(client, post.identifier)
