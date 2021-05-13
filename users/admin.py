from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin, GroupAdmin as BaseGroupAdmin
from .forms import AdminRegisterForm, AdminAccountForm

User = get_user_model()


class GroupUserAdmin(admin.TabularInline):
    model = User.groups.through


class UserAdmin(BaseUserAdmin):
    search_fields = ['username', 'email', 'groups__name']
    form = AdminAccountForm
    add_form = AdminRegisterForm
    list_display = ('username', 'email', 'activated_at',
                    'group_names', 'post_count', 'banned', 'deleted')
    list_filter = ('groups',)
    fieldsets = (
        (None, {'fields': ('username', 'email',
                           'profile_pic', 'current_password', 'new_password', 'delete_requested_at', 'deleted')}),
        ('Permissions', {
            'fields': ('activated_at', 'banned', 'banned_until', 'temporary_bans', 'max_posts_interval', 'count_posts_interval', 'post_wait_until')
        }),
    )

    filter_horizontal = ()
    ordering = ('-created_at',)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password', 'activated_at'),
        }),
    )

    inlines = (GroupUserAdmin,)


class GroupAdmin(BaseGroupAdmin):
    fieldsets = (
        (None, {'fields': ('name',)}),
    )

    filter_horizontal = ()


admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)
