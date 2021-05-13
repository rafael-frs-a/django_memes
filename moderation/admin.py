from django.contrib import admin
from .models import PostDenialReason, ModerationStatus


class PostDenialReasonAdmin(admin.ModelAdmin):
    search_fields = ['description', 'moderator__username']

    class Meta:
        model = PostDenialReason


class ModerationStatusAdmin(admin.ModelAdmin):
    search_fields = ['post__author__username', 'result']

    class Meta:
        model = ModerationStatus

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)

        for option in ModerationStatus.RESULTS:
            if search_term.lower() == option[1].lower():
                queryset |= self.model.objects.filter(result=option[0])
                break

        return queryset, use_distinct


admin.site.register(PostDenialReason, PostDenialReasonAdmin)
admin.site.register(ModerationStatus, ModerationStatusAdmin)
