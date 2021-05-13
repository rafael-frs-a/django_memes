import pytest
from django.urls import reverse
from .test_utils import create_moderator_test_user


@pytest.mark.django_db
@pytest.mark.parametrize('view', [
    ('moderation:home', {}, 200, 405, 405, 405, 405),
    ('moderation:denial-reason-list', {}, 200, 405, 405, 405, 405),
    ('moderation:denial-reason-delete', {'id': 0}, 404, 404, 405, 405, 405),
    ('moderation:denial-reason-create', {}, 200, 200, 405, 405, 405),
    ('moderation:denial-reason-edit', {'id': 0}, 404, 404, 405, 405, 405),
    ('moderation:moderate-start', {}, 200, 405, 405, 405, 405),
    ('moderation:moderate-fetch', {}, 200, 405, 405, 405, 405),
    ('moderation:moderate-stop', {}, 200, 405, 405, 405, 405),
    ('moderation:moderate-post', {'id': 0}, 404, 405, 405, 405, 405),
    ('moderation:moderate-approve', {'id': 0}, 404, 405, 405, 405, 405),
    ('moderation:moderate-deny', {'id': 0}, 404, 404, 405, 405, 405),
])
def test_requests(client, view, valid_user_1):
    user = create_moderator_test_user(valid_user_1)
    client.force_login(user)
    url = reverse(view[0], kwargs=view[1])
    response = client.get(url, follow=True)
    assert response.status_code == view[2]
    response = client.post(url, follow=True)
    assert response.status_code == view[3]
    response = client.delete(url, follow=True)
    assert response.status_code == view[4]
    response = client.put(url, follow=True)
    assert response.status_code == view[5]
    response = client.patch(url, follow=True)
    assert response.status_code == view[6]
