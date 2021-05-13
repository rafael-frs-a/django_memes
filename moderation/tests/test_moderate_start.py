import pytest
from pytest_django.asserts import assertTemplateUsed
from django.urls import reverse
from ..models import fetch_post_moderate
from .test_utils import create_moderator_test_user, create_test_post


@pytest.mark.django_db
def test_render_template(client, valid_user_1):
    user = create_moderator_test_user(valid_user_1)
    client.force_login(user)
    url = reverse('moderation:moderate-start')
    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, 'moderation/moderate_start.html')


@pytest.mark.django_db
def test_redirect_post_left_moderating(client, valid_user_1, valid_image_file):
    user = create_moderator_test_user(valid_user_1)
    post = create_test_post(user, valid_image_file)
    client.force_login(user)
    fetch_post_moderate(user)
    assert user.status_moderating.post == post
    url = reverse('moderation:moderate-start')
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == reverse(
        'moderation:moderate-post', kwargs={'id': post.identifier})
