import pytest
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize('view', [
    ('users:register', {}, 200, 200, 405, 405, 405),
    ('users:login', {}, 200, 200, 405, 405, 405),
    ('users:logout', {}, 200, 200, 405, 405, 405),
    ('users:activate-account', {'token': 'token'}, 200, 200, 405, 405, 405),
    ('users:reset-password', {}, 200, 200, 405, 405, 405),
    ('users:reset-password-token',
     {'token': 'token'}, 200, 200, 405, 405, 405),
    ('users:account', {}, 200, 200, 405, 405, 405),
    ('users:change-email', {'current_email_token': 'token',
                            'new_email_token': 'token'}, 200, 200, 405, 405, 405),
    ('users:delete-account', {}, 200, 200, 405, 405, 405),
    ('users:cancel-delete-account', {}, 200, 200, 405, 405, 405),
    ('users:cancel-delete-account-token',
     {'token': 'token'}, 200, 200, 405, 405, 405),
])
def test_requests(client, view):
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
