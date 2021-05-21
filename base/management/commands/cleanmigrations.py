import os
from django.core.management.base import BaseCommand
from django_memes.settings import BASE_DIR


def clean_migrations():
    for folder in os.scandir(BASE_DIR):
        if not folder.is_dir():
            continue

        for sub in os.scandir(folder):
            if sub.name != 'migrations':
                continue

            for file in os.scandir(sub):
                if file.is_file() and file.name != '__init__.py':
                    os.remove(file)

            break

    print('Migrations cleaned...')


class Command(BaseCommand):
    def handle(self, *args, **options):
        clean_migrations()
