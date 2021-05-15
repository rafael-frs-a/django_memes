import os
from django.core.wsgi import get_wsgi_application
from .dotenv_loader import load_dotenv

load_dotenv()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_memes.settings')
application = get_wsgi_application()
