import os
from django.core.asgi import get_asgi_application
from .dotenv_loader import load_dotenv

load_dotenv()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_memes.settings')
application = get_asgi_application()
