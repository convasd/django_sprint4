from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse, reverse_lazy


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class CommentRedirectMixin:

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'pk': self.kwargs['post_id']})


class ProfileRedirectMixin:

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})
