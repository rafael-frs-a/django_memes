import pytest
from django.urls import reverse
from .test_utils import create_active_test_user


@pytest.mark.django_db
@pytest.mark.parametrize('view', [
    ('moderation:home', {}),
    ('moderation:denial-reason-list', {}),
    ('moderation:denial-reason-delete', {'id': 0}),
    ('moderation:denial-reason-create', {}),
    ('moderation:denial-reason-edit', {'id': 0}),
    ('moderation:moderate-start', {}),
    ('moderation:moderate-fetch', {}),
    ('moderation:moderate-stop', {}),
    ('moderation:moderate-post', {'id': 0}),
    ('moderation:moderate-approve', {'id': 0}),
    ('moderation:moderate-deny', {'id': 0}),
])
def test_successful_login_required_request(client, view, valid_user_1):
    user = create_active_test_user(valid_user_1)
    client.force_login(user)
    url = reverse(view[0], kwargs=view[1])
    response = client.get(url, follow=True)
    assert response.status_code == 403


@pytest.mark.django_db
@pytest.mark.parametrize('view', [
    ('moderation:home', {}),
    ('moderation:denial-reason-list', {}),
    ('moderation:denial-reason-delete', {'id': 0}),
    ('moderation:denial-reason-create', {}),
    ('moderation:denial-reason-edit', {'id': 0}),
    ('moderation:moderate-start', {}),
    ('moderation:moderate-fetch', {}),
    ('moderation:moderate-stop', {}),
    ('moderation:moderate-post', {'id': 0}),
    ('moderation:moderate-approve', {'id': 0}),
    ('moderation:moderate-deny', {'id': 0}),
])
def test_failed_login_required_request(client, view):
    url = reverse(view[0], kwargs=view[1])
    final_url = reverse('users:login') + '?next=' + url
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == final_url
