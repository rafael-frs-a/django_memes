import os
import shutil
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand

UserModel = get_user_model()


def clean_media():
    folders, files = default_storage.listdir(settings.MEDIA_ROOT)

    for folder in folders:
        path = os.path.join(settings.MEDIA_ROOT, folder)
        shutil.rmtree(path)

    for file in files:
        if file.lower() == UserModel.DEFAULT_PROFILE_PIC.lower():
            continue

        path = os.path.join(settings.MEDIA_ROOT, file)
        default_storage.delete(file)

    print('Media files deleted...')


class Command(BaseCommand):
    def handle(self, *args, **options):
        if not settings.DEBUG:
            print('Project not in debug mode...')
            return

        clean_media()
