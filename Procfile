release: python manage.py migrate
web: gunicorn django_memes.wsgi
worker: celery -A django_memes worker -l INFO
