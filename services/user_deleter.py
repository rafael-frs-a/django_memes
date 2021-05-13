from time import time
from threading import Thread, Event
from django.utils import timezone
from users.models import (get_not_activated_users_expired_links, get_users_execute_delete_request,
                          execute_user_delete_request)

user_deleter = Event()


def delete_not_activated_users_expired_links():
    print(f'{timezone.now()}: Checking for not activated users with expired links...')
    users = get_not_activated_users_expired_links()
    count = 0

    for user in users:
        try:
            user.delete()
            count += 1
        except:
            pass

    if len(users) > 0:
        print(f'{count}/{len(users)} users deleted...')


def delete_users_delete_request():
    print(f'{timezone.now()}: Checking for users with expired delete requests...')
    users = get_users_execute_delete_request()
    count = 0

    for user in users:
        try:
            execute_user_delete_request(user)
            count += 1
        except:
            pass

    if len(users) > 0:
        print(f'{count}/{len(users)} users with delete request executed...')


def __delete_users():
    INTERVAL = 5 * 60  # 5 minutes

    while True:
        start = time()
        delete_not_activated_users_expired_links()
        delete_users_delete_request()
        duration = time() - start

        if duration < INTERVAL:
            user_deleter.clear()
            user_deleter.wait(INTERVAL - duration)


def start_user_deleter():
    Thread(name='Check users to delete',
           target=__delete_users, daemon=True).start()
