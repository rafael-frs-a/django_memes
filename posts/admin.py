from django.contrib import admin
from .models import Post, PostTag


class PostTagAdmin(admin.TabularInline):
    model = PostTag


class PostAdmin(admin.ModelAdmin):
    search_fields = ['author__username', 'moderation_status']
    fieldsets = (
        (None, {'fields': ('author', 'meme_file', 'approved_at',
                           'moderation_status', 'meme_text', 'meme_labelled')}),
    )

    inlines = (PostTagAdmin,)

    class Meta:
        model = Post

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)

        for option in Post.MODERATION_STATUS:
            if search_term.lower() == option[1].lower():
                queryset |= self.model.objects.filter(
                    moderation_status=option[0])
                break

        return queryset, use_distinct


admin.site.register(Post, PostAdmin)
