from django.contrib import admin
from .models import Email


class EmailAdmin(admin.ModelAdmin):
    search_fields = ['subject', 'recipient__email', 'recipient__username']
    list_display = ('recipient', 'recipients', 'subject', 'sent')

    class Meta:
        model = Email


admin.site.register(Email, EmailAdmin)
