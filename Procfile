web: gunicorn django_memes.wsgi --preload
worker: celery -A django_memes worker -l INFO
