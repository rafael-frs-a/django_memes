release: python3 manage.py migrate
web: gunicorn django_memes.wsgi --preload
worker: celery -A django_memes worker -l INFO
