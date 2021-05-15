release: python manage.py migrate
heroku buildpacks: set https://github.com/buyersight/heroku-google-application-credentials-buildpack.git -a django_memes
web: gunicorn django_memes.wsgi
worker: celery -A django_memes worker -l INFO
