from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, DetailView
from base.views import PrgView
from .models import Post, get_user_posts, get_approved_posts, get_approved_post, get_author
from .forms import CreatePostForm


class HomeView(TemplateView):
    template_name = 'posts/home.html'
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        if 'page' in request.GET:
            data = get_approved_posts(request.GET.get(
                'page'), request.GET.get('search', ''))
            return JsonResponse(data)

        return super().get(request, *args, **kwargs)


class AuthorPostsView(DetailView):
    model = get_user_model()
    template_name = 'posts/home.html'
    http_method_names = ['get']
    context_object_name = 'author'

    def get_object(self):
        username = self.kwargs.get('username')
        return get_author(username)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.username
        return context

    def get(self, request, *args, **kwargs):
        if 'page' in request.GET:
            author = self.get_object()
            data = get_approved_posts(request.GET.get(
                'page'), request.GET.get('search', ''), author)
            return JsonResponse(data)

        return super().get(request, *args, **kwargs)


class CreatePostView(LoginRequiredMixin, PrgView, CreateView):
    model = Post
    form_class = CreatePostForm
    template_name = 'posts/create_post.html'
    http_method_names = ['get', 'post']
    success_url = reverse_lazy('posts:home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Post Meme'
        return context

    def get_success_url(self):
        messages.success(
            self.request, 'Meme posted. Waiting for moderation to approve it.')
        return super().get_success_url()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class UserPostsView(LoginRequiredMixin, TemplateView):
    template_name = 'posts/user_posts.html'
    http_method_names = ['get']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'My Memes'
        return context

    def get(self, request, *args, **kwargs):
        if 'page' in request.GET:
            data = get_user_posts(request.user, request.GET.get(
                'page'), request.GET.get('timezone', 0))
            return JsonResponse(data)

        return super().get(request, *args, **kwargs)


class PostView(DetailView):
    model = Post
    template_name = 'posts/post_detail.html'
    http_method_names = ['get']

    def get_object(self):
        identifier = self.kwargs.get('id')
        return get_approved_post(identifier)
