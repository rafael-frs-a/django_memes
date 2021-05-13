import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from ..models import ModerationStatus, fetch_post_moderate
from .test_utils import create_moderator_test_user, create_test_post


UserModel = get_user_model()


@pytest.mark.django_db
def test_moderate_stop_no_post(client, valid_user_1):
    user = create_moderator_test_user(valid_user_1)
    client.force_login(user)
    url = reverse('moderation:moderate-stop')
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == reverse('moderation:moderate-start')


@pytest.mark.django_db
def test_moderate_stop_with_post(client, valid_user_1, valid_image_file):
    user = create_moderator_test_user(valid_user_1)
    post = create_test_post(user, valid_image_file)
    client.force_login(user)
    fetch_post_moderate(user)
    assert user.status_moderating.post == post
    url = reverse('moderation:moderate-stop')
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == reverse('moderation:moderate-start')
    user = UserModel.objects.filter(id=user.id).first()

    with pytest.raises(ModerationStatus.DoesNotExist):
        user.status_moderating
