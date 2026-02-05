from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .forms import CommentForm, PostForm, ProfileUpdateForm
from .models import Category, Comment, Post
from .utils import get_published_posts

User = get_user_model()


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class PostListView(ListView):

    model = Post
    template_name = 'blog/index.html'
    paginate_by = 10

    def get_queryset(self):
        queryset = get_published_posts().order_by('-pub_date')
        queryset = queryset.annotate(comment_count=Count('comment'))
        return queryset


class PostDetailView(UserPassesTestMixin, DetailView):

    model = Post
    template_name = 'blog/detail.html'

    def test_func(self):
        post = self.get_object()
        if post.author == self.request.user:
            return True
        return get_object_or_404(get_published_posts(), id=post.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comment.select_related('author')
        return context


class PostCreateView (LoginRequiredMixin, CreateView):

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(OnlyAuthorMixin, UpdateView):

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def handle_no_permission(self):
        """Метод перенаправления при отказе в доступе."""
        post_id = self.kwargs.get('pk')
        return redirect(reverse_lazy('blog:post_detail',
                                     kwargs={'pk': post_id}))

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.object.pk})


class PostDeleteView(OnlyAuthorMixin, DeleteView):

    model = Post
    success_url = reverse_lazy('blog:index')

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.delete(request, self.object)
        return redirect(self.success_url)


class ProfileDetailView(DetailView):

    model = User
    template_name = 'blog/profile.html'
    paginate_by = 10

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = Post.objects.filter(author=self.object).order_by('-pub_date')
        posts = posts.annotate(comment_count=Count('comment'))
        paginator = Paginator(posts, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        context['profile'] = self.object
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):

    model = User
    form_class = ProfileUpdateForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse('blog:profile', args=[self.object.username])


class CommentCreateView(LoginRequiredMixin, CreateView):

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'pk': self.kwargs['post_id']})


class CommentUpdateView(OnlyAuthorMixin, UpdateView):

    model = Comment
    template_name = 'blog/comment.html'
    form_class = CommentForm
    success_url = reverse_lazy('blog:post_detail')

    def get_object(self, queryset=None):
        comment_id = self.kwargs.get('comment_id')
        return get_object_or_404(Comment, id=comment_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_id'] = self.kwargs.get('post_id')
        return context

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'pk': self.kwargs['post_id']})


class CommentDeleteView(OnlyAuthorMixin, DeleteView):

    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'pk': self.kwargs['post_id']})


class CategoryPostsView(DetailView):

    model = Category
    template_name = 'blog/category.html'
    paginate_by = 10

    def get_object(self, queryset=None):
        category = get_object_or_404(Category,
                                     slug=self.kwargs['category_slug'])
        if not category.is_published:
            raise Http404("Категория не опубликована")
        return category

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = get_published_posts(self.object.slug).order_by('-pub_date')
        paginator = Paginator(posts, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        return context
