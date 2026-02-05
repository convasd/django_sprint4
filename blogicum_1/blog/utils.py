"""Дополнительные функции."""
from blog.models import Post
from django.utils import timezone


def get_published_posts(category_slug=None):
    """Метод получения опубликованных постов."""
    posts = Post.objects.select_related('category').filter(
        pub_date__lt=timezone.now(),
        is_published=True,
        category__is_published=True
    )
    if category_slug:
        posts = posts.filter(category__slug=category_slug)
    return posts
