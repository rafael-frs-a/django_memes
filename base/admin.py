from django.contrib import admin
from django.conf import settings

admin.site.site_header = f'{settings.APP_NAME} - Admin'
