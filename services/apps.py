from django.apps import AppConfig


class ServicesConfig(AppConfig):
    name = 'services'

    def ready(self):
        from .user_deleter import start_user_deleter
        start_user_deleter()
