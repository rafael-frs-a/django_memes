from itsdangerous import URLSafeTimedSerializer
from django.conf import settings

url_timed_serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
