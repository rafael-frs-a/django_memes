from django.shortcuts import redirect
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    View, TemplateView, RedirectView, ListView, CreateView, UpdateView, DeleteView, DetailView)
from base.views import PrgView
from posts.models import Post
from .decorators import moderator_required
from .forms import DenyPostForm
from .models import (PostDenialReason, ModerationStatus, get_reasons_moderator,
                     get_total_reasons_moderator, get_denial_reason, get_post_moderating,
                     check_post_moderating, fetch_post_moderate, stop_moderating, approve_post)


@method_decorator(moderator_required, 'dispatch')
class ModerationView(View):
    ...


class Home(ModerationView, RedirectView):
    pattern_name = 'moderation:denial-reason-list'
    http_method_names = ['get']


class ReasonsListView(ModerationView, ListView):
    model = PostDenialReason
    template_name = 'moderation/denial_reason_list.html'
    http_method_names = ['get']
    context_object_name = 'reasons'
    ordering = ['-created_at']
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Moderation'
        context['reasons_total'] = get_total_reasons_moderator(
            self.request.user)
        return context

    def get_queryset(self):
        return get_reasons_moderator(
            self.request.user, self.request.GET.get('sort', '-created_at'))


class ReasonDeleveView(ModerationView, DeleteView):
    template_name = 'moderation/denial_reason_delete.html'
    http_method_names = ['get', 'post']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Delete Denial Reason'
        return context

    def get_object(self):
        id_ = self.kwargs.get('id')
        return get_denial_reason(self.request.user, id_)

    def get_success_url(self):
        messages.success(self.request, 'Denial reason deleted.')
        return reverse('moderation:denial-reason-list')


class ReasonCreateView(ModerationView, PrgView, CreateView):
    model = PostDenialReason
    fields = ['description']
    template_name = 'moderation/denial_reason_create.html'
    http_method_names = ['get', 'post']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Denial Reason'
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.instance.moderator = self.request.user
        return form

    def get_success_url(self):
        messages.success(self.request, 'Post denial reason created.')
        return reverse('moderation:denial-reason-list')


class ReasonUpdateView(ModerationView, PrgView, UpdateView):
    model = PostDenialReason
    fields = ['description']
    template_name = 'moderation/denial_reason_create.html'
    http_method_names = ['get', 'post']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Denial Reason'
        return context

    def get_object(self):
        id_ = self.kwargs.get('id')
        return get_denial_reason(self.request.user, id_)

    def get_success_url(self):
        messages.success(self.request, 'Changes saved.')
        return reverse('moderation:denial-reason-list')


class ModerateStartView(ModerationView, TemplateView):
    template_name = 'moderation/moderate_start.html'
    http_method_names = ['get']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Moderate'
        return context

    def get(self, request, *args, **kwargs):
        post = get_post_moderating(request.user)

        if post:
            return redirect('moderation:moderate-post', id=post.identifier)

        return super().get(request, *args, **kwargs)


class ModerateFetchView(ModerationView, TemplateView):
    template_name = 'moderation/moderate_fetch.html'
    http_method_names = ['get']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Moderate'
        return context

    def get(self, request, *args, **kwargs):
        post = fetch_post_moderate(request.user)

        if post:
            return redirect('moderation:moderate-post', id=post.identifier)

        return super().get(request, *args, **kwargs)


class ModeratePostView(ModerationView, DetailView):
    model = Post
    template_name = 'moderation/moderate_post.html'
    http_method_names = ['get']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Moderate'
        return context

    def get_object(self):
        identifier = self.kwargs.get('id')
        return check_post_moderating(self.request.user, identifier)


class StopModerateView(ModerationView, RedirectView):
    pattern_name = 'moderation:moderate-start'
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        stop_moderating(request.user)
        return super().get(request, *args, **kwargs)


class ModerateApproveView(ModerationView, RedirectView):
    pattern_name = 'moderation:moderate-fetch'
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        identifier = self.kwargs.get('id')
        approve_post(request.user, identifier)
        return super().get(request, *args)


class ModerateDenyView(ModerationView, PrgView, CreateView):
    model = ModerationStatus
    form_class = DenyPostForm
    template_name = 'moderation/moderate_deny.html'
    http_method_names = ['get', 'post']
    success_url = reverse_lazy('moderation:moderate-fetch')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Moderate'
        post = get_post_moderating(self.request.user)
        context['author_moderator_or_admin'] = post and (
            post.author.is_moderator or post.author.is_staff)
        return context

    def get(self, request, *args, **kwargs):
        identifier = self.kwargs.get('id')
        check_post_moderating(request.user, identifier)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        identifier = self.kwargs.get('id')
        check_post_moderating(request.user, identifier)
        return super().post(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['post'] = get_post_moderating(self.request.user)
        return kwargs
