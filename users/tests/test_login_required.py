import pytest
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize('view', [
    ('users:account', {}),
    ('users:logout', {}),
    ('users:change-email',
     {'current_email_token': 'token', 'new_email_token': 'token'}),
    ('posts:create-post', {}),
    ('posts:user-posts', {}),
    ('users:delete-account', {}),
    ('users:cancel-delete-account', {}),
])
def test_failed_login_required_request(client, view):
    url = reverse(view[0], kwargs=view[1])
    final_url = reverse('users:login') + '?next=' + url
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == final_url
    response = client.post(url)
    assert response.status_code == 302
    assert response.url == final_url
